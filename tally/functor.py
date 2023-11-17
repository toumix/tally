""" Functor from :class:`Composition` to parameterised quantum circuits. """

from numpy.random import rand
from pytket.extensions.qiskit import AerBackend

from discopy.monoidal import PRO
from discopy.markov import Diagram, Box, Functor, Category
from discopy.quantum import qubit, Ty, Circuit, Discard, Bra, IQPansatz

Diagram.ty_factory = PRO

MAX_ARITY = 3
WIDTH, DEPTH = 1, 3

def ansatz(params):
    n_qubits = params.shape[1] + 1
    left, right = (n_qubits - WIDTH) // 2, (n_qubits - WIDTH + 1) // 2
    return IQPansatz(n_qubits, params)\
        >> Discard(left) @ qubit ** WIDTH @ Discard(right)

boxes = [Box(label, arity, 1)
         for label in "HV" for arity in range(2, MAX_ARITY)]
param_shapes = {box: (DEPTH, len(box.dom) * WIDTH - 1) for box in boxes}
n_params = sum(i * j for i, j in param_shapes.values())

def flatten(box_to_params):
    return np.concatenate([box_to_params[box].flatten() for box in boxes])

def unflatten(params):
    box_to_params, scan = {}, 0
    for box in boxes:
        i, j = param_shapes[box]
        box_to_params[box] = params[scan:][:i * j].reshape(i, j)
        scan += i * j
    return box_to_params

def functor(params):
    box_to_params = unflatten(params)
    return Functor(
        ob={PRO(1): qubit ** WIDTH},
        ar={box: ansatz(box_to_params[box]) for box in boxes},
        cod=Category(Ty, Circuit))

def evaluate(F, composition, backend=None, compilation=None):
    if compilation is None:
        compilation = None if backend is None\
            else backend.default_compilation_pass()
    circuit = F(composition.to_diagram()) >> Bra(*WIDTH * [0])
    return float(circuit.eval(backend=backend, compilation=compilation))
