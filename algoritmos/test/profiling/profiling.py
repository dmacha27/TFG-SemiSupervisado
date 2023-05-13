import cProfile
import pstats

from sklearn.datasets import load_breast_cancer
from sklearn.naive_bayes import GaussianNB

from algoritmos import SelfTraining, CoTraining
from algoritmos.utilidades.datasplitter import data_split

TRAINING_FILE = '../utilidades/datasets/waveform5000.arff'


def profile_selftraining():
    """
    Obtiene el tiempo de ejecución de las llamadas que se llevan a cabo en el entrenamiento del algoritmo
    para poder observar su complejidad.

    """
    st = SelfTraining(clf=GaussianNB(), n=10, n_iter=150)

    data = load_breast_cancer()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(data.data, data.target, False, p_unlabelled=0.8, p_test=0.4)

    profile = cProfile.Profile()
    profile.enable()
    st.fit(x, y, x_test, y_test, data.feature_names)
    profile.disable()
    profile.dump_stats('profile_results/selftraining.pstats')


def profile_cotraining():
    """
    Obtiene el tiempo de ejecución de las llamadas que se llevan a cabo en el entrenamiento del algoritmo
    para poder observar su complejidad.

    """
    st = CoTraining(clf1=GaussianNB(),
                    clf2=GaussianNB(),
                    p=1, n=3, u=5, n_iter=10)

    data = load_breast_cancer()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(data.data, data.target, False, p_unlabelled=0.8, p_test=0.4)

    profile = cProfile.Profile()
    profile.enable()
    st.fit(x, y, x_test, y_test, data.feature_names)
    profile.disable()
    profile.dump_stats('profile_results/cotraining.pstats')


def show_stats(file):
    """
    Muestra las estadísticas guardadas en un fichero

    :param file: Fichero de estadísticas de entrada.
    """
    stats = pstats.Stats(f'profile_results/{file}')
    stats.sort_stats('tottime')
    stats.print_stats()


if __name__ == '__main__':
    profile_selftraining()
    profile_cotraining()

    show_stats('selftraining.pstats')
