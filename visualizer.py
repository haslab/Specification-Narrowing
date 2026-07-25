"""Native Tk visualization for generated Alloy instances.

The rendering code is deliberately separated from Tk widgets: ``instance_view``
turns solver tuples into a small, testable graph snapshot, while
``NativeInstanceVisualizer`` owns the interactive window.
"""

from __future__ import annotations

import colorsys
from dataclasses import dataclass
import math
from timeit import default_timer as timer
from typing import Callable, Optional

from alloy import Collector, Instance


INTERNAL_RELATIONS = {"State", "__SNFirst", "__sn_step", "__sn_loop"}
PALETTE = (
    "#5B8FF9",
    "#61DDAA",
    "#F6BD16",
    "#E8684A",
    "#6DC8EC",
    "#9270CA",
    "#FF9D4D",
    "#269A99",
)
EDGE_PALETTE = (
    "#376FB6",
    "#C44E52",
    "#238B68",
    "#8055A5",
    "#CC7314",
    "#008C95",
    "#95652F",
    "#C84383",
)


def signature_colors(collector: Collector) -> dict[str, str]:
    """Assign stable, distinct colors to Alloy extension signatures."""

    metadata = collector.original or collector
    signatures = sorted(
        {
            name
            for declaration in metadata._signature_decls
            if declaration.relation != "in"
            for name in declaration.names
        }
    )
    colors = {}
    for index, signature in enumerate(signatures):
        if index < len(PALETTE):
            color = PALETTE[index]
        else:
            # Golden-angle hue stepping extends the palette without making
            # later signatures repeat an earlier color.
            hue = (0.08 + index * 0.61803398875) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.62, 0.82)
            color = f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"
            while color in colors.values():
                hue = (hue + 0.037) % 1.0
                red, green, blue = colorsys.hsv_to_rgb(hue, 0.62, 0.82)
                color = f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"
        colors[signature] = color
    colors["Atom"] = "#68758A"
    return colors


def relation_colors(collector: Collector) -> dict[str, str]:
    """Assign a stable, distinct line color to every field relation."""

    metadata = collector.original or collector
    relations = sorted(metadata.fields)
    colors = {}
    for index, relation in enumerate(relations):
        if index < len(EDGE_PALETTE):
            color = EDGE_PALETTE[index]
        else:
            hue = (0.56 + index * 0.61803398875) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.70, 0.68)
            color = f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"
            while color in colors.values():
                hue = (hue + 0.037) % 1.0
                red, green, blue = colorsys.hsv_to_rgb(hue, 0.70, 0.68)
                color = f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"
        colors[relation] = color
    return colors


@dataclass(frozen=True)
class GraphSnapshot:
    atoms: tuple[str, ...]
    labels: dict[str, str]
    types: dict[str, str]
    memberships: dict[str, tuple[str, ...]]
    edges: tuple[tuple[str, str, str], ...]
    higher_arity: tuple[tuple[str, tuple[str, ...]], ...]
    state_index: Optional[int]
    state_count: int
    loop_index: Optional[int]


def force_directed_positions(
    atoms: tuple[str, ...],
    edges: tuple[tuple[str, str, str], ...],
    initial: Optional[dict[str, tuple[float, float]]] = None,
    pinned: frozenset[str] = frozenset(),
    iterations: int = 140,
) -> dict[str, tuple[float, float]]:
    """Lay out a relation graph in normalized coordinates.

    This is a small deterministic Fruchterman-Reingold implementation.  It
    keeps enough boundary space for node and membership labels and accepts
    pinned nodes so a manual drag can be followed by local untangling.
    """

    if not atoms:
        return {}
    count = len(atoms)
    positions: dict[str, list[float]] = {}
    for index, atom in enumerate(atoms):
        if initial and atom in initial:
            x, y = initial[atom]
        elif count == 1:
            x, y = 0.5, 0.45
        else:
            angle = -math.pi / 2 + 2 * math.pi * index / count
            x = 0.5 + 0.34 * math.cos(angle)
            y = 0.45 + 0.30 * math.sin(angle)
        positions[atom] = [x, y]

    graph_edges = sorted(
        {
            (source, target)
            for source, target, _relation in edges
            if source in positions and target in positions and source != target
        }
    )
    area = 0.68 * 0.66
    ideal = math.sqrt(area / count) * 0.72
    for iteration in range(iterations):
        displacement = {atom: [0.0, 0.0] for atom in atoms}
        for left_index, left in enumerate(atoms):
            for right in atoms[left_index + 1:]:
                dx = positions[left][0] - positions[right][0]
                dy = positions[left][1] - positions[right][1]
                distance = math.hypot(dx, dy)
                if distance < 1e-5:
                    # Deterministic nudge for coincident nodes.
                    dx = 0.001 * (left_index + 1)
                    dy = -0.001 * (left_index + 1)
                    distance = math.hypot(dx, dy)
                force = ideal * ideal / distance
                fx, fy = dx / distance * force, dy / distance * force
                displacement[left][0] += fx
                displacement[left][1] += fy
                displacement[right][0] -= fx
                displacement[right][1] -= fy

        for source, target in graph_edges:
            dx = positions[source][0] - positions[target][0]
            dy = positions[source][1] - positions[target][1]
            distance = max(math.hypot(dx, dy), 1e-5)
            force = distance * distance / ideal
            fx, fy = dx / distance * force, dy / distance * force
            displacement[source][0] -= fx
            displacement[source][1] -= fy
            displacement[target][0] += fx
            displacement[target][1] += fy

        temperature = 0.08 * (1 - iteration / max(1, iterations)) + 0.002
        for atom in atoms:
            if atom in pinned:
                continue
            # A light center pull keeps disconnected components in view.
            displacement[atom][0] += (0.5 - positions[atom][0]) * 0.06
            displacement[atom][1] += (0.45 - positions[atom][1]) * 0.06
            dx, dy = displacement[atom]
            magnitude = max(math.hypot(dx, dy), 1e-9)
            positions[atom][0] += dx / magnitude * min(magnitude, temperature)
            positions[atom][1] += dy / magnitude * min(magnitude, temperature)
            positions[atom][0] = min(0.88, max(0.12, positions[atom][0]))
            positions[atom][1] = min(0.79, max(0.14, positions[atom][1]))

    return {atom: tuple(position) for atom, position in positions.items()}


