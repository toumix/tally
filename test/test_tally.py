import os
from matplotlib.testing.compare import compare_images
from tally import H, V, e


def test_repr():
    composition = H(e, e, e) | e & (e | e & e)
    assert repr(composition) == "(H(e, e, e) | (e & (e | (e & e))))"


def test_draw(true_path="docs/_static/example.png", tol=10):
    composition = V(e, e, e) | e & H(e, e & e)
    folder, filename = os.path.split(true_path)
    test_path = os.path.join(folder, "." + filename)
    composition.draw(path=test_path)
    test = compare_images(true_path, test_path, 10)
    assert test is None
    os.remove(test_path)

def test_json(true_path="test/example.json"):
    composition = V(e, e, e) | e & H(e, e & e)
    folder, filename = os.path.split(true_path)
    test_path = os.path.join(folder, "." + filename)
    composition.save(test_path)
    assert composition.load(test_path)\
        == composition.load(true_path) == composition
    os.remove(test_path)
