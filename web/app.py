import os
import json

import datetime
import re
import sys

from flask import Flask, flash, render_template, request, redirect, session, url_for, send_file
from flask_babel import Babel, gettext
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_pca_reduction, log_cxcy_reduction
from sklearn.svm import SVC
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

from algoritmos import SelfTraining, DemocraticCoLearning, TriTraining
from algoritmos import CoTraining

with open("static/parametros.json") as f:
    clasificadores = json.load(f)


def get_locale():
    return request.accept_languages.best_match(['es', 'en'])


app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

babel = Babel(app, locale_selector=get_locale)

app.secret_key = "ae4c977b14e2ecf38d485869018ec8f924b312132ee3d11d1ce755cdff9bc0af"
app.config.update(SESSION_COOKIE_SAMESITE='Strict')
app.config['CARPETA_DATASETS'] = 'datasets'
app.config['SESSION_TYPE'] = 'filesystem'


@app.context_processor
def variables_globales():
    return {'titulos': {'selftraining': 'Self-Training',
                        'cotraining': 'Co-Training',
                        'democraticcolearning': 'Democratic Co-Learning',
                        'tritraining': 'Tri-Training'}}


@app.route('/', methods=['GET'])
def inicio():
    session.pop('ALGORITMO', None)
    session.pop('FICHERO', None)
    return render_template('inicio.html')


@app.route('/seleccionar/<algoritmo>')
def seleccionar_algoritmo(algoritmo=None):
    session['ALGORITMO'] = algoritmo
    return redirect(url_for('subida'))


@app.route('/descargar_prueba')
def descargar_prueba():
    path = 'datasets/seleccionar/Prueba.arff'
    return send_file(path, as_attachment=True)


@app.route('/subida', methods=['GET', 'POST'])
def subida():
    if 'ALGORITMO' not in session:
        flash(gettext("You must select an algorithm"))
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        file = request.files['archivo']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename) + "-" + str(int(datetime.datetime.now().timestamp()))
            session['FICHERO'] = os.path.join(app.config['CARPETA_DATASETS'], filename)
            file.save(os.path.join(app.config['CARPETA_DATASETS'], filename))

    return render_template('subida.html')


@app.route('/configuracion/<algoritmo>', methods=['GET'])
def configurar_algoritmo(algoritmo=None):
    if 'FICHERO' not in session:
        flash(gettext("You must upload a file"))
        return redirect(url_for('subida'))

    if '.ARFF' not in session['FICHERO'].upper():
        if '.CSV' not in session['FICHERO'].upper():
            flash(gettext("File must be ARFF or CSV"))
            return redirect(url_for('subida'))

    dl = DatasetLoader(session['FICHERO'])

    return render_template(algoritmo + 'config.html',
                           caracteristicas=dl.get_allfeatures(),
                           clasificadores=list(clasificadores.keys()),
                           parametros=clasificadores)


@app.route('/visualizacion/<algoritmo>', methods=['GET', 'POST'])
def visualizar_algoritmo(algoritmo):
    """Centraliza la carga de la página de visualización.
    Es el paso siguiente después de la configuración.
    """
    if 'target' not in request.form:
        flash(gettext("You must select the parameters of the algorithm"))
        return redirect(url_for('configurar_algoritmo', algoritmo="None"))

    # En este punto se deben recoger todos los parámetros
    # que el usuario introdujo en el formulario de configuración
    params = []
    if session['ALGORITMO'] == "selftraining":
        params = parametros_selftraining()
    elif session['ALGORITMO'] == "cotraining":
        params = parametros_cotraining()
    elif session['ALGORITMO'] == "democraticcolearning":
        params = parametros_democraticcolearning_tritraining()
    elif session['ALGORITMO'] == "tritraining":
        params = parametros_democraticcolearning_tritraining()

    """En params se encontrarán todos los datos necesarios para ejecutar el algoritmo.
    Realmente no se le pasa la información ejecutada, se realiza una petición POST
    desde Javascript con estos parámetros al renderizar la plantilla del algoritmo."""

    return render_template(session['ALGORITMO'] + '.html',  # p.ej selftraining.html (donde están las visualizaciones)
                           params=params,
                           cx=request.form.get('cx', 'C1'),
                           cy=request.form.get('cy', 'C2'))


