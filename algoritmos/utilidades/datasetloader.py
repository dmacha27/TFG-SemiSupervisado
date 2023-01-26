from os.path import isfile

import pandas as pd
from pandas import DataFrame
from scipy.io import arff
from sklearn.model_selection import train_test_split

from algoritmos.utilidades.filetype import FileType


class DatasetLoader:

    def __init__(self, file, labelled_p=0.1, unlabelled_p=0.9):
        """
        Cargador para archivos (ARFF o CSV).

        :param file: Nombre del dataset a cargar (contenido en '../datasets/')
        :param labelled_p: Porcentaje de datos etiquetados
        :param unlabelled_p: Porcentaje de datos no etiquetados
        """

        if not isfile(f'../datasets/{file}'):
            raise FileNotFoundError("El archivo no existe en el conjunto de datasets")

        if ".csv" in file:
            self.type = FileType.CSV
        elif ".arff" in file:
            self.type = FileType.ARFF
        else:
            raise ValueError("El fichero no es CSV o ARFF")

        self.labelled_p = labelled_p
        self.unlabelled_p = unlabelled_p

    def data(self):
        if self.type == FileType.CSV:
            # return self._csv_data()
            pass
        elif self.type == FileType.ARFF:
            # return self._arff_data()
            pass

        return 0
