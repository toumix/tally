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
from dataclasses import dataclass, asdict

from discopy.monoidal import PRO
from discopy.markov import Box, Diagram

from tally.draw import to_graph, draw


Diagram.ty_factory = PRO

class Label(str, Enum):
    Horizontal = 'H'
    Vertical = 'V'
    Empty = 'e'

Horizontal, Vertical, Empty = Label

Label.__call__ = lambda self, *terms: Composition(*terms, label=self)

@dataclass(frozen=True)
class Composition:
    """
    A composition is a list of terms, which are themselves compositions.

    Parameters:
        terms : The terms of the composition.
        label : Either `Horizontal`, `Vertical` or `Empty`.

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
                or not terms and label == Empty)
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
            return self.label.value
        if len(self.terms) == 2:
            symbol = '|' if self.label == Horizontal else '&'
            return f"({self.terms[0]} {symbol} {self.terms[1]})"
        return f"{self.label.value}{self.terms}"

    @property
    def depth(self):
        return max([0] + [t.depth + 1 for t in self.terms])

    @property
    def max_arity(self):
        return max([len(self.terms)] + [t.max_arity for t in self.terms])

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
        return Box(self.label.value, len(self.terms), 1)\
            << Diagram.id().tensor(*(term.to_diagram() for term in self.terms))

    def save(self, path):
        with open(path, "w+") as file:
            file.write(json.dumps(asdict(self)))

    @staticmethod
    def load(path):
        with open(path, "r") as file:
            return Composition.from_dict(json.loads(file.read()))

    @staticmethod
    def from_dict(tree):
        return Label(tree['label'])(*map(Composition.from_dict, tree['terms']))

    @staticmethod
    def random(seed=None, max_trials=10, prob_empty=.25,
               min_depth=2, max_depth=4, max_arity=3):
        """
        Generate a random composition.

        Parameters:
            seed : Random seed.
            max_trials : Raise if too many failures.
            prob_empty : Probability of generating an empty composition.
            min_depth : Minimum depth of a composition.
            max_depth : Maximum depth of a composition.
            max_arity : Maximum number of terms at each level.

        Example
        -------
        >>> Composition.random(seed=42).draw(path="docs/_static/random.png")

        .. image:: /_static/random.png
            :center:
        """
        if seed is not None:
            random.seed(seed)
        if not max_depth or not min_depth and random.random() <= prob_empty:
            return Composition()
        for trial in range(max_trials):
            cls, n_terms = map(random.choice, (
                [Horizontal, Vertical], range(2, max_arity)))
            result = cls(*[Composition.random(
                    seed=None if seed is None else hash((seed, i, trial)),
                    min_depth=None,
                    max_depth=max_depth - 1,
                    prob_empty=prob_empty) for i in range(n_terms)])
            if result.max_arity > max_arity or result.depth < (min_depth or 0):
                continue
            return result
        raise RuntimeError


Composition.to_graph, Composition.draw = to_graph, draw
H, V, e = Horizontal, Vertical, Empty()
