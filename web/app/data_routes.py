import json
import os
from datetime import datetime

from flask import request, session, Blueprint, current_app
from flask_login import current_user
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sqlalchemy.exc import SQLAlchemyError

from algoritmos import SelfTraining, CoTraining, DemocraticCoLearning, TriTraining
from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_pca_reduction, log_cxcy_reduction

from . import db
from .models import Run

data_bp = Blueprint('data_bp', __name__)


@data_bp.route('/selftraining', methods=['POST'])
def datosselftraining():
    clasificador = request.form['clasificador1']

    n = int(request.form['n'])
    th = float(request.form['th'])

    st = SelfTraining(
        clf=obtener_clasificador(clasificador, obtener_parametros_clasificador(clasificador, "clasificador1")),
        n=n if n != -1 else None,
        th=th if th != -1 else None,
        n_iter=int(request.form['n_iter']))

    info = obtener_info(st)

    return json.dumps(info)


@data_bp.route('/cotraining', methods=['POST'])
def datoscotraining():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']
    ct = CoTraining(
        clf1=obtener_clasificador(clasificador1, obtener_parametros_clasificador(clasificador1, "clasificador1")),
        clf2=obtener_clasificador(clasificador2, obtener_parametros_clasificador(clasificador2, "clasificador2")),
        p=int(request.form['p']),
        n=int(request.form['n']),
        u=int(request.form['u']),
        n_iter=int(request.form['n_iter']))

    info = obtener_info(ct)

    return json.dumps(info)


@data_bp.route('/democraticcolearning', methods=['POST'])
def datosdemocraticcolearning():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']
    clasificador3 = request.form['clasificador3']

    clf1 = obtener_clasificador(clasificador1, obtener_parametros_clasificador(clasificador1, "clasificador1"))
    clf2 = obtener_clasificador(clasificador2, obtener_parametros_clasificador(clasificador2, "clasificador2"))
    clf3 = obtener_clasificador(clasificador3, obtener_parametros_clasificador(clasificador3, "clasificador3"))

    dcl = DemocraticCoLearning([clf1, clf2, clf3])

    info = obtener_info(dcl)
    return json.dumps(info)


@data_bp.route('/tritraining', methods=['POST'])
def datostritraining():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']
    clasificador3 = request.form['clasificador3']

    clf1 = obtener_clasificador(clasificador1, obtener_parametros_clasificador(clasificador1, "clasificador1"))
    clf2 = obtener_clasificador(clasificador2, obtener_parametros_clasificador(clasificador2, "clasificador2"))
    clf3 = obtener_clasificador(clasificador3, obtener_parametros_clasificador(clasificador3, "clasificador3"))

    tt = TriTraining([clf1, clf2, clf3])

    info = obtener_info(tt)
    return json.dumps(info)


def obtener_info(algoritmo):
    """Evita el código duplicado de la obtención de toda la información
    de la ejecución de los algoritmos.

    Realiza la carga de datos, las particiones de datos, el entrenamiento del algoritmo,
    la conversión a un log (logger) en 2D y la conversión a JSON para las plantillas.
    """
    datasetloader = DatasetLoader(session['FICHERO'])
    datasetloader.set_target(request.form['target'])
    x, y, mapa, is_unlabelled = datasetloader.get_x_y()

    (x, y, x_test, y_test) = data_split(x,
                                        y,
                                        is_unlabelled,
                                        p_unlabelled=int(request.form['p_unlabelled']) / 100,
                                        p_test=int(request.form['p_test']) / 100)

    specific_stats = None
    if not isinstance(algoritmo, (DemocraticCoLearning, TriTraining)):
        log, stats, iteration = algoritmo.fit(x, y, x_test, y_test, datasetloader.get_only_features())
    else:
        log, stats, specific_stats, iteration = algoritmo.fit(x, y, x_test, y_test, datasetloader.get_only_features())

    norm = True if request.form['norm'] == 'on' else False

    if request.form['pca'] == 'on':
        _2d = log_pca_reduction(log,
                                datasetloader.get_only_features(), normalize=norm).to_json()
    else:
        _2d = log_cxcy_reduction(log,
                                 request.form['cx'],
                                 request.form['cy'],
                                 datasetloader.get_only_features(), normalize=norm).to_json()

    info = {'iterations': iteration,
            'log': _2d,
            'stats': stats.to_json(),
            'mapa': json.dumps(mapa)}

    if isinstance(algoritmo, (DemocraticCoLearning, TriTraining)):
        info = info | {'specific_stats': {key: specific_stats[key].to_json() for key in specific_stats}}

    if current_user.is_authenticated:
        date = int(datetime.now().timestamp())

        with open(os.path.join(current_app.config['CARPETA_RUNS'], f'run-{current_user.id}-{date}.json'), 'w') as f:
            json.dump(info, f)

        run = Run()
        run.algorithm = session['ALGORITMO']
        run.filename = os.path.basename(session['FICHERO'])
        if request.form['pca'] == 'on':
            run.cx = 'C1'
            run.cy = 'C2'
        else:
            run.cx = request.form['cx']
            run.cy = request.form['cy']
        run.date = datetime.now()
        run.jsonfile = f'run-{current_user.id}-{date}.json'
        run.user_id = current_user.id

        try:
            db.session.add(run)
        except SQLAlchemyError:
            db.session.rollback()
            os.remove(os.path.join(current_app.config['CARPETA_RUNS'], f'run-{current_user.id}-{date}.json'))
        else:
            db.session.commit()

    return info


def obtener_parametros_clasificador(clasificador, nombre):
    """A la hora de instanciar un clasificador (sklearn), este tiene una serie de parámetros
    (NO CONFUNDIR CON LOS PARÁMETROS DE LOS ALGORITMOS SEMI-SUPERVISADOS).
    Aclaración: estos vienen codificados en parametros.json.

    Interpreta el formulario de la configuración para obtener estos valores y que puedan ser
    desempaquetados con facilidad (**).
    """
    with open(os.path.join(os.path.dirname(__file__), os.path.normpath("static/json/parametros.json"))) as f:
        clasificadores = json.load(f)

    parametros_clasificador = {}
    for key in clasificadores[clasificador].keys():
        parametro = clasificadores[clasificador][key]
        if parametro["type"] == "number" and parametro["step"] == 0.1:
            p = float(request.form[nombre + "_" + key])
            parametros_clasificador[key] = p
        elif parametro["type"] == "number" and parametro["step"] == 1:
            p = int(request.form[nombre + "_" + key])
            parametros_clasificador[key] = p
        else:
            parametros_clasificador[key] = request.form[nombre + "_" + key]

    return parametros_clasificador


def obtener_clasificador(nombre, params):
    """Instancia un clasificador (sklearn) a partir de su nombre y los parámetros
    introducidos (provenientes de "obtener_parametros_clasificador").
    """

    if nombre == "SVC":
        params = params | {"probability": True}
        return SVC(**params)
    elif nombre == "GaussianNB":
        return GaussianNB()
    elif nombre == "KNeighborsClassifier":
        return KNeighborsClassifier(**params)
    elif nombre == "DecisionTreeClassifier":
        return DecisionTreeClassifier(**params)
