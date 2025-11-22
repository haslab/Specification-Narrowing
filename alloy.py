from lark import lark, Visitor, Tree

alloy_grammar = r"""
%import common.WS
%ignore WS
%import common.CNAME -> NAME
start: paragraph*
paragraph: signature | fact | predicate
signature: [ABSTRACT] [MULTIPLICITY] "sig" names [RELATION NAME] "{" [field ("," field)*] "}"
names: NAME ("," NAME)*
field: NAME ":" TYPE
fact: "fact" NAME "{" [expr] "}"
predicate: "pred" NAME "{" [expr] "}"
expr: ANY? ("{" expr "}")? expr?
MULTIPLICITY: "one" | "lone" | "some"
RELATION: "extends" | "in"
ABSTRACT: "abstract"
TYPE: /[^,}]+/
ANY: /[^{}]+/
"""

parser = lark.Lark(alloy_grammar, start='start', parser='earley')


def expr2string(tree):
    result = ""
    for child in tree.children:
        if isinstance(child, Tree):
            if child.children:
                result += "{" + expr2string(child) + "}"
        else:
            result += child.value
    return result

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
        for n in tree.children[2].children:
            self.signatures.add(n.value)
        
            if not tree.children[3]:
                self.toplevel.add(n.value)
            else:
                parent = tree.children[4].value
                self.subsets[n.value] = parent
                if tree.children[3].value == "extends":
                    self.extensions.setdefault(parent,set()).add(n)
            if tree.children[1]:
                self.multiplicities[n.value] = tree.children[1].value
            if tree.children[0]:
                self.abstract.add(n.value)

    def field(self, tree):
        for p in tree.parent.children[2].children:
            parent = p.value
            field_name = tree.children[0].value
            self.fields[field_name] = parent + " -> " + tree.children[1].value.strip()

    def predicate(self, tree):
        if tree.children[1]:
            self.predicates[tree.children[0].value] = expr2string(tree.children[1])
        else:
            self.predicates[tree.children[0].value] = ""

    def fact(self, tree):
        self.facts[tree.children[0].value] = expr2string(tree.children[1])

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
            atoms.add(str(tuple[0]).replace('$',''))
    if atoms:
        instance = "\tsome disj " + ",".join(atoms) + " : univ {\n"
    else:
        instance = "\t{\n"
    for rel in value:
        tuples = value[rel]
        if tuples:
            relation = []
            for tuple in tuples:
                relation.append("->".join([str(atom).replace('$','') for atom in tuple]))
            instance += f"\t\t{rel} = " + " + ".join(relation) + "\n"
        else:
            instance += f"\t\tno {rel}\n"
    instance += "\t}\n"
    return instance

def print_instances(instances, scope):
    for i, inst in enumerate(instances):
        command = f"run Test{i+1} {{\n{inst}\n}} for {scope}"
        print(command)