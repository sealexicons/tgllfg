# tgllfg/examples/demo.py

from tgllfg.pipeline import parse_text
from tgllfg.renderers import render_c, render_f, render_a

if __name__ == "__main__":
    text = "Kinain ng aso ang isda."
    results = parse_text(text)
    for (ctree, f, a, diags) in results:
        print("# c-structure")
        print(render_c(ctree))
        print("# f-structure")
        print(render_f(f))
        print("# a-structure")
        print(render_a(a))