import manimlib.imports as mn
from manimlib.imports import UP, RIGHT, LEFT, DOWN
import numpy as np
import pygraphviz as pgv


class TikzMobject(mn.TextMobject):
    CONFIG = {
        'template_tex_file_body':
            mn.TextMobject.CONFIG["template_tex_file_body"].replace(
                "%\\usepackage[UTF8]{ctex}",
                r"""
                    \usepackage{mathrsfs}
                    \usepackage{tikz}
                    \usetikzlibrary{arrows, shapes.gates.logic.US, shapes.gates.logic.IEC, calc, positioning}
                """
            ),
        'stroke_width': 0.8,
        'fill_opacity': 0
    }


subtractor_detailed_source = r'''
\tikzstyle{branch}=[fill, shape=circle, minimum size=3pt, inner sep=0pt]
\begin{tikzpicture}
    % Input nodes
    \node (a) at (0, 0) {};
    \node (b) at (1, 0) {};
    \node (r) at (2, 0) {};

    % Si nodes
    \node[xor gate US, draw, logic gate inputs=nn] at (3, -1.5) (xorab) {};
    \node[xor gate US, draw, logic gate inputs=nn] at ($(xorab) + (2.5, -1)$) (xorabr) {};

    % Ri nodes
    \node[not gate US, draw] at ($(xorab) + (0, -2.5)$) (nota) {};
    \node[] at ($(nota.output) + (0.5, 0)$) (notafo) {};
    \node[or gate US, draw, logic gate inputs=nn] at ($(nota) + (1.5, -1)$) (orab) {};
    \node[and gate US, draw, logic gate inputs=nn] at ($(orab) + (2.1, -1)$) (andabr) {};
    \node[or gate US, draw, logic gate inputs=nn] at ($(andabr) + (3.1, -1)$) (orrend) {};
    \node[and gate US, draw, logic gate inputs=nn] at (andabr |- orrend.input 2) (andab) {};

    % Outputs nodes
    \node (send) at (15,0 |- xorabr) {};
    \node (rend) at (15,0 |- orrend) {};

    % Si routing
    \draw (a)
        -- (a |- xorab.input 1) node[branch] {}
        -- (xorab.input 1);
    \draw (b)
        -- (b |- xorab.input 2) node[branch] {}
        -- (xorab.input 2);
    \draw (xorab.output)
        -- node[above]{$A_i \oplus B_i$} ($(xorab.output) + (1.3, 0)$)
        |- (xorabr.input 1);
    \draw (r)
        -- (r |- xorabr.input 2) node[branch] {}
        -- (xorabr.input 2);

    %Ri routing
    \draw (a |- xorab.input 1)
        |- (nota.input);
    \draw (nota.output)
        -- node[above]{$\bar A_i$} (notafo.center)
        -- (notafo |- orab.input 1) node[branch] {}
        -- (orab.input 1);
    \draw (b |- xorab.input 2)
        -- (b |- orab.input 2) node[branch] {}
        -- (orab.input 2);
    \draw (notafo |- orab.input 1)
        |- (andab.input 1);
    \draw (b |- orab.input 2)
        |- (andab.input 2);
    \draw (orab.output)
        -- node[above]{$\bar A_i + B_i$} ($(orab.output) + (1.2, 0)$)
        |- (andabr.input 1);
    \draw (r |- xorabr.input 2)
        |- (andabr.input 2);
    \draw (andab.output)
        -- node[above]{$\bar A_i B_i$} (orrend.input 2);
    \draw (andabr.output)
        -- node[above]{$R_{i-1} (\bar A_i + B_i)$} ($(andabr.output) + (2.2, 0)$)
        |- (orrend.input 1);

    % Outputs routing
    \draw (xorabr.output)
        -- node[above]{$A_i \oplus B_i \oplus R_{i-1}$} (send);
    \draw (orrend.output)
        -- node[above]{$R_{i-1} (\bar A_i + B_i) + \bar A_i B_i$} (rend);
\end{tikzpicture}
'''

subtractor_def_source = r'''
\def\sub(#1)#2{%
  \begin{scope}[shift={(#1)}]
    \draw (0,0) rectangle (1.5,2);
    \draw (0.75, 1) node[] {$\mathscr{S}$};
    \draw (0.75,2) node[below] {} -- +(0,0.25) coordinate (#2 Ri);
    \draw (0,1.25) node[right] {} -- +(-0.25,0) coordinate (#2 A);
    \draw (0,0.5) node[right] {} -- +(-0.25,0) coordinate (#2 B);
    \draw (1.5,1.25) node[left] {} -- +(0.25,0) coordinate (#2 S);
    \draw (1.5,0.5) node[left] {} -- +(0.25,0) coordinate (#2 Ro);
  \end{scope}
}
'''

subtractor_source = subtractor_def_source + r'''
\begin{tikzpicture}
    \sub (0, 0) {a}
\end{tikzpicture}
'''


