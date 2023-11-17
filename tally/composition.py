""" Tally composition module. """

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from discopy.monoidal import PRO
from discopy.markov import Box, Diagram

from tally.draw import to_graph, draw


Diagram.ty_factory = PRO


@dataclass(frozen=True)
class Composition:
    """
    A composition is a list of terms, which are themselves compositions.

    Parameters:
        terms : The terms of the composition.

    Note
    ----
    Compositions are either empty, :class:`Horizontal` or  :class:`Vertical`.
    The composition ``e`` with an empty list of terms is drawn as just a frame.
    The operator ``|`` does binary :class:`Horizontal` composition while ``&``
    does binary :class:`Vertical` composition, shortened to ``H`` and ``V``.
    """
    terms: tuple[Composition, ...]

    def __new__(cls, *terms: Composition):
        classes = set(type(t) for t in terms)
        lengths = set(len(t.terms) for t in terms)
        if (len(classes) == len(lengths) == 1
                and (cls, classes.pop()) == (Horizontal, Vertical)):
            return Vertical(*[Horizontal(*[
                    terms[j].terms[i] for j in range(len(terms))])
                for i in range(lengths.pop())])
        return object.__new__(cls)

    def __init__(self, *terms: Composition):
        assert not terms or type(self) in [Horizontal, Vertical]
        classes = set(type(t) for t in terms)
        lengths = set(len(t.terms) for t in terms)
        if len(classes) == len(lengths) == 1 and classes.pop() == type(self):
            terms = tuple(sum([t.terms for t in terms], ()))
        object.__setattr__(self, "terms", terms)

    def __or__(self, other):
        return Horizontal(self, other)

    def __and__(self, other):
        return Vertical(self, other)

    def __repr__(self):
        if not self.terms:
            return "e"
        if len(self.terms) == 2:
            symbol = '|' if isinstance(self, Horizontal) else '&'
            return f"({self.terms[0]} {symbol} {self.terms[1]})"
        return f"{'H' if isinstance(self, Horizontal) else 'V'}{self.terms}"

    @property
    def depth(self):
        return max([0] + [t.depth + 1 for t in self.terms])

    @classmethod
    def rotate(cls):
        if cls is Horizontal:
            return Vertical
        if cls is Vertical:
            return Horizontal
        return Composition

    def rotate(self):
        return type(self).rotate(*[t.rotate() for t in self.terms])

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
        name = 'H' if isinstance(self, Horizontal) else 'V'
        return Box(name, len(self.terms), 1) << Diagram.id().tensor(*(
            term.to_diagram() for term in self.terms))

    def to_dict(self):
        return {'label': 'e'} if not self.terms else {
            'label': 'H' if isinstance(self, Horizontal) else 'V',
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

Composition.to_graph, Composition.draw = to_graph, draw
H, V, e = Horizontal, Vertical, Composition()
