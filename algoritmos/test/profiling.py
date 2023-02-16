import cProfile
import pstats

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from algoritmos import SelfTraining, CoTraining
from algoritmos.utilidades import DatasetLoader, data_split

TRAINING_FILE = '../utilidades/datasets/waveform5000.arff'


def profile_selftraining():
    """
    Obtiene el tiempo de ejecución de las llamadas que se llevan a cabo en el entrenamiento del algoritmo
    para poder observar su complejidad.

    """
    dl = DatasetLoader(TRAINING_FILE)
    dl.set_target("class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = SelfTraining(clf=GaussianNB(), n=10, n_iter=150)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)

    profile = cProfile.Profile()
    profile.enable()
    log, stats = st.fit(x, y, x_test, y_test, dl.get_only_features())
    profile.disable()
    profile.dump_stats('profile_results/selftraining.pstats')


def profile_cotraining():
    """
    Obtiene el tiempo de ejecución de las llamadas que se llevan a cabo en el entrenamiento del algoritmo
    para poder observar su complejidad.

    """
    dl = DatasetLoader(TRAINING_FILE)
    dl.set_target("class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    st = CoTraining(clf1=GaussianNB(),
                    clf2=GaussianNB(),
                    p=1, n=3, u=5, n_iter=10)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)

    profile = cProfile.Profile()
    profile.enable()
    log, stats = st.fit(x, y, x_test, y_test, dl.get_only_features())
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
