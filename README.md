# tally

Tally is a tool for the quantum-enhanced composition of generative art.

```python
from tally import H, V, e

composition = V(e, e, e) | e & H(e, e & e)

composition.draw()
```

![composition](docs/_static/example.png)

```python
composition.to_diagram().draw()
```

![composition](docs/_static/diagram.png)