class Tikz(mn.Scene):
    def construct(self):
        # Detailed design of the subtractor
        sub_wiring = TikzMobject(subtractor_detailed_source).scale(0.5)
        input_a = mn.TexMobject("A_i") \
            .move_to(sub_wiring.get_center() + 2.8 * UP + 5.3 * LEFT)
        input_b = mn.TexMobject("B_i").next_to(input_a, mn.RIGHT)
        input_r = mn.TexMobject("R_{i-1}").next_to(input_b, mn.RIGHT)
        output_s = mn.TexMobject("S_i") \
            .move_to(sub_wiring.get_center() + 5.7 * RIGHT + 0.9 * UP)
        output_r = mn.TexMobject("R_i") \
            .move_to(sub_wiring.get_center() + 5.7 * RIGHT + 2.3 * DOWN)
        sub_detailed = mn.VGroup(sub_wiring, input_a, input_b, input_r,
                                    output_s, output_r)

        self.play(mn.ShowCreation(sub_detailed))
        self.wait()

        # Simplfied symbol for the subtractor
        sub_symbol = TikzMobject(subtractor_source)
        input_a = mn.TexMobject("A_i") \
            .move_to(sub_symbol.get_center() + 0.7 * LEFT + 0.2 * UP)
        input_b = mn.TexMobject("B_i") \
            .move_to(input_a.get_center() + 1.1 * DOWN)
        input_r = mn.TexMobject("R_{i-1}") \
            .move_to(sub_symbol.get_center() + 0.9 * UP)
        output_s = mn.TexMobject("S_i") \
            .move_to(sub_symbol.get_center() + 0.7 * RIGHT + 0.2 * UP)
        output_r = mn.TexMobject("R_i") \
            .move_to(output_s.get_center() + 1.1 * DOWN)
        sub = mn.VGroup(sub_symbol, input_a, input_b, input_r,
                           output_s, output_r)

        self.play(mn.Transform(sub_detailed, sub))
        self.wait()

        # Draw the four subtractors
        sub1 = sub.copy().scale(0.3).move_to(2.5*UP)
        self.remove(sub_detailed)  # why is it needed?
        self.play(mn.Transform(sub, sub1))
        sub2 = sub1.copy().next_to(sub1, DOWN)
        sub3 = sub2.copy().next_to(sub2, DOWN)
        sub4 = sub3.copy().next_to(sub3, DOWN)
        subs = [sub1, sub2, sub3, sub4]
        self.play(*[mn.ShowCreation(obj) for obj in subs[1:]])

        # Link them
        links = []
        for i in range(3):
            src = subs[i]
            dst = subs[i+1]
            down = mn.Line(
                src.get_center() + 0.43*RIGHT + 0.26*DOWN,
                dst.get_center() + 0.43*RIGHT + 0.48*UP,
                stroke_width=0.8
            )
            left = mn.Line(
                dst.get_center() + 0.43*RIGHT + 0.48*UP,
                dst.get_center() + 0.48*UP,
                stroke_width=0.8
            )
            links.append(mn.VGroup(down, left))
        self.play(*[mn.ShowCreation(link) for link in links])

        # Link inputs
        r0 = mn.TextMobject("0") \
            .scale(0.3) \
            .move_to(sub1.get_center() + 0.7 * UP)
        r0_line = mn.Line(
            sub1.get_center() + 0.47*UP,
            sub1.get_center() + 0.63*UP,
            stroke_width=0.8
        )
        inputs = [r0, r0_line]
        for sub in subs:
            ai_line = mn.Line(
                sub.get_center() + 0.42*LEFT + 0.05*UP,
                sub.get_center() + LEFT + 0.05*UP,
                stroke_width=0.8
            )
            ai = mn.TexMobject(f"A_{i}").scale(0.3).next_to(ai_line, LEFT)
            inputs.append(mn.VGroup(ai_line, ai))

            bi_line = mn.Line(
                sub.get_center() + 0.42*LEFT + 0.265*DOWN,
                sub.get_center() + LEFT + 0.265*DOWN,
                stroke_width=0.8
            )
            bi = mn.TexMobject(f"B_{i}").scale(0.3).next_to(bi_line, LEFT)
            inputs.append(mn.VGroup(bi_line, bi))

        self.play(*[mn.ShowCreation(obj) for obj in inputs])

        # Link outputs
        outputs = []
        for sub in subs:
            si_line = mn.Line(
                sub.get_center() + 0.42*RIGHT + 0.05*UP,
                sub.get_center() + RIGHT + 0.05*UP,
                stroke_width=0.8
            )
            si = mn.TexMobject(f"S_{i}").scale(0.3).next_to(si_line, RIGHT)
            outputs.append(mn.VGroup(si_line, si))

        self.play(*[mn.ShowCreation(obj) for obj in outputs])

        complete_sub = mn.VGroup(*subs, *links, *inputs, *outputs)
        self.play(mn.ApplyMethod(complete_sub.shift, 2*LEFT + 0.5*DOWN))

        # Draw a subtraction
        a = [
            mn.TexMobject("5").move_to(subs[1].get_center() + 4*RIGHT),
            mn.TexMobject("6").move_to(subs[1].get_center() + 4.5*RIGHT),
            mn.TexMobject("3").move_to(subs[1].get_center() + 5*RIGHT),
            mn.TexMobject("1").move_to(subs[1].get_center() + 5.5*RIGHT)
        ]
        b = [
            mn.TexMobject("3").move_to(subs[1].get_center() + 0.5*DOWN + 4*RIGHT),
            mn.TexMobject("8").move_to(subs[1].get_center() + 0.5*DOWN + 4.5*RIGHT),
            mn.TexMobject("4").move_to(subs[1].get_center() + 0.5*DOWN + 5*RIGHT),
            mn.TexMobject("6").move_to(subs[1].get_center() + 0.5*DOWN + 5.5*RIGHT)
        ]
        minus_sign = mn.TexMobject("-").next_to(b[0], LEFT)
        separator = mn.Line(
            minus_sign.get_center() + 0.5*LEFT + 0.5*DOWN,
            b[-1].get_center() + 0.5*RIGHT + 0.5*DOWN
        )
        subtraction = mn.VGroup(*a, *b, minus_sign, separator)
        self.play(mn.ShowCreation(subtraction))
        self.wait(5)
