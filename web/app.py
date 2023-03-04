import os
import json

import datetime
import re
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_babel import Babel
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from algoritmos.utilidades.datasetloader import DatasetLoader
from algoritmos.utilidades.datasplitter import data_split
from algoritmos.utilidades.dimreduction import log_pca_reduction, log_cxcy_reduction
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.svm import SVC
from werkzeug.utils import secure_filename

from algoritmos import SelfTraining, DemocraticCoLearning
from algoritmos import CoTraining


def get_locale():
    return request.accept_languages.best_match(['es', 'en'])


app = Flask(__name__)
babel = Babel(app, locale_selector=get_locale)

app.secret_key = "ae4c977b14e2ecf38d485869018ec8f924b312132ee3d11d1ce755cdff9bc0af"
app.config.update(SESSION_COOKIE_SAMESITE='Strict')
app.config['CARPETA_DATASETS'] = 'datasets'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/', methods=['GET'])
def inicio():
    session.pop('ALGORITMO', None)
    session.pop('FICHERO', None)
    return render_template('inicio.html')


@app.route('/seleccionar/<algoritmo>')
def seleccionar_algoritmo(algoritmo=None):
    session['ALGORITMO'] = algoritmo
    return redirect(url_for('subida'))


@app.route('/subida', methods=['GET', 'POST'])
def subida():
    if 'ALGORITMO' not in session:
        flash("Debe seleccionar un algoritmo")
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
        flash("Debe subir un fichero")
        return redirect(url_for('subida'))

    dl = DatasetLoader(session['FICHERO'])
    with open("static/parametros.json") as f:
        clasificadores = json.load(f)

    return render_template(algoritmo + 'config.html', caracteristicas=dl.get_allfeatures(),
                           clasificadores=list(clasificadores.keys()), parametros=clasificadores)


@app.route('/selftraining', methods=['GET', 'POST'])
def selftraining():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect(url_for('configurar_algoritmo', algoritmo='selftraining'))

    with open("static/parametros.json") as f:
        clasificadores = json.load(f)

    clasificador = request.form['clasificador']
    parametros_clasificador = clasificadores[clasificador]

    params = [
        {"nombre": "clasificador", "valor": request.form['clasificador']},
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

    for key in parametros_clasificador.keys():
        params.append({"nombre": key, "valor": request.form.get(key, -1)})

    return render_template('selftraining.html',
                           params=params,
                           cx=request.form.get('cx', 'C1'),
                           cy=request.form.get('cy', 'C2'))


@app.route('/cotraining', methods=['GET', 'POST'])
def cotraining():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect(url_for('configurar_algoritmo', algoritmo='cotraining'))

    params = {"p": request.form.get('p', -1),
              "n": request.form.get('n', -1),
              "u": request.form.get('u', -1),
              "n_iter": request.form.get('n_iter'),
              "target": request.form.get('target'),
              "cx": request.form.get('cx', 'C1'),
              "cy": request.form.get('cy', 'C2'),
              "pca": request.form.get('pca', 'off'),
              "p_unlabelled": request.form.get('p_unlabelled', -1),
              "p_test": request.form.get('p_test', -1)
              }

    return render_template('cotraining.html', **params)


@app.route('/democraticcolearning', methods=['GET', 'POST'])
def democraticcolearning():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect(url_for('configurar_algoritmo', algoritmo='democraticcolearning'))

    params = {"clasificador1": request.form['clasificador1'],
              "clasificador2": request.form['clasificador2'],
              "clasificador3": request.form['clasificador3'],
              "target": request.form.get('target'),
              "cx": request.form.get('cx', 'C1'),
              "cy": request.form.get('cy', 'C2'),
              "pca": request.form.get('pca', 'off'),
              "p_unlabelled": request.form.get('p_unlabelled', -1),
              "p_test": request.form.get('p_test', -1)
              }

    return render_template('democraticcolearning.html', **params)


@app.route('/selftrainingd', methods=['GET', 'POST'])
def datosselftraining():
    clasificador = request.form['clasificador']

    with open("static/parametros.json") as f:
        clasificadores = json.load(f)

    parametros_clasificador = {}
    for key in clasificadores[clasificador].keys():
        try:
            p = float(request.form[key])
            parametros_clasificador[key] = p
        except ValueError:
            parametros_clasificador[key] = request.form[key]

    n = int(request.form['n'])
    th = float(request.form['th'])
    n_iter = int(request.form['n_iter'])
    cx = request.form['cx']
    cy = request.form['cy']
    pca = request.form['pca']
    p_unlabelled = float(request.form['p_unlabelled'])
    p_test = float(request.form['p_test'])

    clf = SVC(kernel='rbf',
              probability=True,
              C=1.0,
              gamma='scale',
              random_state=0
              )

    st = SelfTraining(clf=obtener_clasificador(clasificador, parametros_clasificador),
                      n=n if n != -1 else None,
                      th=th if th != -1 else None,
                      n_iter=n_iter)

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, is_unlabelled = dl.get_x_y()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=p_unlabelled, p_test=p_test)

    log, stats, iteration = st.fit(x, y, x_test, y_test, dl.get_only_features())

    if pca == 'on':
        _2d = log_pca_reduction(log, dl.get_only_features()).to_json()
    else:
        _2d = log_cxcy_reduction(log, cx, cy, dl.get_only_features()).to_json()

    info = {'iterations': iteration,
            'log': _2d,
            'stats': stats.to_json(),
            'mapa': json.dumps(mapa)}

    return json.dumps(info)