def parametros_selftraining():
    clasificador = request.form['clasificador1']

    # Estos son los parámetros concretos de Self-Training
    params = [
        {"nombre": "clasificador1", "valor": request.form['clasificador1']},
        {"nombre": "n", "valor": request.form.get('n', -1)},
        {"nombre": "th", "valor": request.form.get('th', -1)},
        {"nombre": "n_iter", "valor": request.form.get('n_iter')},
        {"nombre": "target", "valor": request.form.get('target')},
        {"nombre": "cx", "valor": request.form.get('cx', 'C1')},
        {"nombre": "cy", "valor": request.form.get('cy', 'C2')},
        {"nombre": "pca", "valor": request.form.get('pca', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled', -1)},
        {"nombre": "p_test", "valor": request.form.get('p_test', -1)},
    ]

    # Los parámetros anteriores no incluyen los propios parámetros de los clasificadores
    # (SVM, GaussianNB...), esta función lo incluye
    incorporar_clasificadores_params([clasificador], params)

    return params


def parametros_cotraining():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']

    # Estos son los parámetros concretos de Co-Training
    params = [
        {"nombre": "clasificador1", "valor": request.form['clasificador1']},
        {"nombre": "clasificador2", "valor": request.form['clasificador2']},
        {"nombre": "p", "valor": request.form.get('p', -1)},
        {"nombre": "n", "valor": request.form.get('n', -1)},
        {"nombre": "u", "valor": request.form.get('u', -1)},
        {"nombre": "n_iter", "valor": request.form.get('n_iter')},
        {"nombre": "target", "valor": request.form.get('target')},
        {"nombre": "cx", "valor": request.form.get('cx', 'C1')},
        {"nombre": "cy", "valor": request.form.get('cy', 'C2')},
        {"nombre": "pca", "valor": request.form.get('pca', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled', -1)},
        {"nombre": "p_test", "valor": request.form.get('p_test', -1)},
    ]

    # Los parámetros anteriores no incluyen los propios parámetros de los clasificadores
    # (SVM, GaussianNB...), esta función lo incluye
    incorporar_clasificadores_params([clasificador1, clasificador2], params)

    return params


def parametros_democraticcolearning_tritraining():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']
    clasificador3 = request.form['clasificador3']

    # Estos son los parámetros concretos de Democratic Co-Learning
    params = [
        {"nombre": "clasificador1", "valor": request.form['clasificador1']},
        {"nombre": "clasificador2", "valor": request.form['clasificador2']},
        {"nombre": "clasificador3", "valor": request.form['clasificador3']},
        {"nombre": "target", "valor": request.form.get('target')},
        {"nombre": "cx", "valor": request.form.get('cx', 'C1')},
        {"nombre": "cy", "valor": request.form.get('cy', 'C2')},
        {"nombre": "pca", "valor": request.form.get('pca', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled', -1)},
        {"nombre": "p_test", "valor": request.form.get('p_test', -1)},
    ]

    # Los parámetros anteriores no incluyen los propios parámetros de los clasificadores
    # (SVM, GaussianNB...), esta función lo incluye
    incorporar_clasificadores_params([clasificador1, clasificador2, clasificador3], params)

    return params


def incorporar_clasificadores_params(nombre_clasificadores, params):
    """Incluye los parámetros de los propios clasificadores
    a la lista de parámetros generales.
    """
    for i, clasificador in enumerate(nombre_clasificadores):
        for key in clasificadores[clasificador].keys():
            params.append({"nombre": f"clasificador{i + 1}_" + key,
                           "valor": request.form.get(f"clasificador{i + 1}_" + key, -1)})


@app.route('/selftrainingd', methods=['GET', 'POST'])
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


@app.route('/cotrainingd', methods=['GET', 'POST'])
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


@app.route('/democraticcolearningd', methods=['GET', 'POST'])
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


@app.route('/tritrainingd', methods=['GET', 'POST'])
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
                                        p_unlabelled=float(request.form['p_unlabelled']),
                                        p_test=float(request.form['p_test']))

    specific_stats = None
    if not isinstance(algoritmo, (DemocraticCoLearning, TriTraining)):
        log, stats, iteration = algoritmo.fit(x, y, x_test, y_test, datasetloader.get_only_features())
    else:
        log, stats, specific_stats, iteration = algoritmo.fit(x, y, x_test, y_test, datasetloader.get_only_features())

    print(log.to_string(), file=sys.stderr)

    if request.form['pca'] == 'on':
        _2d = log_pca_reduction(log,
                                datasetloader.get_only_features()).to_json()
    else:
        _2d = log_cxcy_reduction(log,
                                 request.form['cx'],
                                 request.form['cy'],
                                 datasetloader.get_only_features()).to_json()

    info = {'iterations': iteration,
            'log': _2d,
            'stats': stats.to_json(),
            'mapa': json.dumps(mapa)}

    if isinstance(algoritmo, (DemocraticCoLearning, TriTraining)):
        info = info | {'specific_stats': {key: specific_stats[key].to_json() for key in specific_stats}}

    return info


@app.template_filter()
def nombredataset(text):
    """Obtiene solo el nombre del conjunto de datos
    eliminando la ruta completa"""

    return re.split(r"\\", re.split(r"-", text)[0])[1]


def obtener_parametros_clasificador(clasificador, nombre):
    """A la hora de instanciar un clasificador (sklearn), este tiene una serie de parámetros
    (NO CONFUNDIR CON LOS PARÁMETROS DE LOS ALGORITMOS SEMI-SUPERVISADOS).
    Aclaración: estos vienen codificados en parametros.json.

    Interpreta el formulario de la configuración para obtener estos valores y que puedan ser
    desempaquetados con facilidad (**).
    """
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


if __name__ == '__main__':
    app.run(debug=True)
