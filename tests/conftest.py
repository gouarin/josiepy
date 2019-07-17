import pytest

from josie.bc import make_periodic, Direction, Neumann
from josie.geom import Line, CircleArc
from josie.mesh import Mesh
from josie.solver.state import StateTemplate


def pytest_addoption(parser):
    parser.addoption(
        "--plot", action="store_true", help="Some tests can plot the mesh. "
        "Set to true if you want to see them"
    )


@pytest.fixture
def Q():
    yield StateTemplate("u")


@pytest.fixture
def boundaries(Q):
    left = Line([0, 0], [0, 1])
    # bottom = CircleArc([0, 0], [1, 0], [0.2, 0.2])
    bottom = Line([0, 0], [1, 0])
    right = Line([1, 0], [1, 1])
    top = Line([0, 1], [1, 1])

    left, right = make_periodic(left, right, Direction.X)
    bottom, top = make_periodic(bottom, top, Direction.Y)

    yield (left, bottom, right, top)


@pytest.fixture
def mesh(boundaries):
    left, bottom, right, top = boundaries

    mesh = Mesh(left, bottom, right, top)
    mesh.interpolate(20, 20)
    mesh.generate()

    yield mesh


@pytest.fixture
def plot(request):
    return request.config.getoption("--plot")


@pytest.fixture
def tol():
    yield 1E-12
