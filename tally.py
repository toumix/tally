from __future__ import annotations
from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx


@dataclass
class Composition:
    terms: tuple[Composition, ...]

    def __init__(self, *terms: Composition):
        self.terms = terms
        assert not self.terms or type(self) in [Horizontal, Vertical]

    def __or__(self, other):
        return Vertical(self, other)

    def __and__(self, other):
        return Horizontal(self, other)

    def __repr__(self):
        if not self.terms:
            return "e"
        if len(self.terms) == 2:
            symbol = '&' if isinstance(self, Horizontal) else '|'
            result = f"{self.terms[0]} {symbol} {self.terms[1]}"
            return result if isinstance(self, Horizontal) else f"({result})"
        return f"{'H' if isinstance(self, Horizontal) else 'V'}{self.terms}"

    def to_graph(self):
        if not self.terms:
            graph = nx.Graph(zip(range(4), [1, 2, 3, 0]))
            position = dict(enumerate([
                (0., 0.), (0., 1.), (1., 1.), (1., 0.)]))
            return graph, position
        graph, position, n_terms = nx.Graph(), dict(), len(self.terms)
        for i, (G, p) in enumerate([term.to_graph() for term in self.terms]):
            for v, (x, y) in p.items():
                if isinstance(self, Horizontal):
                    position[v + len(graph)] = (x, 1 - (i + y) / n_terms)
                else:
                    position[v + len(graph)] = ((i + x) / n_terms, y)
            graph = nx.disjoint_union(graph, G)
        return graph, position

    def draw(self, path=None, figsize=(5, 5)):
        plt.figure(figsize=figsize)
        graph, position = self.to_graph()
        nx.draw_networkx(graph, pos=position, with_labels=False, node_size=0)
        plt.tight_layout()
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.margins(0)
        plt.gca().set_aspect('equal')
        if path is None:
            plt.show()
        else:
            plt.savefig(path)
            plt.close()


class Horizontal(Composition):
    pass


class Vertical(Composition):
    pass


H, V, e = Horizontal, Vertical, Composition()