def typed_layered_positions(
    atoms: tuple[str, ...],
    edges: tuple[tuple[str, str, str], ...],
    types: dict[str, str],
) -> dict[str, tuple[float, float]]:
    """Arrange atom types in relation-directed layers without node overlap."""

    if not atoms:
        return {}
    type_names = sorted({types.get(atom, "Atom") for atom in atoms})
    adjacency = {type_name: set() for type_name in type_names}
    for source, target, _relation in edges:
        source_type = types.get(source, "Atom")
        target_type = types.get(target, "Atom")
        if source_type != target_type:
            adjacency[source_type].add(target_type)

    # Collapse cycles before assigning a longest-path layer to each type.
    index = 0
    indices = {}
    lowlinks = {}
    stack = []
    on_stack = set()
    components = []

    def visit(node):
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for following in sorted(adjacency[node]):
            if following not in indices:
                visit(following)
                lowlinks[node] = min(lowlinks[node], lowlinks[following])
            elif following in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[following])
        if lowlinks[node] == indices[node]:
            component = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(tuple(sorted(component)))

    for type_name in type_names:
        if type_name not in indices:
            visit(type_name)

    component_of = {
        type_name: component_index
        for component_index, component in enumerate(components)
        for type_name in component
    }
    component_edges = {component_index: set() for component_index in range(len(components))}
    indegree = {component_index: 0 for component_index in range(len(components))}
    for source_type, targets in adjacency.items():
        source_component = component_of[source_type]
        for target_type in targets:
            target_component = component_of[target_type]
            if source_component == target_component or target_component in component_edges[source_component]:
                continue
            component_edges[source_component].add(target_component)
            indegree[target_component] += 1

    ranks = {component_index: 0 for component_index in range(len(components))}
    queue = sorted(component for component, degree in indegree.items() if degree == 0)
    while queue:
        component = queue.pop(0)
        for following in sorted(component_edges[component]):
            ranks[following] = max(ranks[following], ranks[component] + 1)
            indegree[following] -= 1
            if indegree[following] == 0:
                queue.append(following)
                queue.sort()

    layer_atoms = {}
    for atom in atoms:
        rank = ranks[component_of[types.get(atom, "Atom")]]
        layer_atoms.setdefault(rank, []).append(atom)
    layer_numbers = sorted(layer_atoms)
    positions = {}
    for layer_offset, layer in enumerate(layer_numbers):
        members = sorted(layer_atoms[layer], key=lambda atom: (types.get(atom, "Atom"), atom))
        if len(layer_numbers) == 1:
            layer_center = 0.5
            layer_width = 0.72
        else:
            layer_center = 0.12 + 0.76 * layer_offset / (len(layer_numbers) - 1)
            layer_width = min(0.24, 0.62 / len(layer_numbers))
        column_count = math.ceil(len(members) / 3)
        for member_index, atom in enumerate(members):
            column = member_index // 3
            row = member_index % 3
            rows_in_column = min(3, len(members) - column * 3)
            if column_count == 1:
                x = layer_center
            else:
                x = layer_center - layer_width / 2 + layer_width * column / (column_count - 1)
            y = 0.5 if rows_in_column == 1 else 0.14 + 0.68 * row / (rows_in_column - 1)
            positions[atom] = (min(0.94, max(0.06, x)), y)
    return positions


def clipped_edge(
    source: tuple[float, float],
    target: tuple[float, float],
    radius_x: float = 32,
    radius_y: float = 25,
) -> tuple[float, float, float, float]:
    """Clip a straight edge to elliptical node boundaries."""

    x1, y1 = source
    x2, y2 = target
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return x1, y1, x2, y2
    scale = min(
        0.45,
        1 / math.sqrt((dx / radius_x) ** 2 + (dy / radius_y) ** 2),
    )
    return x1 + dx * scale, y1 + dy * scale, x2 - dx * scale, y2 - dy * scale


def distance_to_segment(x, y, x1, y1, x2, y2):
    """Distance from a point to a line segment, for edge hover detection."""

    dx, dy = x2 - x1, y2 - y1
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return math.hypot(x - x1, y - y1)
    amount = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_squared))
    return math.hypot(x - (x1 + amount * dx), y - (y1 + amount * dy))


def parallel_edge_slots(edges, separation: float = 20.0):
    """Assign stable curved lanes to relations joining the same atom pair."""

    groups = {}
    for edge in edges:
        source, target, _relation = edge
        key = (source, target) if source == target else tuple(sorted((source, target)))
        groups.setdefault(key, []).append(edge)

    slots = {}
    for group in groups.values():
        ordered = sorted(group, key=lambda edge: (edge[2], edge[0], edge[1]))
        count = len(ordered)
        for index, edge in enumerate(ordered):
            offset = (index - (count - 1) / 2) * separation
            source, target, _relation = edge
            # curved_edge_points measures its perpendicular from source to
            # target. Reverse the lane offset for a reverse-directed edge so
            # every edge in this unordered pair still uses the same canonical
            # set of physical lanes.
            if source != target and (source, target) != tuple(sorted((source, target))):
                offset = -offset
            slots[edge] = (index, count, offset)
    return slots


def _ellipse_boundary(center, toward, radius_x=32.0, radius_y=25.0):
    x, y = center
    dx, dy = toward[0] - x, toward[1] - y
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return center
    scale = 1 / math.sqrt((dx / radius_x) ** 2 + (dy / radius_y) ** 2)
    return x + dx * scale, y + dy * scale


