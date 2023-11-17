# """ Functor from :class:`Composition` to parameterised quantum circuits. """

# from numpy.random import rand, seed; seed(42)

# from discopy.monoidal import PRO
# from discopy.markov import Box, Functor, Category
# from discopy.quantum import (
#     qubit, Ty, Circuit, Discard, Measure, IQPansatz, Bits)

# DEPTH = 1

# def ansatz(n_qubits, params):
#     return IQPansatz(n_qubits, params)\
#         >> Discard((n_qubits - 1) // 2) @ qubit @ Discard(n_qubits // 2)

# params0 = rand(6)

# F = lambda params: Functor(
#     ob={PRO(1): qubit},
#     ar={Box('H', 3, 1): ansatz(3, params[0:2].reshape(1, 2)),
#         Box('V', 3, 1): ansatz(3, params[2:4].reshape(1, 2)),
#         Box('H', 2, 1): ansatz(2, params[4:5].reshape(1, 1)),
#         Box('V', 2, 1): ansatz(2, params[5:6].reshape(1, 1))},
#     cod=Category(Ty, Circuit))

# F0 = F(params0)

# circuit = F0(diagram) >> Measure() >> Bits(0)[::-1]
# backend = AerBackend()

# evaluate = lambda F, composition: float((
#     F(composition.to_diagram()) >> Measure() >> Bits(0)[::-1]).eval(
#         backend=backend, compilation=backend.default_compilation_pass()))

# evaluate(F0, composition)
# from time import time
# import numpy as np
# import noisyopt

# i, start, losses = 0, time(), []

# def callback(params):
#     global i
#     i += 1
#     losses.append(loss(params))
#     print("Step {}: {}".format(i, params))

# def loss(params):
#     return np.mean(np.array([
#         (value - evaluate(F(params), composition)) ** 2
#         for composition, value in data.items()]))

# experiment = noisyopt.minimizeSPSA(
#     loss, params0, paired=False, callback=callback, niter=21)
# experiment
