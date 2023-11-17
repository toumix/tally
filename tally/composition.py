"""
Tally composition module.

Example
-------
>>> composition = V(e, e, e) | e & H(e, e & e)
>>> composition.draw(path="docs/_static/example.png")

.. image:: /_static/example.png
    :align: center
"""

from __future__ import annotations

import json
import random
from enum import Enum
from dataclasses import dataclass

from discopy.monoidal import PRO
from discopy.markov import Box, Diagram

from tally.draw import to_graph, draw


Diagram.ty_factory = PRO

Label = Enum('Label', ['Horizontal', 'Vertical', 'Empty'])
Horizontal, Vertical, Empty = Label

Label.__call__ = lambda self, *terms: Composition(*terms, label=self)

@dataclass(frozen=True)
class Composition:
    """
    A composition is a list of terms, which are themselves compositions.

    Parameters:
        label : Either `Horizontal`, `Vertical` or `Empty`.
        terms : The terms of the composition.

    Note
    ----
    The composition ``e`` with an empty list of terms is drawn as just a frame.
    The operator ``|`` does binary `Horizontal` composition while ``&``
    does binary `Vertical` composition, shortened to ``H`` and ``V``.

    Examples
    --------
    >>> assert H(H(e, e), H(e, e), H(e, e))\\
    ...     == H(e, e, e, e, e, e)\\
    ...     == H(H(e, e, e), H(e, e, e))
    >>> H(*6 * [e]).draw(path="docs/_static/horizontal.png")

    .. image:: /_static/horizontal.png
        :align: center

    >>> assert V(V(e, e), V(e, e), V(e, e))\\
    ...     == V(e, e, e, e, e, e)\\
    ...     == V(V(e, e, e), V(e, e, e))
    >>> V(*6 * [e]).draw(path="docs/_static/vertical.png")

    .. image:: /_static/vertical.png
        :align: center

    >>> assert V(H(e, e), H(e, e), H(e, e))\\
    ...     == H(V(e, e, e), V(e, e, e))
    >>> H(V(e, e, e), V(e, e, e)).draw(path="docs/_static/two-by-three.png")

    .. image:: /_static/two-by-three.png
        :align: center

    >>> assert H(V(e, e), V(e, e), V(e, e))\\
    ...     == V(H(e, e, e), H(e, e, e))
    >>> V(H(e, e, e), H(e, e, e)).draw(path="docs/_static/three-by-two.png")

    .. image:: /_static/three-by-two.png
        :align: center
    """
    terms: tuple[Composition, ...]
    label: Label

    def __init__(self, *terms: Composition, label: Label = Empty):
        assert (terms and label in [Horizontal, Vertical]
                or not terms and label is Empty)
        labels = set(t.label for t in terms)
        lengths = set(len(t.terms) for t in terms)
        if len(labels) == len(lengths) == 1:
            label_of_each, length_of_each = labels.pop(), lengths.pop()
            if label == label_of_each:
                terms = tuple(sum([t.terms for t in terms], ()))
            if (label, label_of_each) == (Horizontal, Vertical):
                label = Vertical
                terms = tuple(
                    Horizontal(*[terms[j].terms[i] for j in range(len(terms))])
                    for i in range(length_of_each))
        object.__setattr__(self, "terms", terms)
        object.__setattr__(self, "label", label)

    def __or__(self, other):
        return Horizontal(self, other)

    def __and__(self, other):
        return Vertical(self, other)

    def __repr__(self):
        if not self.terms:
            return "e"
        if len(self.terms) == 2:
            symbol = '|' if self.label is Horizontal else '&'
            return f"({self.terms[0]} {symbol} {self.terms[1]})"
        return f"{'H' if self.label is Horizontal else 'V'}{self.terms}"

    @property
    def depth(self):
        return max([0] + [t.depth + 1 for t in self.terms])

    def to_diagram(self) -> Diagram:
        """
        Encode a composition as a DisCoPy diagram.

        Example
        -------
        >>> composition = V(e, e, e) | e & H(e, e & e)
        >>> composition.to_diagram().draw(path="docs/_static/diagram.png")

        .. image:: /_static/diagram.png
            :center:
        """
        if not self.terms:
            return Diagram.id(1)
        name = 'H' if self.label is Horizontal else 'V'
        return Box(name, len(self.terms), 1) << Diagram.id().tensor(*(
            term.to_diagram() for term in self.terms))

    def to_dict(self):
        return {'label': 'e'} if not self.terms else {
            'label': 'H' if self.label is Horizontal else 'V',
            'terms': [t.to_dict() for t in self.terms]}

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def random(seed=None, min_depth=2, max_depth=4, prob_empty=.25):
        if seed is not None:
            random.seed(seed)
        if not max_depth or not min_depth and random.random() <= prob_empty:
            return Composition()
        while True:
            cls, n_terms = map(random.choice, ([Horizontal, Vertical], [2, 3]))
            result = cls(*[Composition.random(
                    seed=None if seed is None else seed + i,
                    min_depth=None,
                    max_depth=max_depth - 1,
                    prob_empty=prob_empty) for i in range(n_terms)])
            if min_depth is None or result.depth >= min_depth:
                return result


Composition.to_graph, Composition.draw = to_graph, draw
H, V, e = Horizontal, Vertical, Empty()