def curved_edge_points(source, target, offset: float):
    """Return boundary-clipped quadratic points for one parallel edge lane."""

    x1, y1 = source
    x2, y2 = target
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return (source, source, target)
    control = (
        (x1 + x2) / 2 - dy / length * offset,
        (y1 + y2) / 2 + dx / length * offset,
    )
    return (
        _ellipse_boundary(source, control),
        control,
        _ellipse_boundary(target, control),
    )


def quadratic_point(points, amount):
    """Evaluate the quadratic curve described by three points."""

    start, control, end = points
    inverse = 1 - amount
    return (
        inverse * inverse * start[0]
        + 2 * inverse * amount * control[0]
        + amount * amount * end[0],
        inverse * inverse * start[1]
        + 2 * inverse * amount * control[1]
        + amount * amount * end[1],
    )


def self_loop_points(x: float, y: float, lane: int = 0) -> tuple[float, ...]:
    """Control points for a smooth directed self-loop above an atom."""

    side = 44 + lane * 12
    peak = 65 + lane * 14
    endpoint = 18 + lane * 2
    return (
        x - endpoint,
        y - 21,
        x - side,
        y - (49 + lane * 8),
        x,
        y - peak,
        x + side,
        y - (49 + lane * 8),
        x + endpoint,
        y - 21,
    )


def scale_positions(
    positions: dict[str, tuple[float, float]],
    width: int,
    graph_height: int,
) -> dict[str, tuple[float, float]]:
    """Map normalized layout coordinates into a safely padded canvas area."""

    left, right, top, bottom = 55, width - 55, 45, graph_height - 50
    return {
        atom: (
            left + x * (right - left),
            top + y * (bottom - top),
        )
        for atom, (x, y) in positions.items()
    }


def following_state_index(snapshot: GraphSnapshot, current: int) -> int:
    """Advance through a finite prefix, then follow its mandatory back-loop."""

    if not snapshot.state_count:
        return current
    if current + 1 < snapshot.state_count:
        return current + 1
    return snapshot.loop_index if snapshot.loop_index is not None else current


def _trace(instance: Instance) -> tuple[list[str], Optional[int]]:
    relations = instance.relations or {}
    first = relations.get("__SNFirst", ())
    if len(first) != 1:
        return [], None
    states = [first[0][0]]
    step = {tuple_[0]: tuple_[1] for tuple_ in relations.get("__sn_step", ())}
    while states[-1] in step and step[states[-1]] not in states:
        states.append(step[states[-1]])
    loops = relations.get("__sn_loop", ())
    if len(loops) != 1 or loops[0][1] not in states:
        return states, None
    return states, states.index(loops[0][1])


