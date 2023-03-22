import copy
import os
from copy import deepcopy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sslearn.wrapper
from numpy import mean, std
from sklearn.model_selection import KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_digits, load_wine

from sklearn.metrics import accuracy_score, f1_score
from algoritmos import CoTraining, DemocraticCoLearning, SelfTraining
from algoritmos.utilidades.datasplitter import data_split


def cross_validation(own_clf, clf1_params, other_clf, clf2_params, x, y, folds, own_features, comparison_name,
                     ssl_features=None):
    """
    Realiza el proceso de validación cruzada manualmente para comparar modelo de implementación propia contra uno
    de sslearn

    :param own_clf: Primer modelo de entrenamiento (implementación propia).
    :param clf1_params: Parámetros para el primer modelo.
    :param other_clf: Segundo modelo de entrenamiento (sslearn).
    :param clf2_params: Parámetros para el segundo modelo.
    :param x: Instancias.
    :param y: Etiquetas de las instancias.
    :param folds: Número de folds.
    :param own_features: Etiquetas de las características (implementación propia).
    :param comparison_name: Nombre de la comparación.
    :param ssl_features: Índices de las características (sslearn)
    :return: Exactitud de ambos modelos (mismo orden que de entrada) junto con ambas desviaciones estándar
    """

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled=False, p_unlabelled=0.8, p_test=0.2)

    first_i_u = np.where(y == -1)[0][0]
    x_labelled = x[:first_i_u]
    x_unlabelled = x[first_i_u:]

    y = y[:first_i_u]

    # En x e y solo hay datos etiquetados
    x = np.concatenate((x_labelled, x_test), axis=0)
    y = np.concatenate((y, y_test))

    kf = KFold(n_splits=folds)

    stats_clf1 = pd.DataFrame(columns=['Accuracy', 'F1-Score'])
    stats_clf2 = pd.DataFrame(columns=['Accuracy', 'F1-Score'])
    accuracy_clf1 = []
    accuracy_clf2 = []
    for train_index, test_index in kf.split(x):
        x_test = x[test_index]
        y_test = y[test_index]

        x_train = x[train_index]
        y_train = y[train_index]
        x_train = np.concatenate((x_train, x_unlabelled), axis=0)
        y_train = np.concatenate((y_train, [-1] * len(x_unlabelled)))

        clf1 = own_clf(**copy.deepcopy(clf1_params))

        clf1.fit(x_train, y_train, x_test, y_test, own_features)  # Implementación

        clf2 = other_clf(**copy.deepcopy(clf2_params))
        if ssl_features:
            clf2.fit(x_train, y_train, features=ssl_features)  # sslearn
        else:
            clf2.fit(x_train, y_train)

        acc = clf1.get_accuracy_score(x_test, y_test)
        accuracy_clf1.append(acc)
        stats_clf1.loc[len(stats_clf1)] = [acc, f1_score(y_test, clf1.predict(x_test), average="weighted")]

        acc = clf2.score(x_test, y_test)
        accuracy_clf2.append(acc)
        stats_clf2.loc[len(stats_clf2)] = [acc, f1_score(y_test, clf2.predict(x_test), average="weighted")]

    stats_clf1.to_csv(path_or_buf=f'./results/{comparison_name}-own.csv', index=False)
    stats_clf2.to_csv(path_or_buf=f'./results/{comparison_name}-sslearn.csv', index=False)
    return mean(accuracy_clf1), std(accuracy_clf1), mean(accuracy_clf2), std(accuracy_clf2)


def selftraining_comparison(data, comparison_name):
    """
    Este método compara la implementación de SelfTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """
    return cross_validation(SelfTraining,
                            {'clf': GaussianNB(), 'th': 0.75, 'n_iter': 10},
                            sslearn.wrapper.SelfTraining,
                            {'base_estimator': GaussianNB(), 'threshold': 0.75, 'max_iter': 10},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name)


