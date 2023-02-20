import random

import numpy as np
import pandas as pd

from algoritmos.utilidades.common import obtain_train_unlabelled
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_pca_reduction, log_cxcy_reduction

import pytest


def test_obtain_train_unlabelled():
    data = (np.array([[i, i] for i in range(5)]), np.array([-1, 1, -1, 2, 0]))

    # Cuando i = 0 e i = 2 es un dato no etiquetado
    expected = (np.array([[1, 1], [3, 3], [4, 4]]), [1, 2, 0], np.array([[0, 0], [2, 2]]))
    #          -------------x_train--------------   -y_train-  ---------unlabelled-------

    x_train, y_train, x_u = obtain_train_unlabelled(data[0], data[1])

    assert (expected[0] == x_train).all()
    assert (expected[1] == y_train).all()
    assert (expected[2] == x_u).all()


def test_obtain_train_unlabelled_all_labelled():
    data = (np.array([[i, i] for i in range(5)]), np.array([0, 1, 2, 2, 0]))

    # Cuando i = 0 e i = 2 es un dato no etiquetado
    expected = (np.array([[i, i] for i in range(5)]), np.array([0, 1, 2, 2, 0]))
    #          -------------x_train--------------     ---------y_train---------

    x_train, y_train, x_u = obtain_train_unlabelled(data[0], data[1])

    assert (expected[0] == x_train).all()
    assert (expected[1] == y_train).all()
    assert not x_u  # Vacío


def test_obtain_train_unlabelled_all_unlabelled():
    data = (np.array([[i, i] for i in range(5)]), np.array([-1, -1, -1, -1, -1]))

    # Cuando i = 0 e i = 2 es un dato no etiquetado
    expected = np.array([[i, i] for i in range(5)])
    #          ------------unlabelled-------------

    x_train, y_train, x_u = obtain_train_unlabelled(data[0], data[1])

    assert not x_train
    assert not y_train
    assert (expected == x_u).all()


def test_split_all_labelled():
    x = pd.DataFrame(data=[[i, i] for i in range(100)])
    y = pd.DataFrame(data=[random.randint(0, 2) for _ in range(100)])

    x_train, y_train, x_test, y_test = data_split(x, y, False, p_unlabelled=0.5, p_test=0.2)
    """
    El 50% de 100 = 50 serán etiquetados (otros 50 no etiquetados).
    De esos 50 etiquetados el 20% serán para test = 10 para test.
    El total de entrenamiento (etiquetados + no etiquetados) = 90
    """
    assert len(x_train) == 90
    assert len(y_train) == 90
    assert len(x_test) == 10
    assert len(y_test) == 10


def test_split_all_some_unlabelled():
    x = pd.DataFrame(data=[[i, i] for i in range(100)])
    y = pd.DataFrame(data=[random.randint(0, 2) if i < 30 else -1 for i in range(100)])

    x_train, y_train, x_test, y_test = data_split(x, y, True, p_unlabelled=-1, p_test=0.2)
    """
    El 30% serán etiquetados (otros 70 no etiquetados).
    De esos 30 etiquetados el 20% serán para test = 6 para test.
    El total de entrenamiento (etiquetados + no etiquetados) = 94
    """
    assert len(x_train) == 94
    assert len(y_train) == 94
    assert len(x_test) == 6
    assert len(y_test) == 6


def test_pca_reduction():
    columns = ["C1", "C2", "class", "info"]

    log = pd.DataFrame(data=[[i, i + 1, i + 2, random.randint(0, 1), i + 3] for i in range(100)],
                       columns=["feature1", "feature2", "feature3", "class", "info"])

    df_3_to_2 = log_pca_reduction(log, ["feature1", "feature2", "feature3"])

    assert (df_3_to_2.columns == columns).all()

    log = pd.DataFrame(data=[[i, i + 1, random.randint(0, 1), i + 3, i + 4, i + 2, i + 5] for i in range(100)],
                       columns=["feature1", "feature2", "class", "feature4", "feature5", "feature3", "info"])

    df_5_to_2 = log_pca_reduction(log, ["feature1", "feature2", "feature3", "feature4", "feature5"])

    assert (df_5_to_2.columns == columns).all()

    log = pd.DataFrame(data=[[i, i + 1, i + 2, i + 3, i + 4, random.randint(0, 1), i + 5] for i in range(100)],
                       columns=["feature1", "feature2", "feature3", "feature4", "feature5", "class", "info"])

    df_5_to_3 = log_pca_reduction(log, ["feature1", "feature2", "feature3", "feature4", "feature5"], n_com=3)

    assert (df_5_to_3.columns == ["C1", "C2", "C3", "class", "info"]).all()


def test_cxcy_reduction():
    log = pd.DataFrame(data=[[i, i + 1, i + 2, random.randint(0, 1), i + 3] for i in range(100)],
                       columns=["feature1", "feature2", "feature3", "class", "info"])

    df = log_cxcy_reduction(log, "feature1", "feature3", ["feature1", "feature2", "feature3"])

    assert (df.columns == ["feature1", "feature3", "class", "info"]).all()


def test_labelencoder():
    normal_expected_x = [[5.1, 3.5, 1.4, 0.2],
                         [4.9, 3.0, 1.4, 0.2]]

    normal_expected_y = [0, 1]

    unlabelled_expected_x = [[5.1, 3.5, 1.4, 0.2],
                             [4.9, 3.0, 1.4, 0.2],
                             [4.7, 3.2, 1.3, 0.2]]

    unlabelled_expected_y = [0, 1, -1]

    combinations = [["normal", normal_expected_x, normal_expected_y, False],
                    ["unlabelled", unlabelled_expected_x, unlabelled_expected_y, True]]

    formats = [".arff", ".csv"]

    for combination in combinations:
        for form in formats:
            dl = DatasetLoader(f"test_files/{combination[0]}{form}")

            assert (dl.get_allfeatures() == ["feature1", "feature2", "feature3", "feature4", "class"]).all()

            dl.set_target("class")

            assert dl.target == "class"
            assert (dl.get_only_features() == ["feature1", "feature2", "feature3", "feature4"]).all()

            x, y, mapping, is_unlabelled = dl.get_x_y()

            assert (x.values == combination[1]).all()
            assert (y.values.ravel() == combination[2]).all()
            assert is_unlabelled == combination[3]


if __name__ == '__main__':
    pytest.main()
