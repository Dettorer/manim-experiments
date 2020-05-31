import manimlib.imports as mn
from manimlib.imports import UP, RIGHT, LEFT, DOWN
import numpy as np
import pygraphviz as pgv
from pylatex.utils import escape_latex


class Node(mn.Circle):
    CONFIG = {
        'radius': 0.3,
    }


class GraphArrow(mn.Arrow):
    CONFIG = {
        #  'stroke_width': 3,
        #  'tip_length': 0.4,
        #  "max_tip_length_to_length_ratio": 0.2,
    }


dot_to_manim_colors = {
    'white': mn.WHITE,
    'DimGray': mn.LIGHT_COLOR,
    '': mn.WHITE,
    'lightgray': mn.LIGHT_COLOR,
}


def scale_ratio_and_shift(graph):
    """
    Compute the ratio and shift by wich we need to rescale and move the graph's
    graphviz positions so that it fits in manim's scene.
    """
    (min_x, min_y) = (float('+inf'), float('+inf'))
    (max_x, max_y) = (float('-inf'), float('-inf'))
    for node in graph.nodes():
        x, y = map(float, node.attr['pos'].split(','))
        min_x, min_y = min(min_x, x), min(min_y, y)
        max_x, max_y = max(max_x, x), max(max_y, y)
    for edge in graph.edges():
        # edge.attr['pos'] contains a list of spline control points of the
        # form: 'e,x1,y1 x2,y2 x3,y3 x4,y4 […]'
        points = [
            (float(x), float(y)) for x, y in
            [point.split(',') for point in
                edge.attr['pos'][2:].split()]
        ]
        # also consider the label's position
        if 'lp' in edge.attr and edge.attr['lp']:
            points.append(map(float, edge.attr['lp'].split(',')))
        for x, y in points:
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)

    width = max_x - min_x
    height = max_y - min_y

    ratio = min(mn.FRAME_WIDTH / width, mn.FRAME_HEIGHT / height)
    # last adjustment: the previous ration only allows for each node's *center*
    # to be in screen, so we need to factor in the manim's rendered circle
    # radius and stroke width
    ratio *= mn.FRAME_WIDTH \
        / (mn.FRAME_WIDTH
            + 2 * Node.CONFIG['radius']
            + mn.Circle().stroke_width / 2)

    center = np.array([
        (max_x + min_x) * ratio / 2,
        (max_y + min_y) * ratio / 2,
        0
    ])

    return ratio, -center


rendered_graphs = 0


def dot_to_vgroup(source):
    A = pgv.AGraph(source)
    A.layout(prog='dot')

    # DEBUG: draw the dot layout in png files
    global rendered_graphs
    A.draw(f'{rendered_graphs}.png')
    rendered_graphs += 1

    ratio, shift = scale_ratio_and_shift(A)

    # spawn each node in manim using the graphviz positions and our rescaling
    # ratio
    mnodes = []
    for node in A.iternodes():
        # 'point' shaped nodes aren't real nodes, they often represent the
        # origin of the arrow of an initial stat or the destination of the
        # arrow of a final state
        if node.attr['shape'] == 'point':
            continue

        x, y = map(lambda s: float(s), node.attr['pos'].split(','))
        pos = np.array([x*ratio, y*ratio, 0])

        # Try to translate graphviz color to manim, fallback to white
        color = dot_to_manim_colors.get(
            node.attr.get('fillcolor', 'white'),
            mn.WHITE
        )

        # Render the node's label and circle
        mlabel = mn.TextMobject(escape_latex(node.name)).move_to(pos)
        mcircle = Node(arc_center=pos, color=color)
        mnodes.append(mn.VGroup(mcircle, mlabel))

    # spawn each edges in a similar way
    medges = []
    for edge in A.edges():
        # edge.attr['pos'] contains a list of spline control points of the
        # form: 'e,x1,y1 x2,y2 x3,y3 x4,y4 […]'
        spline_points = [
            np.array([float(x)*ratio, float(y)*ratio, 0]) for x, y in
            [point.split(',') for point in
                edge.attr['pos'][2:].split()[1:]]
        ]

        # Try to translate graphviz color to manim, fallback to white
        color = dot_to_manim_colors.get(
            edge.attr.get('color', 'white'),
            mn.WHITE
        )

        # Render the edge's label and path
        mpath = mn.VMobject(color=color).set_points_smoothly(spline_points)
        if 'label' in edge.attr and edge.attr['label']:
            (labelx, labely) = map(float, edge.attr['lp'].split(','))
            mlabel = mn.TextMobject(escape_latex(edge.attr['label']))
            mlabel.scale(0.65)
            mlabel.move_to(np.array([labelx*ratio, labely*ratio, 0]))
            medges.append(mn.VGroup(mpath, mlabel))
        else:
            medges.append(mpath)
        print(len(spline_points))
    return mn.VGroup(*mnodes, *medges).shift(shift)


