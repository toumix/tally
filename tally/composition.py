""" Tally composition module. """

from __future__ import annotations

from dataclasses import dataclass

from discopy.monoidal import PRO
from discopy.markov import Box, Diagram

from tally.plot import to_graph, plot


Diagram.ty_factory = PRO


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
    The operator ``|`` does binary :class:`Horizontal` composition while ``&``
    does binary :class:`Vertical` composition, shortened to ``H`` and ``V``.
    """
    terms: tuple[Composition, ...]

    def __init__(self, *terms: Composition):
        self.terms = terms
        assert not self.terms or type(self) in [Horizontal, Vertical]

    def __or__(self, other):
        return Horizontal(self, other)

    def __and__(self, other):
        return Vertical(self, other)

    def __repr__(self):
        if not self.terms:
            return "e"
        if len(self.terms) == 2:
            symbol = '|' if isinstance(self, Horizontal) else '&'
            result = f"{self.terms[0]} {symbol} {self.terms[1]}"
            return f"({result})" if isinstance(self, Horizontal) else result
        return f"{'H' if isinstance(self, Horizontal) else 'V'}{self.terms}"

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


class Horizontal(Composition):
    """
    Horizontal composition, shortened to ``H``.

    Example
    -------
    >>> H(*10 * [e]).plot(path="docs/_static/horizontal.png")

    .. image:: /_static/horizontal.png
        :align: center
    """


class Vertical(Composition):
    """
    Horizontal composition, shortened to ``H``.

    Example
    -------
    >>> V(*10 * [e]).plot(path="docs/_static/vertical.png")

    .. image:: /_static/vertical.png
        :align: center
    """


Composition.to_graph, Composition.plot = to_graph, plot
H, V, e = Horizontal, Vertical, Composition()