def _display_labels(
    collector: Collector,
    relations,
    atoms: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Name atoms from the deepest ``extends`` signature, as Alloy does."""

    metadata = collector.original or collector
    extension_parent = {
        name: declaration.parent
        for declaration in metadata._signature_decls
        if declaration.relation == "extends"
        for name in declaration.names
    }
    extension_names = {
        name
        for declaration in metadata._signature_decls
        if declaration.relation != "in"
        for name in declaration.names
    }

    def extension_depth(name):
        depth = 0
        seen = set()
        while name in extension_parent and name not in seen:
            seen.add(name)
            name = extension_parent[name]
            depth += 1
        return depth

    result: dict[str, str] = {}
    types: dict[str, str] = {}
    counts: dict[str, int] = {}
    for atom in sorted(atoms):
        signatures = [
            name
            for name in extension_names
            if any(tuple_ and tuple_[0] == atom for tuple_ in relations.get(name, ()))
        ]
        if signatures:
            signature = max(
                signatures,
                key=lambda name: (extension_depth(name), name),
            )
        else:
            signature = "Atom"
        number = counts.get(signature, 0)
        counts[signature] = number + 1
        result[atom] = f"{signature}{number}"
        types[atom] = signature
    return result, types


def instance_view(
    collector: Collector,
    instance: Instance,
    state_index: int = 0,
) -> GraphSnapshot:
    """Convert an instance into one static or temporal graph snapshot."""

    relations = instance.relations or {}
    metadata = collector.original or collector
    states, loop_index = _trace(instance) if collector.temporal else ([], None)
    if states:
        state_index = max(0, min(state_index, len(states) - 1))
        state = states[state_index]
    else:
        state_index = 0
        state = None

    visible: dict[str, tuple[tuple[str, ...], ...]] = {}
    for name, tuples in relations.items():
        if name in INTERNAL_RELATIONS:
            continue
        if state is not None and name in collector.mutable_global:
            visible[name] = tuple(tuple_[1:] for tuple_ in tuples if tuple_ and tuple_[0] == state)
        elif state is not None and name in collector.mutable_local:
            visible[name] = tuple(tuple_[:-1] for tuple_ in tuples if tuple_ and tuple_[-1] == state)
        else:
            visible[name] = tuples

    atoms = {
        atom
        for tuples in visible.values()
        for tuple_ in tuples
        for atom in tuple_
    }
    labels, types = _display_labels(collector, relations, atoms)
    inclusion_names = {
        name
        for declaration in metadata._signature_decls
        if declaration.relation == "in"
        for name in declaration.names
    }
    memberships = {
        atom: tuple(
            sorted(
                name
                for name in inclusion_names
                if (atom,) in visible.get(name, ())
            )
        )
        for atom in atoms
    }

    field_names = set(metadata.fields) | collector.mutable_local
    edges = []
    higher_arity = []
    for name in sorted(field_names):
        for tuple_ in visible.get(name, ()):
            if len(tuple_) == 2:
                edges.append((tuple_[0], tuple_[1], name))
            elif tuple_:
                higher_arity.append((name, tuple_))

    return GraphSnapshot(
        atoms=tuple(sorted(atoms, key=lambda atom: labels.get(atom, atom))),
        labels=labels,
        types=types,
        memberships=memberships,
        edges=tuple(edges),
        higher_arity=tuple(higher_arity),
        state_index=state_index if states else None,
        state_count=len(states),
        loop_index=loop_index,
    )


def specification_source(collector: Collector, predicate: str) -> str:
    """Render one collected alternative as a complete Alloy predicate."""

    source = collector.original or collector
    body = source.predicates[predicate].strip()
    indented = "\n".join(f"  {line}" for line in body.splitlines())
    return f"pred {predicate} {{\n{indented}\n}}"


def instance_layout_graph(
    collector: Collector,
    instance: Instance,
) -> tuple[tuple[str, ...], tuple[tuple[str, str, str], ...], tuple[str, ...]]:
    """Return the union graph used for stable layout and relation filters."""

    first = instance_view(collector, instance, 0)
    snapshots = [first]
    if first.state_count:
        snapshots.extend(
            instance_view(collector, instance, index)
            for index in range(1, first.state_count)
        )
    atoms = tuple(sorted({atom for snapshot in snapshots for atom in snapshot.atoms}))
    edges = tuple(sorted({edge for snapshot in snapshots for edge in snapshot.edges}))
    relation_names = tuple(
        sorted(
            {relation for _source, _target, relation in edges}
            | {
                relation
                for snapshot in snapshots
                for relation, _tuple in snapshot.higher_arity
            }
        )
    )
    return atoms, edges, relation_names


class InstanceCard:
    def __init__(
        self,
        tk,
        parent,
        collector,
        instance,
        number,
        classify,
        saved_state=None,
    ):
        self.tk = tk
        self.collector = collector
        self.instance = instance
        self.number = number
        self.classify = classify
        self.signature_colors = signature_colors(collector)
        self.relation_colors = relation_colors(collector)
        saved_state = saved_state or {}
        self.state_index = saved_state.get("state_index", 0)
        self.layout_atoms, self.layout_edges, relation_names = instance_layout_graph(
            collector,
            instance,
        )
        self.layout_types = instance_view(collector, instance, 0).types
        saved_positions = saved_state.get("positions")
        self.positions = (
            dict(saved_positions)
            if saved_positions and set(saved_positions) == set(self.layout_atoms)
            else typed_layered_positions(
                self.layout_atoms,
                self.layout_edges,
                self.layout_types,
            )
        )
        self.pinned: set[str] = set(saved_state.get("pinned", ()))
        self.screen_positions: dict[str, tuple[float, float]] = {}
        self.dragged_atom: Optional[str] = None
        self.drag_moved = False
        self.hovered = None
        self.screen_edges = []

        self.frame = tk.Frame(parent, bg="#F7F8FA", highlightbackground="#CBD1DC", highlightthickness=1)
        header = tk.Frame(self.frame, bg="#F7F8FA")
        header.pack(fill="x", padx=10, pady=(8, 3))
        tk.Label(
            header,
            text=f"Test {number}",
            font=("TkDefaultFont", 13, "bold"),
            bg="#F7F8FA",
        ).pack(side="left")
        self.state_label = tk.Label(header, text="", bg="#F7F8FA", fg="#4E5969")
        self.state_label.pack(side="right")

        self.canvas = tk.Canvas(
            self.frame,
            width=390,
            height=300,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=5)
        self.canvas.bind("<Configure>", lambda _event: self.render())
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drag)
        self.canvas.bind("<Double-Button-1>", self.unpin_atom)
        self.canvas.bind("<Motion>", self.update_hover)
        self.canvas.bind("<Leave>", self.clear_hover)

        graph_controls = tk.Frame(self.frame, bg="#F7F8FA")
        graph_controls.pack(fill="x", padx=10, pady=(0, 4))
        self.relation_vars = {
            relation: tk.BooleanVar(
                value=saved_state.get("relations", {}).get(relation, True)
            )
            for relation in relation_names
        }
        self.relations_button = tk.Menubutton(
            graph_controls,
            text="Relations ▾",
            relief="raised",
        )
        relations_menu = tk.Menu(self.relations_button, tearoff=False)
        self.relations_button.configure(menu=relations_menu)
        if relation_names:
            for relation in relation_names:
                relations_menu.add_checkbutton(
                    label=f"● {relation}",
                    variable=self.relation_vars[relation],
                    command=self.render,
                    foreground=self.relation_colors.get(relation, "#68758A"),
                )
            relations_menu.add_separator()
            relations_menu.add_command(
                label="Show all",
                command=lambda: self.set_all_relations(True),
            )
            relations_menu.add_command(
                label="Hide all",
                command=lambda: self.set_all_relations(False),
            )
        else:
            relations_menu.add_command(label="No field relations", state="disabled")
        self.relations_button.pack(side="left")
        tk.Label(
            graph_controls,
            text="Drag atoms to pin them",
            bg="#F7F8FA",
            fg="#7A8494",
        ).pack(side="left", padx=8)
        tk.Button(
            graph_controls,
            text="Reset layout",
            command=self.reset_layout,
        ).pack(side="right")

        state_controls = tk.Frame(self.frame, bg="#F7F8FA")
        state_controls.pack(fill="x", padx=10)
        self.previous_state = tk.Button(state_controls, text="← State", command=lambda: self.change_state(-1))
        self.previous_state.pack(side="left")
        self.next_state = tk.Button(state_controls, text="State →", command=lambda: self.change_state(1))
        self.next_state.pack(side="right")

        choices = tk.Frame(self.frame, bg="#F7F8FA")
        choices.pack(fill="x", padx=10, pady=(7, 10))
        self.no_button = tk.Button(
            choices,
            text="Undesirable",
            fg="#A61D24",
            command=lambda: self.choose(False),
        )
        self.no_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.yes_button = tk.Button(
            choices,
            text="Desirable",
            fg="#237804",
            command=lambda: self.choose(True),
        )
        self.yes_button.pack(side="right", fill="x", expand=True, padx=(4, 0))
        self.render()

    def export_state(self):
        return {
            "state_index": self.state_index,
            "positions": dict(self.positions),
            "pinned": set(self.pinned),
            "relations": {
                relation: variable.get()
                for relation, variable in self.relation_vars.items()
            },
        }

    def set_all_relations(self, visible):
        for variable in self.relation_vars.values():
            variable.set(visible)
        self.render()

    def relation_is_visible(self, relation):
        variable = self.relation_vars.get(relation)
        return variable is None or variable.get()

    def reset_layout(self):
        self.pinned.clear()
        self.positions = typed_layered_positions(
            self.layout_atoms,
            self.layout_edges,
            self.layout_types,
        )
        self.render()

    def graph_bounds(self, graph_height):
        width = max(200, self.canvas.winfo_width())
        return width, (55, width - 55, 45, graph_height - 50)

    def atom_at(self, x, y):
        if not self.screen_positions:
            return None
        atom, distance = min(
            (
                (atom, math.hypot(x - position[0], y - position[1]))
                for atom, position in self.screen_positions.items()
            ),
            key=lambda item: item[1],
        )
        return atom if distance <= 48 else None

    def start_drag(self, event):
        self.dragged_atom = self.atom_at(event.x, event.y)
        self.drag_moved = False

    def drag(self, event):
        if self.dragged_atom is None:
            return
        height = max(180, self.canvas.winfo_height())
        snapshot = instance_view(self.collector, self.instance, self.state_index)
        detail_height = 48 if any(
            self.relation_is_visible(relation)
            for relation, _tuple in snapshot.higher_arity
        ) else 0
        graph_height = height - detail_height
        _width, (left, right, top, bottom) = self.graph_bounds(graph_height)
        x = min(right, max(left, event.x))
        y = min(bottom, max(top, event.y))
        self.positions[self.dragged_atom] = (
            (x - left) / max(1, right - left),
            (y - top) / max(1, bottom - top),
        )
        self.pinned.add(self.dragged_atom)
        self.drag_moved = True
        self.render()

    def finish_drag(self, _event):
        self.dragged_atom = None
        self.drag_moved = False

    def unpin_atom(self, event):
        atom = self.atom_at(event.x, event.y)
        if atom is None:
            return
        self.pinned.discard(atom)
        self.dragged_atom = None
        automatic = typed_layered_positions(
            self.layout_atoms,
            self.layout_edges,
            self.layout_types,
        )
        self.positions = {
            candidate: (
                self.positions[candidate]
                if candidate in self.pinned
                else automatic[candidate]
            )
            for candidate in self.layout_atoms
        }
        self.render()

    def update_hover(self, event):
        atom = self.atom_at(event.x, event.y)
        hovered = ("atom", atom) if atom is not None else None
        if hovered is None and self.screen_edges:
            edge, distance = min(
                (
                    (
                        (source, target, relation),
                        distance_to_segment(event.x, event.y, x1, y1, x2, y2),
                    )
                    for source, target, relation, x1, y1, x2, y2 in self.screen_edges
                ),
                key=lambda item: item[1],
            )
            if distance <= 7:
                hovered = ("edge",) + edge
        if hovered != self.hovered:
            self.hovered = hovered
            self.render()

    def clear_hover(self, _event):
        if self.hovered is not None:
            self.hovered = None
            self.render()

    def change_state(self, delta):
        snapshot = instance_view(self.collector, self.instance, self.state_index)
        if snapshot.state_count:
            if delta > 0 and self.state_index + 1 == snapshot.state_count:
                self.state_index = following_state_index(snapshot, self.state_index)
            else:
                self.state_index = max(
                    0,
                    min(self.state_index + delta, snapshot.state_count - 1),
                )
            self.render()

    def choose(self, desirable):
        self.mark_choice(desirable)
        self.classify(self.number - 1, desirable)

    def mark_choice(self, desirable):
        self.yes_button.configure(
            text="✓ Desirable" if desirable else "Desirable",
            relief="sunken" if desirable else "raised",
        )
        self.no_button.configure(
            text="Undesirable" if desirable else "✓ Undesirable",
            relief="raised" if desirable else "sunken",
        )
        self.frame.configure(
            highlightbackground="#52A447" if desirable else "#D55252",
            highlightthickness=2,
        )

    def render(self):
        snapshot = instance_view(self.collector, self.instance, self.state_index)
        canvas = self.canvas
        canvas.delete("all")
        if snapshot.state_count:
            loop = f" · loop to {snapshot.loop_index + 1}" if snapshot.loop_index is not None else ""
            self.state_label.configure(
                text=f"State {snapshot.state_index + 1}/{snapshot.state_count}{loop}"
            )
            self.previous_state.configure(state="normal" if self.state_index else "disabled")
            at_last_state = self.state_index + 1 == snapshot.state_count
            self.next_state.configure(
                state="normal",
                text="Loop ↻" if at_last_state else "State →",
            )
        else:
            self.state_label.configure(text="Static instance")
            self.previous_state.configure(state="disabled")
            self.next_state.configure(state="disabled")

        width = max(200, canvas.winfo_width())
        height = max(180, canvas.winfo_height())
        visible_higher_arity = tuple(
            (relation, tuple_)
            for relation, tuple_ in snapshot.higher_arity
            if self.relation_is_visible(relation)
        )
        detail_height = 48 if visible_higher_arity else 0
        graph_height = height - detail_height
        count = len(snapshot.atoms)
        _width, (left, right, top, bottom) = self.graph_bounds(graph_height)
        positions = scale_positions(
            {
                atom: self.positions.get(atom, (0.5, 0.5))
                for atom in snapshot.atoms
            },
            width,
            graph_height,
        )
        self.screen_positions = positions
        self.screen_edges = []
        visible_relation_names = {
            relation
            for relation, variable in self.relation_vars.items()
            if variable.get()
        }
        show_selected_relation_labels = len(visible_relation_names) == 1

        visible_edges = tuple(
            edge
            for edge in snapshot.edges
            if self.relation_is_visible(edge[2])
            and edge[0] in positions
            and edge[1] in positions
        )
        edge_slots = parallel_edge_slots(visible_edges)

        # Draw field arrows first so nodes remain legible. Relations sharing
        # endpoints are fanned into stable lanes instead of being overdrawn.
        for source, target, relation in visible_edges:
            x1, y1 = positions[source]
            x2, y2 = positions[target]
            lane, lane_count, offset = edge_slots[(source, target, relation)]
            relation_color = self.relation_colors.get(relation, "#68758A")
            focused = self.hovered in {
                ("atom", source),
                ("atom", target),
                ("edge", source, target, relation),
            }
            line_width = 3 if focused else 2
            show_label = show_selected_relation_labels or focused
            if source == target:
                loop_points = self_loop_points(x1, y1, lane)
                canvas.create_line(
                    *loop_points,
                    smooth=True,
                    splinesteps=24,
                    arrow="last",
                    fill=relation_color,
                    width=line_width,
                )
                loop_pairs = tuple(zip(loop_points[::2], loop_points[1::2]))
                for start, end in zip(loop_pairs, loop_pairs[1:]):
                    self.screen_edges.append(
                        (source, target, relation, *start, *end)
                    )
                if show_label:
                    canvas.create_text(
                        x1 + 31 + lane * 10,
                        y1 - 25 - lane * 12,
                        text=relation,
                        fill=relation_color,
                        anchor="w",
                    )
            elif lane_count > 1:
                curve = curved_edge_points((x1, y1), (x2, y2), offset)
                samples = tuple(
                    quadratic_point(curve, step / 16)
                    for step in range(17)
                )
                canvas.create_line(
                    *(coordinate for point in samples for coordinate in point),
                    arrow="last",
                    fill=relation_color,
                    width=line_width,
                )
                for start, end in zip(samples, samples[1:]):
                    self.screen_edges.append(
                        (source, target, relation, *start, *end)
                    )
                if show_label:
                    label_x, label_y = quadratic_point(curve, 0.5)
                    canvas.create_text(
                        label_x,
                        label_y - 8,
                        text=relation,
                        fill=relation_color,
                    )
            else:
                edge_x1, edge_y1, edge_x2, edge_y2 = clipped_edge(
                    (x1, y1),
                    (x2, y2),
                )
                canvas.create_line(
                    edge_x1,
                    edge_y1,
                    edge_x2,
                    edge_y2,
                    arrow="last",
                    fill=relation_color,
                    width=line_width,
                )
                self.screen_edges.append(
                    (
                        source,
                        target,
                        relation,
                        edge_x1,
                        edge_y1,
                        edge_x2,
                        edge_y2,
                    )
                )
                if show_label:
                    canvas.create_text(
                        (edge_x1 + edge_x2) / 2,
                        (edge_y1 + edge_y2) / 2 - 8,
                        text=relation,
                        fill=relation_color,
                    )

        for index, atom in enumerate(snapshot.atoms):
            x, y = positions[atom]
            memberships = snapshot.memberships.get(atom, ())
            atom_type = snapshot.types.get(atom, "Atom")
            color = self.signature_colors.get(atom_type, self.signature_colors["Atom"])
            canvas.create_oval(x - 31, y - 24, x + 31, y + 24, fill=color, outline="white", width=2)
            if atom in self.pinned:
                canvas.create_oval(
                    x - 35,
                    y - 28,
                    x + 35,
                    y + 28,
                    outline="#2F54A3",
                    width=2,
                )
            canvas.create_text(x, y - 2, text=snapshot.labels.get(atom, atom), fill="white", font=("TkDefaultFont", 10, "bold"))
            if memberships:
                canvas.create_text(x, y + 34, text=" · ".join(memberships), fill="#4E5969", font=("TkDefaultFont", 8))

        if not count:
            canvas.create_text(width / 2, graph_height / 2, text="Empty instance", fill="#8C8C8C", font=("TkDefaultFont", 12))
        if visible_higher_arity:
            for row, (relation, tuple_) in enumerate(visible_higher_arity):
                rendered = " → ".join(
                    snapshot.labels.get(atom, atom.replace("$", ""))
                    for atom in tuple_
                )
                canvas.create_text(
                    10,
                    graph_height + 8 + row * 16,
                    anchor="nw",
                    width=width - 20,
                    text=f"{relation}: {rendered}",
                    fill=self.relation_colors.get(relation, "#68758A"),
                )


@dataclass(frozen=True)
class ClassificationDecision:
    """One reversible answer in an adaptive classification session."""

    instance_index: int
    desirable: bool


@dataclass
class InteractionTiming:
    """Latency components for preparing and classifying one shown test."""

    preparation: str
    preparation_seconds: float
    partition_seconds: float = 0.0
    filtering_seconds: Optional[float] = None


class AdaptiveTestSession:
    """Consume a fixed test suite in an answer-dependent, balanced order."""

    def __init__(
        self,
        predicates: list[str],
        instances: list[Instance],
        evaluate: Callable[[Instance, str], bool],
    ):
        self.predicates = list(predicates)
        self.instances = instances
        self.evaluate = evaluate
        self.remaining = list(predicates)
        self.history: list[ClassificationDecision] = []
        self.truth_cache: dict[tuple[int, str], bool] = {}
        self.timings: list[InteractionTiming] = []
        self._selection_resolved = False
        self._current_index: Optional[int] = None
        self._current_partition: Optional[tuple[list[str], list[str]]] = None
        self._current_timing: Optional[InteractionTiming] = None

    def truth(self, instance_index: int, predicate: str) -> bool:
        key = (instance_index, predicate)
        if key not in self.truth_cache:
            self.truth_cache[key] = self.evaluate(
                self.instances[instance_index],
                predicate,
            )
        return self.truth_cache[key]

    @property
    def answered_indices(self) -> set[int]:
        return {decision.instance_index for decision in self.history}

    def partition(self, instance_index: int) -> tuple[list[str], list[str]]:
        desirable = []
        undesirable = []
        for predicate in self.remaining:
            target = (
                desirable
                if self.truth(instance_index, predicate)
                else undesirable
            )
            target.append(predicate)
        return undesirable, desirable

    def next_instance_index(self) -> Optional[int]:
        """Return the unused test minimizing the largest answer partition."""

        if len(self.remaining) <= 1:
            return None
        if self._selection_resolved:
            return self._current_index

        start = timer()
        unanswered = (
            index
            for index in range(len(self.instances))
            if index not in self.answered_indices
        )
        ranked = []
        for index in unanswered:
            undesirable, desirable = self.partition(index)
            if not undesirable or not desirable:
                continue
            ranked.append(
                (
                    max(len(undesirable), len(desirable)),
                    -len(undesirable) * len(desirable),
                    index,
                    (undesirable, desirable),
                )
            )
        chosen = min(ranked) if ranked else None
        self._selection_resolved = True
        self._current_index = chosen[2] if chosen is not None else None
        self._current_partition = chosen[3] if chosen is not None else None
        self._current_timing = InteractionTiming(
            "fixed-suite selection",
            timer() - start,
        )
        self.timings.append(self._current_timing)
        return self._current_index

    def answer(self, instance_index: int, desirable: bool) -> None:
        if instance_index in self.answered_indices:
            raise ValueError("test has already been classified")
        if len(self.remaining) <= 1:
            raise ValueError("classification session is already complete")
        start = timer()
        self.history.append(ClassificationDecision(instance_index, desirable))
        self.remaining = [
            predicate
            for predicate in self.remaining
            if self.truth(instance_index, predicate) == desirable
        ]
        elapsed = timer() - start
        if self._current_timing is None:
            self._current_timing = InteractionTiming("fixed-suite selection", 0.0)
            self.timings.append(self._current_timing)
        self._current_timing.filtering_seconds = elapsed
        self._invalidate_selection()

    def _invalidate_selection(self) -> None:
        self._selection_resolved = False
        self._current_index = None
        self._current_partition = None
        self._current_timing = None

    def undo(self) -> Optional[ClassificationDecision]:
        if not self.history:
            return None
        decision = self.history.pop()
        self.remaining = list(self.predicates)
        for previous in self.history:
            self.remaining = [
                predicate
                for predicate in self.remaining
                if self.truth(previous.instance_index, predicate)
                == previous.desirable
            ]
        self._invalidate_selection()
        return decision

    def current_test(self):
        instance_index = self.next_instance_index()
        if instance_index is None:
            return None
        return (
            ("fixed", instance_index),
            instance_index + 1,
            self.instances[instance_index],
        )

    def current_partition(self):
        instance_index = self.next_instance_index()
        if instance_index is None:
            return ([], [])
        if self._current_partition is None:
            self._current_partition = self.partition(instance_index)
        return self._current_partition

    def answer_current(self, desirable):
        instance_index = self.next_instance_index()
        if instance_index is None:
            raise ValueError("there is no test to classify")
        self.answer(instance_index, desirable)

    def current_truth(self, predicate):
        instance_index = self.next_instance_index()
        if instance_index is None:
            raise ValueError("there is no test to classify")
        return self.truth(instance_index, predicate)


@dataclass(frozen=True)
class SynthesizedDecision:
    instance: Instance
    desirable: bool


class AdaptiveSynthesisSession:
    """Generate one new test after each answer and support undoing answers."""

    def __init__(
        self,
        predicates: list[str],
        generate: Callable[[list[str]], Instance],
        evaluate: Callable[[Instance, str], bool],
    ):
        self.predicates = list(predicates)
        self.generate = generate
        self.evaluate = evaluate
        self.remaining = list(predicates)
        self.history: list[SynthesizedDecision] = []
        self.truth_cache: dict[tuple[int, str], bool] = {}
        self._current_instance: Optional[Instance] = None
        self._current_partition: Optional[tuple[list[str], list[str]]] = None
        self._current_timing: Optional[InteractionTiming] = None
        self.timings: list[InteractionTiming] = []
        self.generated_count = 0
        self.generation_seconds = 0.0

    def truth(self, instance: Instance, predicate: str) -> bool:
        key = (id(instance), predicate)
        if key not in self.truth_cache:
            self.truth_cache[key] = self.evaluate(instance, predicate)
        return self.truth_cache[key]

    def _ensure_current(self):
        if len(self.remaining) <= 1:
            return None
        if self._current_instance is None:
            start = timer()
            self._current_instance = self.generate(list(self.remaining))
            elapsed = timer() - start
            self.generation_seconds += elapsed
            self.generated_count += 1
            self._current_timing = InteractionTiming(
                "adaptive synthesis",
                elapsed,
            )
            self.timings.append(self._current_timing)
        elif self._current_timing is None:
            # Undo reuses the exact previously shown separator; no solver call
            # is needed, but record the interaction so timing remains legible.
            self._current_timing = InteractionTiming("reused adaptive test", 0.0)
            self.timings.append(self._current_timing)
        return self._current_instance

    def current_test(self):
        instance = self._ensure_current()
        if instance is None:
            return None
        return (id(instance), len(self.history) + 1, instance)

    def current_partition(self):
        instance = self._ensure_current()
        if instance is None:
            return ([], [])
        if self._current_partition is not None:
            return self._current_partition
        start = timer()
        desirable = []
        undesirable = []
        for predicate in self.remaining:
            target = desirable if self.truth(instance, predicate) else undesirable
            target.append(predicate)
        self._current_partition = (undesirable, desirable)
        if self._current_timing is not None:
            self._current_timing.partition_seconds = timer() - start
        return self._current_partition

    def answer_current(self, desirable):
        instance = self._ensure_current()
        if instance is None:
            raise ValueError("there is no test to classify")
        # Evaluate the complete split before timing the cached candidate filter.
        self.current_partition()
        start = timer()
        self.history.append(SynthesizedDecision(instance, desirable))
        self.remaining = [
            predicate
            for predicate in self.remaining
            if self.truth(instance, predicate) == desirable
        ]
        if self._current_timing is not None:
            self._current_timing.filtering_seconds = timer() - start
        self._current_instance = None
        self._current_partition = None
        self._current_timing = None

    def current_truth(self, predicate):
        instance = self._ensure_current()
        if instance is None:
            raise ValueError("there is no test to classify")
        return self.truth(instance, predicate)

    def undo(self):
        if not self.history:
            return None
        decision = self.history.pop()
        self.remaining = list(self.predicates)
        for previous in self.history:
            self.remaining = [
                predicate
                for predicate in self.remaining
                if self.truth(previous.instance, predicate) == previous.desirable
            ]
        self._current_instance = decision.instance
        self._current_partition = None
        self._current_timing = None
        return decision


class NativeInstanceVisualizer:
    """Show the best remaining test and collect reversible classifications."""

    def __init__(
        self,
        collector: Collector,
        instances: Optional[list[Instance]] = None,
        evaluate: Optional[Callable[[Instance, str], bool]] = None,
        session=None,
    ):
        self.collector = collector
        if session is None:
            if instances is None or evaluate is None:
                raise ValueError("instances and evaluate are required for a fixed suite")
            session = AdaptiveTestSession(
                list(collector.predicates),
                instances,
                evaluate,
            )
        self.session = session
        self.root = None
        self.card_host = None
        self.status = None
        self.current_card = None
        self.current_key = None
        self.card_states = {}

    @property
    def remaining(self):
        return self.session.remaining

    def run(self) -> list[str]:
        try:
            import tkinter as tk
        except ImportError as error:
            raise RuntimeError("Python was built without Tk support") from error

        self.tk = tk
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            raise RuntimeError(f"the native window could not be opened: {error}") from error
        self.root.title("Alloy Specification Narrowing")
        self.root.minsize(560, 580)
        window_width = min(self.root.winfo_screenwidth() - 80, 900)
        window_height = min(self.root.winfo_screenheight() - 100, 780)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        top = tk.Frame(self.root, padx=14, pady=10)
        top.pack(fill="x")
        tk.Label(
            top,
            text="Classify generated instances",
            font=("TkDefaultFont", 16, "bold"),
        ).pack(side="left")
        self.status = tk.Label(top, text="", fg="#4E5969")
        self.status.pack(side="right")
        self.card_host = tk.Frame(self.root, padx=14, pady=4)
        self.card_host.pack(fill="both", expand=True)
        self.result_frame = tk.Frame(self.root, padx=14)
        self.result_frame.pack(fill="x", pady=(6, 0))
        result_scrollbar = tk.Scrollbar(self.result_frame, orient="vertical")
        result_scrollbar.pack(side="right", fill="y")
        self.result_text = tk.Text(
            self.result_frame,
            height=5,
            wrap="word",
            font="TkFixedFont",
            bg="#F7F8FA",
            relief="flat",
            yscrollcommand=result_scrollbar.set,
            padx=8,
            pady=6,
        )
        self.result_text.pack(fill="x", expand=True)
        result_scrollbar.configure(command=self.result_text.yview)
        self.result_text.configure(state="disabled")

        self.footer = tk.Frame(self.root, padx=14, pady=10)
        self.footer.pack(fill="x")
        self.back_button = tk.Button(self.footer, text="← Back", command=self.back)
        self.back_button.pack(side="left")
        tk.Button(
            self.footer,
            text="Close",
            command=self.root.destroy,
        ).pack(side="right")

        try:
            self.render_current()
        except Exception:
            self.root.destroy()
            raise
        self.root.mainloop()
        return self.remaining

    def render_current(self):
        if self.current_card is not None and self.current_key is not None:
            self.card_states[self.current_key] = self.current_card.export_state()
        for child in self.card_host.winfo_children():
            child.destroy()
        self.current_card = None
        self.current_key = None
        current = self.session.current_test()
        if current is not None:
            self.current_key, number, instance = current
            self.current_card = InstanceCard(
                self.tk,
                self.card_host,
                self.collector,
                instance,
                number,
                self.classify,
                saved_state=self.card_states.get(self.current_key),
            )
            self.current_card.frame.pack(fill="both", expand=True)
        self.update_status()

    def classify(self, _display_index, desirable):
        self.session.answer_current(desirable)
        self.render_current()

    def back(self):
        if self.session.undo() is not None:
            self.render_current()

    def show_result(self, text, color):
        self.result_text.configure(state="normal", fg=color)
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def update_status(self):
        self.status.configure(
            text=(
                f"{len(self.remaining)} specifications remain  ·  "
                f"{len(self.session.history)} classified"
            )
        )
        self.back_button.configure(
            state="normal" if self.session.history else "disabled"
        )
        if len(self.remaining) == 1:
            predicate = self.remaining[0]
            self.show_result(
                "Selected specification:\n"
                + specification_source(self.collector, predicate),
                "#237804",
            )
        elif not self.remaining:
            self.show_result("No specification is consistent", "#A61D24")
        elif self.current_key is None:
            self.show_result(
                "The remaining specifications are not distinguished by the generated tests.",
                "#A61D24",
            )
        else:
            undesirable, desirable = self.session.current_partition()
            self.show_result(
                "Choose Desirable or Undesirable. This test partitions the "
                f"remaining specifications {len(undesirable)} / {len(desirable)}. "
                "Use Back to revise the previous classification.",
                "#4E5969",
            )