def cotraining_comparison(data, comparison_name):
    """
    Este método compara la implementación de CoTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """
    n_features = len(data.feature_names)

    return cross_validation(CoTraining,
                            {'clf1': DecisionTreeClassifier(), 'clf2': GaussianNB(),
                             'p': 1, 'n': 3, 'u': 75, 'n_iter': 30},
                            sslearn.wrapper.CoTraining,
                            {'second_base_estimator': GaussianNB()},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name,
                            [list(range(n_features // 2 + 1)),
                             list(range(n_features // 2 + 1,
                                        n_features))])


def democraticolearning_comparison(data, comparison_name):
    """
    Este método compara la implementación de Democratic Co-Learning realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    clfs = [SVC(kernel='rbf',
                probability=True,
                C=1.0,
                gamma='scale'
                ), GaussianNB(), DecisionTreeClassifier()]

    return cross_validation(DemocraticCoLearning,
                            {'clfs': deepcopy(clfs)},
                            sslearn.wrapper.DemocraticCoLearning,
                            {'base_estimator': deepcopy(clfs)},
                            data.data,
                            data.target,
                            10,
                            data.feature_names,
                            comparison_name)


def draw_performance(dataset_name):
    """
    Con los archivos generados de las estadísticas de las implementaciones
    se dibuja un gráfico de cajas para el conjunto de datos indicado.
    En el eje Y la medida de la estadística y en X cada algoritmo

    :param dataset_name: nombre del conjunto de datos
    """

    pandas_dict = {}
    stats = None
    for file in os.listdir('./results/'):
        if f'{dataset_name}' in file:
            implementation = file.split("-")[2].split(".")[0]
            algorithm = file.split("-")[0]
            if algorithm not in pandas_dict:
                pandas_dict[algorithm] = {}
            if implementation not in pandas_dict[algorithm]:
                pandas_dict[algorithm][implementation] = pd.read_csv(f'./results/{file}')

            stats = list(pandas_dict[algorithm][implementation].columns)

    algorithms = list(pandas_dict.keys())

    fig, axs = plt.subplots(len(stats), len(pandas_dict.keys()), sharey='row', sharex='col', figsize=(10, 8))
    fig.subplots_adjust(wspace=0, hspace=0.02)

    # https://stackoverflow.com/questions/20289091/python-matplotlib-filled-boxplots
    colors = ['pink', 'lightblue', 'tan']

    stat_count = 0
    for n_row, ax_row in enumerate(axs):
        algorithms_count = 0
        for n_col, ax in enumerate(ax_row):
            box = ax.boxplot(
                [pandas_dict[algorithms[algorithms_count]][item][stats[stat_count]] for item in ['own', 'sslearn']],
                showmeans=True,
                meanline=True,
                showfliers=False,
                patch_artist=True,
                medianprops=dict(color='blue'),
                meanprops=dict(color='black'))
            for patch in box['boxes']:
                patch.set_facecolor(colors[stat_count])

            ax.set_xticks([1, 2])
            if n_row == 0:
                ax.set(xticklabels=['Propia', 'sslearn'])
            else:
                ax.set(xticklabels=['Propia', 'sslearn'], xlabel=algorithms[algorithms_count])

            if n_col == 0:
                ax.set_ylabel(stats[stat_count])
            algorithms_count += 1
        stat_count += 1

    plt.suptitle(dataset_name, fontsize=35)
    fig.savefig(f'./results/plot_images/{dataset_name}')


if __name__ == '__main__':
    data = load_wine()

    dataset_name = "Wine"

    print("---Self-Training---")
    own, std_own, ssl, std_ssl = selftraining_comparison(data, f"SelfTraining-{dataset_name}")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Co-Training---")
    own, std_own, ssl, std_ssl = cotraining_comparison(data, f"CoTraining-{dataset_name}")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    print("---Democratic Co-Learning---")
    own, std_own, ssl, std_ssl = democraticolearning_comparison(data, f"DemocraticCoLearning-{dataset_name}")

    print(f"Implementación propia: {own} ({std_own})")
    print(f"Implementación sslearn: {ssl} ({std_ssl})")

    draw_performance(dataset_name)
