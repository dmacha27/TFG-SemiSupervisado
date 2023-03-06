import sslearn.wrapper
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from algoritmos import CoTraining, DemocraticCoLearning
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split


def cotraining_comparison():
    """
    Este método compara la implementación de CoTraining realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    dl = DatasetLoader('../../utilidades/datasets/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    ct = CoTraining(clf1=DecisionTreeClassifier(),
                    clf2=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ), p=1, n=3, u=75, n_iter=30)

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)

    log, _, _ = ct.fit(x, y, x_test, y_test, dl.get_only_features())

    ct_acc = ct.get_accuracy_score(x_test, y_test)
    print("Precisión Implementación: ", ct_acc)

    ctssl = sslearn.wrapper.CoTraining(second_base_estimator=SVC(kernel='rbf',
                                                                 probability=True,
                                                                 C=1.0,
                                                                 gamma='scale',
                                                                 random_state=0
                                                                 ))

    ctssl.fit(x, y, features=[[0, 1, 2, 3, 4], [5, 6, 7, 8]])

    ctssl_acc = ctssl.score(x_test, y_test)
    print("Precisión sslearn: ", ctssl_acc)

    return ct_acc, ctssl_acc


def democraticolearning_comparison():
    """
    Este método compara la implementación de Democratic Co-Learning realizada en este proyecto contra
    la de sslearn (de José Luis Garrido-Labrador).

    :return: Accuracy de ambos modelos después del entrenamiento
    """

    dl = DatasetLoader('../../utilidades/datasets/breast.w.arff')
    dl.set_target("Class")
    x, y, mapa, is_unlabelled = dl.get_x_y()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=0.8, p_test=0.2)
    clfs = [SVC(kernel='rbf',
                probability=True,
                C=1.0,
                gamma='scale',
                random_state=0
                ), GaussianNB(), DecisionTreeClassifier()]
    dcl = DemocraticCoLearning(clfs=clfs)

    log, _ = dcl.fit(x, y, x_test, y_test, dl.get_only_features())
    dcl_acc = dcl.get_accuracy_score(x_test, y_test)
    print("Precisión Implementación: ", dcl_acc)

    dclssl = sslearn.wrapper.DemocraticCoLearning(base_estimator=clfs)

    dclssl.fit(x, y)
    dclssl_acc = dclssl.score(x_test, y_test)
    print("Precisión sslearn: ", dclssl_acc)
    return dcl_acc, dclssl_acc


if __name__ == '__main__':
    print("---Co-Training---")
    cotraining_comparison()
    print("---Democratic Co-Learning---")
    democraticolearning_comparison()
