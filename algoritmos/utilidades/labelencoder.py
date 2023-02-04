# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: David Martínez Acha
# Fecha: 04/02/2023 18:43
# Descripción: Codifica las etiquetas categóricas (o no) para que sean numéricas
# Version: 1.0

import pandas as pd
from pandas import DataFrame
from sklearn.preprocessing import LabelEncoder


class OwnLabelEncoder:

    def __init__(self):
        self.le = LabelEncoder()

    def transform(self, y: DataFrame):
        """
        Transforma las etiquetas (cateogóricas o no) a numéricas ignorando -1 en el caso
        de que el propio conjunto de datos ya fuese semi-supervisado.

        :param y: Etiquetas de los datos.
        :return: Las clases o targets (y) y el mapeo de las clases codificadas a las
        originales
        """

        values = y[y.columns[0]].values
        self.le.fit([v for v in values if v not in [-1, "-1", "-1.0"]])

        y = pd.DataFrame([self.le.transform([v])[0] if v not in [-1, "-1", "-1.0"] else -1 for v in values],
                         columns=['target'], dtype=int)

        mapping = {int(t): c for t, c in zip(self.le.transform(self.le.classes_), self.le.classes_)}

        return y, mapping
