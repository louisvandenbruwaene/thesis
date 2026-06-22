# Defence slides

A short, visual Beamer deck for the thesis defence of *Erdős Problem 915, from
Proof to Search*. It reuses the thesis house style (`../shared/colors.tex` and
`../shared/tikz-styles.tex`) and pulls a few plots from `../figures/`.

## Build

```bash
cd slides
latexmk -pdf slides.tex
```

The built deck is `slides.pdf`.

## Structure (the red wire)

1. Title
2. A hard problem is a wall (around, through, over)
3. Three ways past the wall: proof, calculation, approximation
4. The road of a research problem
5. Problem 915, precisely (graph, connectivity, the rule, Mader)
6. What is it good for (the methods outlive the result)
7. One question, twelve variants
8. Edge routes versus vertex routes (the k versus l divergence)
9. What fell, and how hard
10. How the machine works (annealing vs tabu, Python vs C)
11. Results on the directed frontier
12. The whole landscape (the twelve-variant table)
13. What is left, and why it matters

After the closing slide there are backup slides, one per topic, to dive deeper
during the question round: the directed arc conjecture, the hypergraph vertex
problem, the n=7 reduction, the Gomory-Hu storage trick, and a values
cheat-sheet.
