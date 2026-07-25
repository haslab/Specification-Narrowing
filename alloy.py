"""Parsing and bounded translation support for the Alloy narrowing scripts.

The original version of this module used ``ANY: /[^{}]+/`` to skip over most
of the Alloy language.  That happened to work for the small, static benchmark
models, but it could not distinguish declaration structure from expressions
and could not process Alloy 6 temporal syntax.

This module now has a small lexer and a structure-aware parser.  Relational
expressions remain source text (the Alloy Analyzer is still the authority for
their syntax and typing), while formula-level Boolean and future-time
operators are parsed into an AST for the Alloy 6 -> Alloy 5 BMC translation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable, Optional


TEMPORAL_UNARY = {"after", "always", "eventually"}
TEMPORAL_BINARY = {"until", "releases"}
UNSUPPORTED_TEMPORAL = {"before", "historically", "once", "since", "triggered", ";"}
BOOLEAN_UNARY = {"not", "!"}
BOOLEAN_BINARY = {
    "iff": "iff",
    "<=>": "iff",
    "implies": "implies",
    "=>": "implies",
    "or": "or",
    "||": "or",
    "and": "and",
    "&&": "and",
}

_GENERATED_NAMES = {
    "State",
    "__SNFirst",
    "__sn_step",
    "__sn_loop",
}


class AlloyParseError(ValueError):
    """Raised for malformed or currently unsupported Alloy input."""


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int


def _lex(source: str) -> list[Token]:
    """Tokenize Alloy while retaining source offsets.

    Comments and whitespace are discarded.  Offsets let atomic relational
    expressions be reproduced verbatim apart from identifier substitutions.
    """

    tokens: list[Token] = []
    i = 0
    multi = ("<=>", "!in", "=>", "->", "++", "<:", ":>", "<=", ">=", "!=", "=<", "&&", "||")
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        if source.startswith("//", i) or source.startswith("--", i):
            newline = source.find("\n", i + 2)
            i = len(source) if newline < 0 else newline + 1
            continue
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            if end < 0:
                raise AlloyParseError("unterminated block comment")
            i = end + 2
            continue
        operator = next((op for op in multi if source.startswith(op, i)), None)
        if operator is not None:
            tokens.append(Token(operator, i, i + len(operator)))
            i += len(operator)
            continue
        if source[i].isalpha() or source[i] in "_$":
            end = i + 1
            while end < len(source) and (source[end].isalnum() or source[end] in "_$/'?"):
                end += 1
            tokens.append(Token(source[i:end], i, end))
            i = end
            continue
        if source[i].isdigit():
            end = i + 1
            while end < len(source) and source[end].isdigit():
                end += 1
            tokens.append(Token(source[i:end], i, end))
            i = end
            continue
        tokens.append(Token(source[i], i, i + 1))
        i += 1
    return tokens


def _matching(tokens: list[Token], start: int, opening: str, closing: str) -> int:
    depth = 0
    for i in range(start, len(tokens)):
        if tokens[i].text == opening:
            depth += 1
        elif tokens[i].text == closing:
            depth -= 1
            if depth == 0:
                return i
    raise AlloyParseError(f"unmatched {opening!r}")


def _split_top_level(tokens: list[Token], separator: str) -> list[list[Token]]:
    result: list[list[Token]] = []
    start = 0
    depths = {"(": 0, "[": 0, "{": 0}
    closing = {")": "(", "]": "[", "}": "{"}
    for i, token in enumerate(tokens):
        if token.text in depths:
            depths[token.text] += 1
        elif token.text in closing:
            depths[closing[token.text]] -= 1
        elif token.text == separator and not any(depths.values()):
            result.append(tokens[start:i])
            start = i + 1
    result.append(tokens[start:])
    return result


def _source_for(source: str, tokens: list[Token]) -> str:
    if not tokens:
        return ""
    return source[tokens[0].start:tokens[-1].end]


@dataclass
class SignatureDecl:
    names: list[str]
    parent: Optional[str]
    relation: Optional[str]
    multiplicity: Optional[str]
    abstract: bool
    variable: bool
    fields: list["FieldDecl"] = field(default_factory=list)


@dataclass
class FieldDecl:
    owner: str
    name: str
    type_expr: str
    variable: bool


@dataclass
class FormulaNode:
    kind: str
    value: str = ""
    left: Optional["FormulaNode"] = None
    right: Optional["FormulaNode"] = None
    source: str = ""


class FormulaParser:
    """Parse the Boolean/temporal skeleton around Alloy relational atoms."""

    def __init__(self, source: str):
        self.source = source
        self.tokens = _lex(source)

    def parse(self) -> FormulaNode:
        if not self.tokens:
            return FormulaNode("atom", source="true")
        return self._parse(0, len(self.tokens))

    def _depths(self, lo: int, hi: int) -> Iterable[tuple[int, Token, int]]:
        depth = 0
        for i in range(lo, hi):
            token = self.tokens[i]
            yield i, token, depth
            if token.text in ("(", "[", "{"):
                depth += 1
            elif token.text in (")", "]", "}"):
                depth -= 1

    def _encloses(self, lo: int, hi: int) -> bool:
        opening = self.tokens[lo].text
        pairs = {"(": ")", "{": "}"}
        if opening not in pairs or self.tokens[hi - 1].text != pairs[opening]:
            return False
        depth = 0
        for i in range(lo, hi):
            text = self.tokens[i].text
            if text == opening:
                depth += 1
            elif text == pairs[opening]:
                depth -= 1
                if depth == 0:
                    return i == hi - 1
        return False

    def _top_level(self, lo: int, hi: int, operators: set[str]) -> list[int]:
        result = []
        depth = 0
        for i in range(lo, hi):
            text = self.tokens[i].text
            if text in ("(", "[", "{"):
                depth += 1
            elif text in (")", "]", "}"):
                depth -= 1
            elif depth == 0 and text in operators:
                result.append(i)
        return result

    def _parse(self, lo: int, hi: int) -> FormulaNode:
        while hi - lo >= 2 and self._encloses(lo, hi):
            lo += 1
            hi -= 1
        if lo >= hi:
            return FormulaNode("atom", source="true")

        first = self.tokens[lo].text
        if first in {"all", "some", "one", "lone", "no", "let"}:
            bars = self._top_level(lo + 1, hi, {"|"})
            if bars:
                bar = bars[0]
                declaration = self.source[self.tokens[lo + 1].start:self.tokens[bar - 1].end]
                return FormulaNode(
                    "binder",
                    value=f"{first} {declaration}",
                    left=self._parse(bar + 1, hi),
                )

        # Ordered from weakest to strongest binding.  Right-associative
        # operators use their first occurrence; associative ones use the last.
        precedence = [
            {"iff", "<=>"},
            {"implies", "=>"},
            {"or", "||"},
            {"and", "&&"},
            TEMPORAL_BINARY,
        ]
        for operators in precedence:
            positions = self._top_level(lo, hi, operators)
            if positions:
                index = positions[0] if operators & {"implies", "=>"} else positions[-1]
                op = BOOLEAN_BINARY.get(self.tokens[index].text, self.tokens[index].text)
                return FormulaNode(op, left=self._parse(lo, index), right=self._parse(index + 1, hi))

        if first in BOOLEAN_UNARY | TEMPORAL_UNARY:
            op = "not" if first in BOOLEAN_UNARY else first
            return FormulaNode(op, left=self._parse(lo + 1, hi))

        return FormulaNode(
            "atom",
            source=self.source[self.tokens[lo].start:self.tokens[hi - 1].end],
        )


def _contains_temporal(node: FormulaNode) -> bool:
    if node.kind in TEMPORAL_UNARY | TEMPORAL_BINARY:
        return True
    return bool(
        (node.left is not None and _contains_temporal(node.left))
        or (node.right is not None and _contains_temporal(node.right))
    )


def _needs_temporal_translation(
    source: str,
    mutable_global: set[str],
    mutable_local: set[str],
) -> bool:
    """Whether a formula must be made explicitly state-dependent."""

    mutable = mutable_global | mutable_local
    for token in _lex(source):
        if token.text in TEMPORAL_UNARY | TEMPORAL_BINARY:
            return True
        base = token.text.rstrip("'")
        if base in mutable:
            return True
    return False


def _nnf(node: FormulaNode, negated: bool = False) -> FormulaNode:
    """Convert the parsed formula to negation-normal form before BMC."""

    if node.kind == "not":
        return _nnf(node.left, not negated)
    if node.kind == "implies":
        expanded = FormulaNode("or", left=FormulaNode("not", left=node.left), right=node.right)
        return _nnf(expanded, negated)
    if node.kind == "iff":
        same = FormulaNode(
            "or",
            left=FormulaNode("and", left=node.left, right=node.right),
            right=FormulaNode(
                "and",
                left=FormulaNode("not", left=node.left),
                right=FormulaNode("not", left=node.right),
            ),
        )
        return _nnf(same, negated)
    if node.kind in {"and", "or"}:
        kind = ({"and": "or", "or": "and"}[node.kind] if negated else node.kind)
        return FormulaNode(kind, left=_nnf(node.left, negated), right=_nnf(node.right, negated))
    if node.kind in {"always", "eventually"}:
        kind = ({"always": "eventually", "eventually": "always"}[node.kind] if negated else node.kind)
        return FormulaNode(kind, left=_nnf(node.left, negated))
    if node.kind in {"until", "releases"}:
        kind = ({"until": "releases", "releases": "until"}[node.kind] if negated else node.kind)
        return FormulaNode(kind, left=_nnf(node.left, negated), right=_nnf(node.right, negated))
    if node.kind == "after":
        # LTL's next operator is self-dual because every encoded trace has a
        # mandatory back-loop and therefore denotes an infinite execution.
        child = _nnf(node.left, negated)
        return FormulaNode("after", left=child)
    if node.kind == "binder":
        keyword, declaration = node.value.split(" ", 1)
        if negated and keyword in {"all", "some"}:
            keyword = "some" if keyword == "all" else "all"
            return FormulaNode("binder", value=f"{keyword} {declaration}", left=_nnf(node.left, True))
        if negated:
            return FormulaNode("not", left=FormulaNode("binder", value=node.value, left=_nnf(node.left)))
        return FormulaNode("binder", value=node.value, left=_nnf(node.left))
    if negated:
        return FormulaNode("neg_atom", source=node.source)
    return node


def _bound_names(keyword: str, declaration: str) -> set[str]:
    tokens = _lex(declaration)
    if keyword == "let":
        names = set()
        for part in _split_top_level(tokens, ","):
            equals = next((i for i, token in enumerate(part) if token.text == "="), None)
            if equals is not None:
                names.update(
                    token.text
                    for token in part[:equals]
                    if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$/'?]*", token.text)
                )
        return names

    # Quantified declarations may share a type (``p,q: P``).  An identifier
    # belongs to the declaration's left side until its first top-level colon.
    colon = next((i for i, token in enumerate(tokens) if token.text == ":"), len(tokens))
    return {
        token.text
        for token in tokens[:colon]
        if re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$/'?]*", token.text)
        and token.text not in {"disj", "one", "lone", "some", "set"}
    }


class TemporalRenderer:
    def __init__(self, mutable_global: set[str], mutable_local: set[str]):
        self.mutable_global = mutable_global
        self.mutable_local = mutable_local
        self.counter = 0

    @staticmethod
    def successor() -> str:
        return "(__sn_step + __sn_loop)"

    def fresh(self) -> str:
        self.counter += 1
        return f"__sn_t{self.counter}"

    def _rewrite_atom(self, source: str, state: str, bound: set[str]) -> str:
        tokens = _lex(source)
        if not tokens:
            return source
        replacements: list[tuple[int, int, str]] = []
        max_prime = 0
        for token in tokens:
            raw = token.text
            base = raw.rstrip("'")
            primes = len(raw) - len(base)
            if base in bound:
                continue
            if base not in self.mutable_global and base not in self.mutable_local:
                continue
            max_prime = max(max_prime, primes)
            at = state
            for _ in range(primes):
                at = f"({at}).{self.successor()}"
            if base in self.mutable_global:
                replacement = f"({at}).{base}"
            else:
                replacement = f"{base}.({at})"
            replacements.append((token.start, token.end, replacement))

        rendered = source
        for start, end, replacement in reversed(replacements):
            rendered = rendered[:start] + replacement + rendered[end:]

        if max_prime:
            guard_state = state
            guards = []
            for _ in range(max_prime):
                guards.append(f"some ({guard_state}).{self.successor()}")
                guard_state = f"({guard_state}).{self.successor()}"
            rendered = f"({' and '.join(guards)} and ({rendered}))"
        return rendered

    def render(self, node: FormulaNode, state: str, bound: Optional[set[str]] = None) -> str:
        bound = set() if bound is None else bound
        if node.kind in {"atom", "neg_atom"}:
            atom = self._rewrite_atom(node.source, state, bound)
            return f"not ({atom})" if node.kind == "neg_atom" else f"({atom})"
        if node.kind in {"and", "or"}:
            return f"({self.render(node.left, state, bound)} {node.kind} {self.render(node.right, state, bound)})"
        if node.kind == "not":
            return f"not ({self.render(node.left, state, bound)})"
        if node.kind == "binder":
            keyword, declaration = node.value.split(" ", 1)
            rewritten = self._rewrite_atom(declaration, state, bound)
            nested_bound = bound | _bound_names(keyword, declaration)
            return f"({keyword} {rewritten} | {self.render(node.left, state, nested_bound)})"
        if node.kind == "after":
            following = f"({state}).{self.successor()}"
            return f"(some {following} and {self.render(node.left, following, bound)})"
        if node.kind == "always":
            time = self.fresh()
            return (
                f"(some __sn_loop and all {time}: ({state}).*{self.successor()} | "
                f"{self.render(node.left, time, bound)})"
            )
        if node.kind == "eventually":
            time = self.fresh()
            return (
                f"(some {time}: ({state}).*{self.successor()} | "
                f"{self.render(node.left, time, bound)})"
            )
        if node.kind in {"until", "releases"}:
            witness = self.fresh()
            prefix = self.fresh()
            reachable = f"({state}).*{self.successor()}"
            before = f"({reachable} & ^{self.successor()}.{witness})"
            if node.kind == "until":
                return (
                    f"(some {witness}: {reachable} | {self.render(node.right, witness, bound)} and "
                    f"all {prefix}: {before} | {self.render(node.left, prefix, bound)})"
                )
            through = f"({reachable} & *{self.successor()}.{witness})"
            globally = self.render(FormulaNode("always", left=node.right), state, bound)
            return (
                f"({globally} or some {witness}: {reachable} | "
                f"{self.render(node.left, witness, bound)} and "
                f"all {prefix}: {through} | {self.render(node.right, prefix, bound)})"
            )
        raise AlloyParseError(f"unsupported formula node {node.kind!r}")


class Collector:
    def __init__(self):
        self.predicates: dict[str, str] = {}
        self.signatures: set[str] = set()
        self.subsets: dict[str, str] = {}
        self.toplevel: set[str] = set()
        self.fields: dict[str, str] = {}
        self.extensions: dict[str, set[str]] = {}
        self.multiplicities: dict[str, str] = {}
        self.abstract: set[str] = set()
        self.facts: dict[str, str] = {}
        self.content = ""
        self.temporal = False
        self.trace_length: Optional[int] = None
        self.original: Optional["Collector"] = None
        self.mutable_global: set[str] = set()
        self.mutable_local: set[str] = set()
        self._signature_decls: list[SignatureDecl] = []
        self._field_decls: list[FieldDecl] = []
        self._fact_sources: list[tuple[str, str]] = []
        self._predicate_sources: list[tuple[str, str]] = []

    def _add_signature(self, decl: SignatureDecl) -> None:
        self._signature_decls.append(decl)
        for name in decl.names:
            self.signatures.add(name)
            if decl.parent is None:
                self.toplevel.add(name)
            else:
                self.subsets[name] = decl.parent
                if decl.relation == "extends":
                    self.extensions.setdefault(decl.parent, set()).add(name)
            if decl.multiplicity:
                self.multiplicities[name] = decl.multiplicity
            if decl.abstract:
                self.abstract.add(name)
        for field_decl in decl.fields:
            self._add_field(field_decl)

    def _add_field(self, decl: FieldDecl) -> None:
        if decl.name in self.fields:
            raise AlloyParseError(f"duplicate or ambiguous field name {decl.name!r}")
        self._field_decls.append(decl)
        self.fields[decl.name] = f"{decl.owner} -> {decl.type_expr.strip()}"


class ModelParser:
    def __init__(self, content: str):
        self.content = content
        self.tokens = _lex(content)
        self.collector = Collector()

    def parse(self) -> Collector:
        i = 0
        while i < len(self.tokens):
            start = i
            while i < len(self.tokens) and self.tokens[i].text in {"abstract", "var", "one", "lone", "some", "private"}:
                i += 1
            if i < len(self.tokens) and self.tokens[i].text == "sig":
                i = self._signature(start, i)
                continue
            i = start
            if self.tokens[i].text == "fact":
                i = self._formula_paragraph(i, "fact")
                continue
            if self.tokens[i].text == "pred":
                i = self._formula_paragraph(i, "pred")
                continue
            i += 1
        if not self.collector._signature_decls:
            raise AlloyParseError("no signature declarations found")
        return self.collector

    def _signature(self, start: int, sig_index: int) -> int:
        qualifiers = {token.text for token in self.tokens[start:sig_index]}
        open_index = next((i for i in range(sig_index + 1, len(self.tokens)) if self.tokens[i].text == "{"), None)
        if open_index is None:
            raise AlloyParseError("signature has no body")
        close_index = _matching(self.tokens, open_index, "{", "}")
        header = self.tokens[sig_index + 1:open_index]
        relation_index = next((i for i, token in enumerate(header) if token.text in {"extends", "in"}), None)
        name_tokens = header if relation_index is None else header[:relation_index]
        names = [token.text for token in name_tokens if re.match(r"[A-Za-z_$]", token.text)]
        if not names:
            raise AlloyParseError("signature has no name")
        relation = None if relation_index is None else header[relation_index].text
        parent = None
        if relation_index is not None:
            parents = [token.text for token in header[relation_index + 1:] if re.match(r"[A-Za-z_$]", token.text)]
            if len(parents) != 1:
                raise AlloyParseError("only a single named parent is currently supported")
            parent = parents[0]

        fields = self._fields(names, self.tokens[open_index + 1:close_index])
        decl = SignatureDecl(
            names=names,
            parent=parent,
            relation=relation,
            multiplicity=next((q for q in ("one", "lone", "some") if q in qualifiers), None),
            abstract="abstract" in qualifiers,
            variable="var" in qualifiers,
            fields=fields,
        )
        self.collector._add_signature(decl)
        return close_index + 1

    def _fields(self, owners: list[str], tokens: list[Token]) -> list[FieldDecl]:
        if not tokens:
            return []
        fields: list[FieldDecl] = []
        start = 0
        while start < len(tokens):
            while start < len(tokens) and tokens[start].text == ",":
                start += 1
            if start >= len(tokens):
                break
            colon = next((i for i in range(start, len(tokens)) if tokens[i].text == ":"), None)
            if colon is None:
                raise AlloyParseError("signature facts and malformed field declarations are not supported")
            end = colon + 1
            depth = 0
            while end < len(tokens):
                text = tokens[end].text
                if text in ("(", "[", "{"):
                    depth += 1
                elif text in (")", "]", "}"):
                    depth -= 1
                elif text == "," and depth == 0:
                    break
                end += 1
            name_tokens = tokens[start:colon]
            variable = any(token.text == "var" for token in name_tokens)
            names = [
                token.text for token in name_tokens
                if re.match(r"[A-Za-z_$]", token.text) and token.text not in {"var", "disj", "private"}
            ]
            type_expr = _source_for(self.content, tokens[colon + 1:end]).strip()
            if not names or not type_expr:
                raise AlloyParseError("malformed field declaration")
            if len(owners) != 1:
                raise AlloyParseError("fields on a multi-name signature declaration are ambiguous")
            for name in names:
                fields.append(FieldDecl(owners[0], name, type_expr, variable))
            start = end + 1
        return fields

    def _formula_paragraph(self, start: int, kind: str) -> int:
        i = start + 1
        name = ""
        if i < len(self.tokens) and re.match(r"[A-Za-z_$]", self.tokens[i].text) and self.tokens[i].text != "{":
            name = self.tokens[i].text
            i += 1
        if kind == "pred" and i < len(self.tokens) and self.tokens[i].text == "[":
            end_params = _matching(self.tokens, i, "[", "]")
            if end_params != i + 1:
                raise AlloyParseError("parameterized predicates are not yet supported as alternatives")
            i = end_params + 1
        while i < len(self.tokens) and self.tokens[i].text != "{":
            i += 1
        if i >= len(self.tokens):
            raise AlloyParseError(f"{kind} has no body")
        close = _matching(self.tokens, i, "{", "}")
        body = self.content[self.tokens[i].end:self.tokens[close].start]
        if kind == "fact":
            name = name or f"__anonymous_fact_{len(self.collector._fact_sources) + 1}"
            self.collector._fact_sources.append((name, body))
            self.collector.facts[name] = body
        else:
            if not name:
                raise AlloyParseError("predicate has no name")
            self.collector._predicate_sources.append((name, body))
            self.collector.predicates[name] = body
        return close + 1


def _render_signature(decl: SignatureDecl) -> str:
    qualifiers = []
    if decl.abstract:
        qualifiers.append("abstract")
    if decl.multiplicity:
        qualifiers.append(decl.multiplicity)
    prefix = (" ".join(qualifiers) + " ") if qualifiers else ""
    parent = f" {decl.relation} {decl.parent}" if decl.parent else ""
    lines = []
    for field_decl in decl.fields:
        lines.append(f"    {field_decl.name}: {field_decl.type_expr}")
    body = ",\n".join(lines)
    return f"{prefix}sig {', '.join(decl.names)}{parent} {{\n{body}\n}}"


def _compile_temporal(collector: Collector, trace_length: int) -> Collector:
    if trace_length < 1:
        raise AlloyParseError("maximum trace length must be at least 1")
    declared = set(collector.signatures) | set(collector.fields)
    collisions = declared & _GENERATED_NAMES
    if collisions:
        raise AlloyParseError(f"model uses reserved temporal-encoding names: {', '.join(sorted(collisions))}")

    original_signatures = list(collector._signature_decls)
    original_fields = list(collector._field_decls)
    mutable_sigs = [decl for decl in original_signatures if decl.variable]
    unsupported = [
        decl
        for decl in mutable_sigs
        if decl.relation != "in" or decl.abstract or decl.fields
    ]
    if unsupported:
        names = ", ".join(name for decl in unsupported for name in decl.names)
        raise AlloyParseError(
            "only fieldless mutable subset signatures declared with 'in' are currently "
            f"supported ({names})"
        )
    mutable_global: set[str] = set()
    state_fields = [
        FieldDecl("State", "__sn_step", "lone State", False),
        FieldDecl("State", "__sn_loop", "lone State", False),
    ]
    for decl in mutable_sigs:
        multiplicity = decl.multiplicity or "set"
        for name in decl.names:
            mutable_global.add(name)
            state_fields.append(FieldDecl("State", name, f"{multiplicity} {decl.parent}", False))

    mutable_local = {decl.name for decl in original_fields if decl.variable}
    static_signatures: list[SignatureDecl] = []
    for decl in original_signatures:
        if decl.variable:
            continue
        static_fields = []
        for field_decl in decl.fields:
            if field_decl.variable:
                # Local-state idiom: the last column identifies the state.
                # Leading field multiplicities are enforced pointwise below.
                type_without_mult = re.sub(
                    r"^(one|lone|some|set)\s+", "", field_decl.type_expr.strip()
                )
                static_fields.append(
                    FieldDecl(
                        field_decl.owner,
                        field_decl.name,
                        f"{type_without_mult} -> State",
                        False,
                    )
                )
            else:
                static_fields.append(field_decl)
        static_signatures.append(
            SignatureDecl(
                names=decl.names,
                parent=decl.parent,
                relation=decl.relation,
                multiplicity=decl.multiplicity,
                abstract=decl.abstract,
                variable=False,
                fields=static_fields,
            )
        )

    state_decl = SignatureDecl(["State"], None, None, None, False, False, state_fields)
    first_decl = SignatureDecl(["__SNFirst"], "State", "in", "one", False, False, [])

    compiled = Collector()
    compiled.temporal = True
    compiled.trace_length = trace_length
    compiled.original = collector
    compiled.mutable_global = mutable_global
    compiled.mutable_local = mutable_local
    for decl in static_signatures + [state_decl, first_decl]:
        compiled._add_signature(decl)

    trace_fact = (
        f"#State <= {trace_length}\n"
        "no iden & ^__sn_step\n"
        "State = __SNFirst.*__sn_step\n"
        "one State - __sn_step.State\n"
        "one __sn_loop\n"
        "__sn_loop in (State - __sn_step.State) -> State"
    )
    compiled.facts["__SNTrace"] = trace_fact
    compiled._fact_sources.append(("__SNTrace", trace_fact))

    # Restore a mutable field's leading multiplicity independently at every
    # owner/state pair after adding the explicit State column.
    for field_decl in original_fields:
        if not field_decl.variable:
            continue
        match = re.match(r"^(one|lone|some)\s+", field_decl.type_expr.strip())
        if match:
            multiplicity = match.group(1)
            fact_name = f"__SNMultiplicity_{field_decl.name}"
            formula = (
                f"all __sn_owner: {field_decl.owner}, __sn_state: State | "
                f"{multiplicity} __sn_owner.{field_decl.name}.__sn_state"
            )
            compiled.facts[fact_name] = formula
            compiled._fact_sources.append((fact_name, formula))

    renderer = TemporalRenderer(mutable_global, mutable_local)
    for name, body in collector._fact_sources:
        if _needs_temporal_translation(body, mutable_global, mutable_local):
            tree = _nnf(FormulaParser(body).parse())
            formula = renderer.render(tree, "__SNFirst")
        else:
            formula = body.strip()
        compiled.facts[name] = formula
        compiled._fact_sources.append((name, formula))
    for name, body in collector._predicate_sources:
        if _needs_temporal_translation(body, mutable_global, mutable_local):
            tree = _nnf(FormulaParser(body).parse())
            formula = renderer.render(tree, "__SNFirst")
        else:
            formula = body.strip()
        compiled.predicates[name] = formula
        compiled._predicate_sources.append((name, formula))

    paragraphs = [_render_signature(decl) for decl in compiled._signature_decls]
    paragraphs.extend(f"fact {name} {{\n{body}\n}}" for name, body in compiled._fact_sources)
    paragraphs.extend(f"pred {name} {{\n{body}\n}}" for name, body in compiled._predicate_sources)
    compiled.content = "\n\n".join(paragraphs) + "\n"
    return compiled


def parse(content: str, trace_length: Optional[int] = None) -> Collector:
    """Parse an Alloy model and, when needed, compile Alloy 6 temporal syntax.

    ``trace_length`` is the maximum number of states in a bounded trace.
    Static models do not require it; temporal models do.
    """

    collector = ModelParser(content).parse()
    formula_sources = [body for _, body in collector._fact_sources + collector._predicate_sources]
    unsupported = {
        token.text
        for body in formula_sources
        for token in _lex(body)
        if token.text in UNSUPPORTED_TEMPORAL
    }
    if unsupported:
        raise AlloyParseError(
            "past-time and sequential temporal operators are not yet supported by the "
            f"Alloy 5 translation ({', '.join(sorted(unsupported))})"
        )
    temporal_formula = any(_contains_temporal(FormulaParser(body).parse()) for body in formula_sources)
    temporal_declaration = any(decl.variable for decl in collector._signature_decls) or any(
        decl.variable for decl in collector._field_decls
    )
    if temporal_formula or temporal_declaration:
        if trace_length is None:
            raise AlloyParseError("trace_length is required for an Alloy 6 temporal model")
        return _compile_temporal(collector, trace_length)
    collector.content = content
    return collector


def requires_trace_length(content: str) -> bool:
    """Return whether a model uses mutable or temporal Alloy 6 syntax."""

    temporal_tokens = TEMPORAL_UNARY | TEMPORAL_BINARY | UNSUPPORTED_TEMPORAL | {"var"}
    return any(token.text in temporal_tokens or token.text.endswith("'") for token in _lex(content))


def int_bitwidth(max_cardinality: int) -> int:
    """Smallest signed Alloy bitwidth that represents ``max_cardinality``."""

    if max_cardinality < 0:
        raise ValueError("maximum cardinality cannot be negative")
    return max(2, max_cardinality.bit_length() + 1)


def command_scope(collector: Collector, structural_scope: int) -> str:
    """Build an Alloy 5 scope that keeps structure and trace bounds separate."""

    if collector.temporal:
        bitwidth = max(structural_scope, int_bitwidth(collector.trace_length))
        return (
            f"for {structural_scope} but {bitwidth} Int, "
            f"{collector.trace_length} State"
        )
    return f"for {structural_scope}"


@dataclass(frozen=True)
class Instance:
    """A solver constraint plus data used by textual and graphical views."""

    alloy5: str
    alloy6_body: Optional[str] = None
    trace_length: Optional[int] = None
    relations: Optional[dict[str, tuple[tuple[str, ...], ...]]] = None

    def __str__(self) -> str:
        # Narrowing queries are submitted to AlloyMax/Alloy 5.
        return self.alloy5


def _atom_text(
    atom: object,
    alloy6: bool = False,
    labels: Optional[dict[str, str]] = None,
) -> str:
    if labels is not None and str(atom) in labels:
        return labels[str(atom)]
    text = str(atom).replace("$", "")
    return f"_{text}" if alloy6 else text


def _relation_formula(
    name: str,
    tuples: list[list[object]],
    alloy6: bool = False,
    labels: Optional[dict[str, str]] = None,
) -> str:
    if not tuples:
        return f"no {name}"
    rendered = ["->".join(_atom_text(atom, alloy6, labels) for atom in tuple_) for tuple_ in tuples]
    return f"{name} = " + " + ".join(rendered)


def _alloy6_instance(collector: Collector, value: dict[str, list[list[object]]]) -> tuple[str, int]:
    original = collector.original
    if original is None:
        raise AlloyParseError("temporal collector has no original model metadata")

    state_atoms = {str(tuple_[0]) for tuple_ in value["State"]}
    first_values = value["__SNFirst"]
    if len(first_values) != 1:
        raise AlloyParseError("encoded trace does not have exactly one initial state")
    first = str(first_values[0][0])
    step = {str(tuple_[0]): str(tuple_[1]) for tuple_ in value["__sn_step"]}
    loop_values = value["__sn_loop"]
    if len(loop_values) != 1:
        raise AlloyParseError("encoded trace does not have exactly one back-loop")
    loop_source, loop_target = map(str, loop_values[0])

    states = [first]
    while states[-1] in step:
        following = step[states[-1]]
        if following in states:
            raise AlloyParseError("linear trace prefix contains a cycle")
        states.append(following)
    if set(states) != state_atoms or loop_source != states[-1] or loop_target not in state_atoms:
        raise AlloyParseError("malformed bounded-lasso instance")
    loop_index = states.index(loop_target)

    static_signature_names = {
        name
        for decl in original._signature_decls
        if not decl.variable
        for name in decl.names
    }
    static_field_names = {decl.name for decl in original._field_decls if not decl.variable}
    static_toplevel = {
        name
        for decl in original._signature_decls
        if not decl.variable and decl.parent is None
        for name in decl.names
    }
    atoms = {
        str(tuple_[0])
        for name in static_toplevel
        for tuple_ in value.get(name, [])
    }

    # AlloyMax's optimal meta-model calls every carrier atom ``Atom``.  Give
    # the reconstructed Alloy 6 instance useful, type-oriented names by
    # choosing the smallest static signature that contains each atom.
    labels: dict[str, str] = {}
    label_counts: dict[str, int] = {}
    for atom in sorted(atoms):
        candidates = [
            name
            for name in static_signature_names
            if any(str(tuple_[0]) == atom for tuple_ in value.get(name, []))
        ]
        if candidates:
            prefix = min(candidates, key=lambda name: (len(value.get(name, [])), name in original.abstract, name))
        else:
            prefix = "Atom"
        index = label_counts.get(prefix, 0)
        label_counts[prefix] = index + 1
        labels[atom] = f"_{prefix}{index}"

    configuration = []
    for name in sorted(static_signature_names):
        configuration.append(_relation_formula(name, value.get(name, []), alloy6=True, labels=labels))
    for name in sorted(static_field_names):
        configuration.append(_relation_formula(name, value.get(name, []), alloy6=True, labels=labels))

    state_formulas: list[list[str]] = []
    for state in states:
        formulas = []
        for name in sorted(collector.mutable_global):
            tuples = [tuple_[1:] for tuple_ in value.get(name, []) if str(tuple_[0]) == state]
            formulas.append(_relation_formula(name, tuples, alloy6=True, labels=labels))
        for name in sorted(collector.mutable_local):
            tuples = [tuple_[:-1] for tuple_ in value.get(name, []) if str(tuple_[-1]) == state]
            formulas.append(_relation_formula(name, tuples, alloy6=True, labels=labels))
        state_formulas.append(formulas or ["true"])

    atom_names = ",".join(sorted(labels[atom] for atom in atoms))
    lines = []
    if atom_names:
        lines.append(f"some disj {atom_names} : univ {{")
    else:
        lines.append("{")
    lines.append("  // configuration")
    lines.extend(f"  {formula}" for formula in configuration)
    lines.append("")

    for index, formulas in enumerate(state_formulas):
        lines.append("  {")
        lines.append(f"  // state {index}")
        lines.extend(f"  {formula}" for formula in formulas)
        suffix = ";" if index + 1 < len(state_formulas) else ""
        lines.append(f"  }}{suffix}")

    period = len(states) - loop_index
    prefix = "after " * loop_index
    advance = "after " * period
    lines.append("")
    lines.append(f"  // enforce loop from state {len(states) - 1} to state {loop_index}")
    lines.append(f"  {prefix}always {{")
    for index in range(loop_index, len(states)):
        formulas = state_formulas[index]
        lines.append("    ({")
        lines.append(f"      // state {index}")
        lines.extend(f"      {formula}" for formula in formulas)
        lines.append(f"    }}) implies {advance}({{")
        lines.append(f"      // state {index}")
        lines.extend(f"      {formula}" for formula in formulas)
        lines.append("    })")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines), len(states)


def build_instance(collector: Collector, value: dict[str, list[list[object]]]) -> Instance:
    atoms = set()
    for sig in collector.toplevel:
        for tuple_ in value[sig]:
            atoms.add(_atom_text(tuple_[0]))
    if atoms:
        instance = "\tsome disj " + ",".join(sorted(atoms)) + " : univ {\n"
    else:
        instance = "\t{\n"
    for relation_name in sorted(value):
        tuples = value[relation_name]
        if tuples:
            relation = []
            for tuple_ in tuples:
                relation.append("->".join([_atom_text(atom) for atom in tuple_]))
            instance += f"\t\t{relation_name} = " + " + ".join(relation) + "\n"
        else:
            instance += f"\t\tno {relation_name}\n"
    instance += "\t}\n"
    relations = {
        name: tuple(tuple(str(atom) for atom in tuple_) for tuple_ in tuples)
        for name, tuples in value.items()
    }
    if collector.temporal:
        alloy6_body, trace_length = _alloy6_instance(collector, value)
        return Instance(instance, alloy6_body, trace_length, relations)
    return Instance(instance, relations=relations)


def print_instances(instances: list[str], scope: int, collector: Optional[Collector] = None) -> None:
    for i, inst in enumerate(instances):
        if isinstance(inst, Instance) and inst.alloy6_body is not None:
            command = (
                f"run Test{i + 1} {{\n{inst.alloy6_body}\n}} "
                f"for {scope} but {inst.trace_length}..{inst.trace_length} steps"
            )
        else:
            command = f"run Test{i + 1} {{\n{inst}\n}} for {scope}"
        print(command)
