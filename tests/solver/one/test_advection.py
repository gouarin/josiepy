import matplotlib.pyplot as plt
import numpy as np
import pytest

from matplotlib.animation import ArtistAnimation
from numba import njit

from .adv1d import main as main_1d

from josie.solver.state import StateTemplate
from josie.solver.solver import Solver
from josie.solver.scheme import Scheme as AbstractScheme


# Advection velocity in x-direction
V = np.array([1.0, 0.0])


def upwind(
    values: np.ndarray,
    neigh_values: np.ndarray,
    normals: np.ndarray,
    surfaces: np.ndarray,
):
    def flux(state_array: np.ndarray) -> np.ndarray:
        # I multiply each element of the given state array by the velocity
        # vector. I obtain an Nx2 array where each row is the flux on each
        # cell
        return V * state_array[:, np.newaxis]

    F = np.zeros_like(values)

    # I do a dot product of each normal in `norm` by the advection velocity
    # Equivalent to: un = np.sum(Advection.V*(normals), axis=-1)
    un = np.einsum("ijk,jk->ij", normals, V[np.newaxis, :])

    # Check where un > 0
    un_positive = np.all(un > 0)

    # Here the einsum is equivalent to a dot product element by element
    # of flux and norm
    if un_positive:
        F = F + np.einsum("ijkl,ijl->ijk", flux(values), normals)
    else:
        F = F + np.einsum("ijkl,ijl->ijk", flux(neigh_values), normals)

    FS = np.einsum("ijk,ik->ij", F, surfaces)

    return FS[:, np.newaxis, :]


@njit(cache=True)
def upwind_jit(
    values: np.ndarray,
    neigh_values: np.ndarray,
    normals: np.ndarray,
    surfaces: np.ndarray,
):
    def flux(state):
        # I multiply each element of the given state array by the velocity
        # vector. I obtain an Nx2 array where each row is the flux on each
        # cell

        return V * (state)

    F = np.zeros_like(values)

    # Loop over cell in x and y
    num_cells_x, num_cells_y, state_size = values.shape
    for i in np.arange(num_cells_x):
        for j in np.arange(num_cells_y):
            norm = normals[i, j]
            un = V.dot(norm)

            if un > 0:
                F[i, j] = (
                    F[i, j] + flux(values[i, j]).dot(norm) * surfaces[i, j]
                )
            else:
                F[i, j] = (
                    F[i, j]
                    + flux(neigh_values[i, j]).dot(norm) * surfaces[i, j]
                )

    return F


@pytest.fixture
def Q():
    yield StateTemplate("u")


@pytest.fixture
def solver(mesh, init_fun, Q):
    mesh.interpolate(1000, 1)
    mesh.generate()
    solver = Solver(mesh, Q)
    solver.init(init_fun)

    yield solver


@pytest.fixture(params=[upwind, upwind_jit])
def Scheme(request):
    class Upwind(AbstractScheme):
        def convective_flux(
            self,
            values: np.ndarray,
            neigh_values: np.ndarray,
            normals: np.ndarray,
            surfaces: np.ndarray,
        ):
            return request.param(values, neigh_values, normals, surfaces)

        def CFL(
            self,
            values: np.ndarray,
            volumes: np.ndarray,
            normals: np.ndarray,
            surfaces: np.ndarray,
            CFL_value: float,
        ) -> float:

            U_abs = np.linalg.norm(V)
            dx = np.min(surfaces)

            return CFL_value * dx / U_abs

    yield Upwind


def test_against_real_1D(solver, Scheme, plot, tol):
    """ Testing against the real 1D solver """

    time, x_1d, solution = main_1d(1000, 4, 0.9, plot)
    dt = time[1] - time[0]

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ims = []

    upwind = Scheme()

    for i, t in enumerate(time):
        x = solver.mesh.centroids[:, :, 0]
        x = x.reshape(x.size)
        u = solver.values[:, :, 0]
        u = u.reshape(u.size)

        err = u - solution[i, :]

        if plot:
            im1, = ax1.plot(x, u, "ro-")
            im2, = ax1.plot(x_1d, solution[i, :], "ks-")
            ims.append([im1, im2])
            im_err, = ax2.plot(x_1d, err, "ks-")
            ims.append([im1, im2, im_err])

        # Check same solution with 1D-only
        # assert np.sum(err < tol) == len(x)
        solver.step(dt, upwind)

    if plot:
        _ = ArtistAnimation(fig, ims, interval=50)
        plt.show()
