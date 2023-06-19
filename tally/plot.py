""" Tally plotting module. """

from __future__ import annotations

from typing import NamedTuple

import networkx as nx
import matplotlib.pyplot as plt


class PlaneGraph(NamedTuple):
    """
    A plane graph is a graph with a mapping from nodes to planar coordinates.
    """
    graph: nx.Graph
    position: dict[int, tuple[float, float]]


PlaneGraph.position.__doc__ = "The mapping from nodes to planar coordinates."
PlaneGraph.graph.__doc__ = "The graph."


def to_graph(composition: Composition) -> PlaneGraph:
    """
    Compile a composition as a graph with positions in the unit square.
    """
    from tally.composition import Horizontal
    if not composition.terms:
        graph = nx.Graph(zip(range(4), [1, 2, 3, 0]))
        position = dict(enumerate([
            (0., 0.), (0., 1.), (1., 1.), (1., 0.)]))
        return graph, position
    graph, position, n_terms = nx.Graph(), dict(), len(composition.terms)
    for i, (G, p) in enumerate([term.to_graph() for term in composition.terms]):
        for v, (x, y) in p.items():
            if isinstance(composition, Horizontal):
                position[v + len(graph)] = ((i + x) / n_terms, y)
            else:
                position[v + len(graph)] = (x, 1 - (i + y) / n_terms)
        graph = nx.disjoint_union(graph, G)
    return graph, position


def plot(composition: Composition,
         path: Optional[str] = None, figsize=(5, 5)) -> None:
    """
    Plot a composition with matplotlib.

    Parameters:
        path : Optional file path, if ``None`` then call ``plt.show()``.
        figsize : Passed to ``plt.figure``.

    Example
    -------
    >>> composition = V(e, e, e) | e & H(e, e & e)
    >>> composition.plot(path="docs/_static/example.png")

    .. image:: /_static/example.png
        :align: center
    """
    plt.figure(figsize=figsize)
    graph, position = to_graph(composition)
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
