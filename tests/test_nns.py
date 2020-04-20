import pytest
import numpy as np
from vincenty_cuda_nns import CudaTree

from .utils import brute_force

DATASET_SIZES = [10**n for n in range(3)]


def process_array(array):
    distances, indices = brute_force(array)

    cuda_tree = CudaTree(array, leaf_size=5)
    cuda_dist, cuda_ind = cuda_tree.query(n_neighbors=2)

    assert np.allclose(cuda_dist[:, 1], distances, atol=1)

    if not (array[0] == array[:]).all():
        assert (cuda_ind[:, 1] == indices).all()


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_distances(size):
    X = (np.random.random((size, 2)) * 180) - 90
    process_array(X)


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_zero_meredian(size):
    X = (np.random.random((size, 2)) * 180) - 90
    X[::2, 0] = 0
    process_array(X)


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_180_meredian(size):
    X = (np.random.random((size, 2)) * 180) - 90
    X[::3, 0] = 180
    X[1::3, 0] = -180
    process_array(X)


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_poles(size):
    X = (np.random.random((size, 2)) * 180) - 90
    X[::3, 0] = 90
    X[1::3, 0] = -90
    process_array(X)


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_zeros(size):
    X = np.zeros((size, 2))
    process_array(X)


@pytest.mark.parametrize('size', DATASET_SIZES)
def test_changed_array(size):
    X = (np.random.random((size, 2)) * 180) - 90
    distances, indices = brute_force(X)

    cuda_tree = CudaTree(X, leaf_size=5)

    X[:, :] = 0

    cuda_dist, cuda_ind = cuda_tree.query(n_neighbors=2)

    assert np.allclose(cuda_dist[:, 1], distances, atol=1)
    assert (cuda_ind[:, 1] == indices).all()