@app.route('/cotrainingd', methods=['GET', 'POST'])
def datoscotraining():
    p = int(request.form['p'])
    n = int(request.form['n'])
    u = int(request.form['u'])
    n_iter = int(request.form['n_iter'])
    cx = request.form['cx']
    cy = request.form['cy']
    pca = request.form['pca']
    p_unlabelled = float(request.form['p_unlabelled'])
    p_test = float(request.form['p_test'])

    clf1 = SVC(kernel='rbf',
               probability=True,
               C=1.0,
               gamma='scale',
               random_state=0
               )
    clf2 = SVC(kernel='rbf',
               probability=True,
               C=1.0,
               gamma='scale',
               random_state=0
               )

    ct = CoTraining(clf1=clf1,
                    clf2=clf2,
                    p=p,
                    n=n,
                    u=u,
                    n_iter=n_iter)

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, is_unlabelled = dl.get_x_y()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=p_unlabelled, p_test=p_test)

    log, stats, iteration = ct.fit(x, y, x_test, y_test, dl.get_only_features())

    if pca == 'on':
        _2d = log_pca_reduction(log, dl.get_only_features()).to_json()
    else:
        _2d = log_cxcy_reduction(log, cx, cy, dl.get_only_features()).to_json()

    info = {'iterations': iteration,
            'log': _2d,
            'stats': stats.to_json(),
            'mapa': json.dumps(mapa)}
    return json.dumps(info)


@app.route('/democraticcolearningd', methods=['GET', 'POST'])
def datosdemocraticcolearning():
    clasificador1 = request.form['clasificador1']
    clasificador2 = request.form['clasificador2']
    clasificador3 = request.form['clasificador3']
    cx = request.form['cx']
    cy = request.form['cy']
    pca = request.form['pca']
    p_unlabelled = float(request.form['p_unlabelled'])
    p_test = float(request.form['p_test'])

    clf1 = obtener_clasificador(clasificador1)
    clf2 = obtener_clasificador(clasificador2)
    clf3 = obtener_clasificador(clasificador3)

    dcl = DemocraticCoLearning([clf1, clf2, clf3])

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, is_unlabelled = dl.get_x_y()

    (
        x,
        y,
        x_test,
        y_test
    ) = data_split(x, y, is_unlabelled, p_unlabelled=p_unlabelled, p_test=p_test)

    log, iteration = dcl.fit(x, y, x_test, y_test, dl.get_only_features())

    if pca == 'on':
        _2d = log_pca_reduction(log, dl.get_only_features()).to_json()
    else:
        _2d = log_cxcy_reduction(log, cx, cy, dl.get_only_features()).to_json()

    info = {'iterations': iteration,
            'log': _2d,
            'mapa': json.dumps(mapa)}

    return json.dumps(info)


@app.template_filter()
def nombredataset(text):
    """Obtiene solo el nombre del conjunto de datos
    eliminando la ruta completa"""

    return re.split(r"-|\\", text)[1]


def obtener_clasificador(nombre, params):
    if nombre == "SVC":
        params = params | {"probability": True}
        return SVC(**params)
    elif nombre == "GaussianNB":
        return GaussianNB(**params)
    elif nombre == "KNeighborsClassifier":
        return KNeighborsClassifier(**params)
    elif nombre == "DecisionTreeClassifier":
        return DecisionTreeClassifier(**params)


if __name__ == '__main__':
    app.run(debug=True)
