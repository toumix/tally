""" Tally is a tool for the quantum-enhanced composition of generative art. """

from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple

import matplotlib.pyplot as plt
import networkx as nx
from discopy.monoidal import PRO
from discopy.cartesian import Box, Diagram


Diagram.ty_factory = PRO


class PlaneGraph(NamedTuple):
    """
    A plane graph is a graph with a mapping from nodes to planar coordinates.
    """
    graph: nx.Graph
    position: dict[int, tuple[float, float]]


PlaneGraph.position.__doc__ = "The mapping from nodes to planar coordinates."
PlaneGraph.graph.__doc__ = "The graph."


@dataclass
class Composition:
    """
    A composition is a list of terms, which are themselves compositions.

    Parameters:
        terms : The terms of the composition.

    Note
    ----
    Compositions are either empty, :class:`Horizontal` or  :class:`Vertical`.
    The composition ``e`` with an empty list of terms is drawn as just a frame.
    The operator ``&`` does binary :class:`Horizontal` composition while ``|``
    does binary :class:`Vertical` composition, shortened to ``H`` and ``V``.
    """
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

    def to_diagram(self) -> Diagram:
        """
        Encode a composition as a DisCoPy diagram.

        Example
        -------
        >>> composition = H(e, e, e) | e & (e | e & e)
        >>> composition.to_diagram().draw(path="docs/_static/diagram.png")

        .. image:: /_static/diagram.png
            :center:
        """
        if not self.terms:
            return Diagram.id(1)
        name = 'H' if isinstance(self, Horizontal) else 'V'
        return Box(name, len(self.terms), 1) << Diagram.id().tensor(*(
            term.to_diagram() for term in self.terms))


    def to_graph(self) -> PlaneGraph:
        """
        Compile a composition as a graph with positions in the unit square.
        """
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

    def draw(self, path: Optional[str] = None, figsize=(5, 5)) -> None:
        """
        Draw a composition with matplotlib.

        Parameters:
            path : Optional file path, if ``None`` then call ``plt.show()``.
            figsize : Passed to ``plt.figure``.

        Example
        -------
        >>> composition = H(e, e, e) | e & (e | e & e)
        >>> composition.draw(path="docs/_static/example.png")

        .. image:: /_static/example.png
            :align: center
        """
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
    """
    Horizontal composition, shortened to ``H``.

    Example
    -------
    >>> H(*10 * [e]).draw(path="docs/_static/horizontal.png")

    .. image:: /_static/horizontal.png
        :align: center
    """


class Vertical(Composition):
    """
    Horizontal composition, shortened to ``H``.

    Example
    -------
    >>> V(*10 * [e]).draw(path="docs/_static/vertical.png")

    .. image:: /_static/vertical.png
        :align: center
    """


H, V, e = Horizontal, Vertical, Composition()

__version__ = '0.0.1'