A_source = r'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F3
    F4
  }
  {
    node [
        fontsize = 12,
        fillcolor = cadetblue1,
        shape = circle,
        style = "filled,rounded",
        height = 0.4,
        width = 0.4,
        fixedsize = true
    ]
    0 [label = "0", shape = box, fixedsize = false]
    1 [label = "1", shape = box, fixedsize = false]
    2 [label = "2", shape = box, fixedsize = false]
    3 [label = "3", shape = box, fixedsize = false]
    4 [label = "4", shape = box, fixedsize = false]
  }
  I0 -> 0
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> 2 [label = "a"]
  2 -> 3 [label = "b"]
  3 -> F3
  3 -> 3 [label = "a"]
  3 -> 4 [label = "b"]
  4 -> F4
  4 -> 3 [label = "a"]
  4 -> 4 [label = "b"]
}
'''

Acomplement_source = r'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F0
    F1
    F2
  }
  {
    node [
        fontsize = 12,
        fillcolor = cadetblue1,
        shape = circle,
        style = "filled,rounded",
        height = 0.4,
        width = 0.4,
        fixedsize = true
    ]
    0
    1
    2
    3 [fillcolor = lightgray]
    4 [fillcolor = lightgray]
  }
  I0 -> 0
  0 -> F0
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> F1
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> F2
  2 -> 2 [label = "a"]
  2 -> 3 [label = "b", color = DimGray]
  3 -> 3 [label = "a", color = DimGray]
  3 -> 4 [label = "b", color = DimGray]
  4 -> 3 [label = "a", color = DimGray]
  4 -> 4 [label = "b", color = DimGray]
}
'''

