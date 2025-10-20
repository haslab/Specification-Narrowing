from lark import lark, Visitor, Tree

alloy_grammar = r"""
%import common.WS
%ignore WS
%import common.CNAME -> NAME
start: paragraph*
paragraph: signature | fact | predicate
signature: [ABSTRACT] [MULTIPLICITY] "sig" NAME [RELATION NAME] "{" [field ("," field)*] "}"
field: NAME ":" TYPE
fact: "fact" NAME "{" [EXPR] "}"
predicate: "pred" NAME "{" [EXPR] "}"
MULTIPLICITY: "one" | "lone" | "some"
RELATION: "extends" | "in"
ABSTRACT: "abstract"
TYPE: /[^,}]+/
EXPR: /[^{}]+/
"""

parser = lark.Lark(alloy_grammar, start='start', parser='lalr')

class Parent(Visitor):
    def __default__(self, tree):
        for subtree in tree.children:
            if isinstance(subtree, Tree):
                subtree.parent = tree

class Collector(Visitor):
    def __init__(self):
        self.predicates = {}
        self.signatures = set()
        self.subsets = {}
        self.toplevel = set()
        self.fields = {}
        self.extensions = {}
        self.multiplicities = {}
        self.abstract = set()
        self.facts = {}

    def signature(self, tree):
        self.signatures.add(tree.children[2].value)
        if not tree.children[3]:
            self.toplevel.add(tree.children[2].value)
        else:
            parent = tree.children[4].value
            self.subsets[tree.children[2].value] = parent
            if tree.children[3].value == "extends":
                if parent not in self.extensions:
                    self.extensions[parent] = set()
                self.extensions[parent].add(tree.children[2].value)
        if tree.children[1]:
            self.multiplicities[tree.children[2].value] = tree.children[1].value
        if tree.children[0]:
            self.abstract.add(tree.children[2].value)

    def field(self, tree):
        parent = tree.parent.children[2].value
        field_name = tree.children[0].value
        self.fields[field_name] = parent + " -> " + tree.children[1].value.strip()

    def predicate(self, tree):
        if tree.children[1]:
            self.predicates[tree.children[0].value] = tree.children[1].value.strip()
        else:
            self.predicates[tree.children[0].value] = ""

    def fact(self, tree):
        self.facts[tree.children[0].value] = tree.children[1].value.strip()

def parse(content):
    tree = parser.parse(content)
    parent_setter = Parent()
    parent_setter.visit(tree)
    collector = Collector()
    collector.visit(tree)
    return collector

def build_instance(collector, value):
    atoms = set()
    for sig in collector.toplevel:
        for tuple in value[sig]:
            atoms.add(str(tuple.atom(0)).replace('$',''))
    instance = "\tsome disj " + ",".join(atoms) + " : univ {\n"
    for sig in collector.signatures:
        tuples = value[sig]
        if tuples:
            instance += f"\t\t{sig} = " + " + ".join([str(tuple.atom(0)).replace('$','') for tuple in tuples]) + "\n"
        else:
            instance += f"\t\tno {sig}\n"
    for field in collector.fields:
        tuples = value[field]
        if tuples:
            relation = []
            for tuple in tuples:
                atoms = []
                for k in range(tuple.arity()):
                    atoms.append(str(tuple.atom(k)).replace('$',''))
                relation.append("->".join(atoms))
            instance += f"\t\t{field} = " + " + ".join(relation) + "\n"
        else:
            instance += f"\t\tno {field}\n"
    instance += "\t}\n"
    return instance

def print_instances(instances, scope):
    for i, inst in enumerate(instances):
        command = f"run Test{i+1} {{\n{inst}\n}} for {scope}"
        print(command)