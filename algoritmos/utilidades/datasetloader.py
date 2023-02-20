# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 04/02/2023 14:30
# Descripción: Permite cargar datasets
# Version: 1.2

from os.path import isfile

import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.api import types
from scipy.io import arff

from algoritmos.utilidades.filetype import FileType
from algoritmos.utilidades.labelencoder import OwnLabelEncoder


class DatasetLoader:

    def __init__(self, file):
        """
        Cargador para archivos (ARFF o CSV).

        :param file: Ruta del fichero
        """

        self.target = None
        if not isfile(file):
            raise FileNotFoundError("El archivo no existe en el conjunto de datasets")

        if ".csv" in file:
            self.type = FileType.CSV
        elif ".arff" in file:
            self.type = FileType.ARFF
        else:
            raise ValueError("El fichero no es CSV o ARFF")

        self.file = file

    def get_allfeatures(self):
        """
        Obtiene las características de los datos. NO distingue el target (también se incluye)

        :return: Listado de las características de los datos.
        """

        return self.get_data().columns.values

    def set_target(self, target):
        """
        Especifica el target de los datos

        :param target: El target o clase para la posterior clasificación
        """
        self.target = target

    def get_only_features(self):
        """
        Obtiene las características de los datos. NO incluye target

        :return: Listado de las características de los datos (sin target).
        """
        if self.target is None:
            raise ValueError("La clase o target no ha sido establecida, selecciona primero la característica que "
                             "actúa como target")

        return np.setdiff1d(self.get_data().columns.values, self.target)

    def get_data(self):
        """
        Obtiene los datos sin procesar (directamente del fichero) según
        el tipo de fichero que sea

        :return: Datos en forma de dataframe
        """
        if self.type == FileType.CSV:
            return self._csv_data()
        elif self.type == FileType.ARFF:
            return self._arff_data()

    def _csv_data(self):
        return pd.read_csv(self.file)

    def _arff_data(self):
        """
        Convierte los datos del fichero en un dataframe

        :return: Datos en forma de dataframe
        """
        data = arff.loadarff(self.file)
        df = pd.DataFrame(data[0])

        return df

    def _detect_categorical_features(self, x: DataFrame):
        """

        :param x: Características
        :return: True si todas son numéricas, False en caso contrario
        """
        return not all(types.is_numeric_dtype(t) for t in list(x.dtypes))

    def _detect_unlabelled_targets(self, y: DataFrame):
        values = y[self.target].astype(str).values
        return "-1" in values or "-1.0" in values

    def get_x_y(self):
        """
        Obtiene por separado los datos (las características) y los target o clases

        :return: Las características (x), las clases o targets (y), el mapeo de las clases codificadas a las
        originales y si el conjunto de datos ya era semi-supervisado
        """

        if self.target is None:
            raise ValueError("La clase o target no ha sido establecida, selecciona primero la característica que "
                             "actúa como target")

        data = self.get_data()

        x = data.drop(columns=[self.target])

        if self._detect_categorical_features(x):
            raise ValueError("Se han detectado características categóricas o indefinidas ('O' de Object),"
                             " es necesario que se aseguren características numéricas")

        if self.type == FileType.CSV:
            y = pd.DataFrame(data[self.target], columns=[self.target])
        else:
            y = pd.DataFrame(
                np.array([v.decode("utf-8") if not types.is_numeric_dtype(type(v)) else v for v in
                          data[self.target].values]),
                columns=[self.target])
            y.replace("?", "-1", inplace=True)

        is_unlabelled = self._detect_unlabelled_targets(y)

        le = OwnLabelEncoder()

        y, mapping = le.transform(y)

        return x, y, mapping, is_unlabelled