Acomplement_trim_source = r'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F0
    F1
    F2
  }
  {
    node [
        fontsize = 12,
        fillcolor = cadetblue1,
        shape = circle,
        style = "filled,rounded",
        height = 0.4,
        width = 0.4,
        fixedsize = true
    ]
    0
    1
    2
  }
  I0 -> 0
  0 -> F0
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> F1
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> F2
  2 -> 2 [label = "a"]
}
'''


D_progression = [
r'''
digraph
{
  vcsn_context = "letterset<char_letters(abc)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F4
  }
  {
    node [fontsize = 12, fillcolor = cadetblue1, shape = circle, style = "filled,rounded", height = 0.4, width = 0.4, fixedsize = true]
    0
    1
    2
    3
    4
  }
  I0 -> 0
  0 -> 0 [label = "[^]"]
  0 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> 3 [label = "a"]
  3 -> 4 [label = "b"]
  4 -> F4
}
''',
'''
digraph
{
  vcsn_context = "letterset<char_letters(abc)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F4
  }
  {
    node [fontsize = 12, fillcolor = cadetblue1, shape = circle, style = "filled,rounded", height = 0.4, width = 0.4, fixedsize = true]
    0 [label = "0", shape = box, fixedsize = false]
    1 [label = "0, 1", shape = box, fixedsize = false]
    2 [label = "0, 2", shape = box, fixedsize = false]
    3 [label = "0, 1, 3", shape = box, fixedsize = false]
    4 [label = "0, 2, 4", shape = box, fixedsize = false]
  }
  I0 -> 0
  0 -> 0 [label = "b, c"]
  0 -> 1 [label = "a"]
  1 -> 0 [label = "c"]
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> 0 [label = "b, c"]
  2 -> 3 [label = "a"]
  3 -> 0 [label = "c"]
  3 -> 1 [label = "a"]
  3 -> 4 [label = "b"]
  4 -> F4
  4 -> 0 [label = "b, c"]
  4 -> 3 [label = "a"]
}
''',
'''
digraph
{
  vcsn_context = "letterset<char_letters(abcde)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F4
  }
  {
    node [fontsize = 12, fillcolor = cadetblue1, shape = circle, style = "filled,rounded", height = 0.4, width = 0.4, fixedsize = true]
    0 [label = "0", shape = box, fixedsize = false]
    1 [label = "0, 1", shape = box, fixedsize = false]
    2 [label = "0, 2", shape = box, fixedsize = false]
    3 [label = "0, 1, 3", shape = box, fixedsize = false]
    4 [label = "0, 2, 4", shape = box, fixedsize = false]
  }
  I0 -> 0
  0 -> 0 [label = "[^a]"]
  0 -> 1 [label = "a"]
  1 -> 0 [label = "[c-e]"]
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> 0 [label = "[^a]"]
  2 -> 3 [label = "a"]
  3 -> 0 [label = "[c-e]"]
  3 -> 1 [label = "a"]
  3 -> 4 [label = "b"]
  4 -> F4
  4 -> 0 [label = "[^a]"]
  4 -> 3 [label = "a"]
}
''',
'''
digraph
{
  vcsn_context = "letterset<char_letters(abc)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F4
  }
  {
    node [fontsize = 12, fillcolor = cadetblue1, shape = circle, style = "filled,rounded", height = 0.4, width = 0.4, fixedsize = true]
    0
    1
    2
    3
    4
  }
  I0 -> 0
  0 -> 0 [label = "b, c"]
  0 -> 1 [label = "a"]
  1 -> 0 [label = "c"]
  1 -> 1 [label = "a"]
  1 -> 2 [label = "b"]
  2 -> 0 [label = "b, c"]
  2 -> 3 [label = "a"]
  3 -> 0 [label = "c"]
  3 -> 1 [label = "a"]
  3 -> 4 [label = "b"]
  4 -> F4
  4 -> 0 [label = "b, c"]
  4 -> 3 [label = "a"]
}
'''
]


C_progression = [
'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F3
    F4
  }
  {
    node [shape = circle, style = rounded, width = 0.5]
    0 [label = "1", shape = box]
    1 [label = "2", shape = box]
    2 [label = "4", shape = box]
    3 [label = "3", shape = box]
    4 [label = "5", shape = box]
  }
  I0 -> 0
  0 -> 0 [label = "b"]
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> 3 [label = "a"]
  2 -> 4 [label = "b"]
  3 -> F3
  3 -> 3 [label = "a, b"]
  4 -> F4
  4 -> 4 [label = "a, b"]
}
''',
'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F3
    F4
    F5
    F6
    F7
  }
  {
    node [shape = circle, style = rounded, width = 0.5]
    0 [label = "1", shape = box]
    1 [label = "2", shape = box]
    2 [label = "1, 4", shape = box]
    3 [label = "3", shape = box]
    4 [label = "1, 4, 5", shape = box]
    5 [label = "2, 5", shape = box]
    6 [label = "3, 5", shape = box]
    7 [label = "5", shape = box]
  }
  I0 -> 0
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> 3 [label = "a"]
  2 -> 1 [label = "a"]
  2 -> 4 [label = "b"]
  3 -> F3
  3 -> 3 [label = "a, b"]
  4 -> F4
  4 -> 4 [label = "b"]
  4 -> 5 [label = "a"]
  5 -> F5
  5 -> 6 [label = "a"]
  5 -> 7 [label = "b"]
  6 -> F6
  6 -> 6 [label = "a, b"]
  7 -> F7
  7 -> 7 [label = "a, b"]
}
''',
'''
digraph
{
  vcsn_context = "letterset<char_letters(ab)>, b"
  rankdir = LR
  edge [arrowhead = vee, arrowsize = .6]
  {
    node [shape = point, width = 0]
    I0
    F3
  }
  {
    node [shape = circle, style = rounded, width = 0.5]
    0 [label = "{1}", shape = box]
    1 [label = "{2}", shape = box]
    2 [label = "{1, 4}", shape = box]
    3 [label = "{3}, {1, 4, 5}, {2, 5}, {3, 5}, {5}", shape = box]
  }
  I0 -> 0
  0 -> 1 [label = "a"]
  0 -> 2 [label = "b"]
  1 -> 3 [label = "a"]
  2 -> 1 [label = "a"]
  2 -> 3 [label = "b"]
  3 -> F3
  3 -> 3 [label = "a, b"]
}
'''
]


class Automaton(mn.Scene):
    def construct(self):
        #  mA = dot_to_vgroup(A_source)
        #  mA_complement = dot_to_vgroup(Acomplement_source)
        #  mA_complement_trim = dot_to_vgroup(Acomplement_trim_source)

        #  self.play(mn.ShowCreation(mA))
        #  self.wait()
        #  self.remove(mA)
        #  self.play(mn.Transform(mA, mA_complement))
        #  self.wait()
        #  self.remove(mA)
        #  self.remove(mA_complement)
        #  self.play(mn.Transform(mA_complement, mA_complement_trim))

        #  self.wait()

        mD = dot_to_vgroup(C_progression[0])
        self.play(mn.ShowCreation(mD))
        self.wait()
        self.remove(mD)
        for source in C_progression[1:]:
            next_mD = dot_to_vgroup(source)
            self.play(mn.Transform(mD, next_mD))
            self.wait()
            self.remove(mD)
            self.remove(next_mD)
            mD = next_mD
