import json
import os

from flask import flash, render_template, request, redirect, session, url_for, Blueprint, current_app, abort, jsonify
from flask_babel import gettext
from flask_login import login_required, current_user

from .models import Run

visualization_bp = Blueprint('visualization_bp', __name__)


@visualization_bp.route('/<algoritmo>', methods=['POST'])
def visualizar_algoritmo(algoritmo):
    """Centraliza la carga de la página de visualización.
    Es el paso siguiente después de la configuración.
    """
    if 'target' not in request.form:
        flash(gettext("You must select the parameters of the algorithm"))
        return redirect(url_for('configuration_bp.configurar_algoritmo', algoritmo="None"))

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

    return render_template('visualizacion/' + session['ALGORITMO'] + '.html',
                           params=params,
                           cx=request.form.get('cx', 'C1'),
                           cy=request.form.get('cy', 'C2'),
                           ejecutar=True)


@visualization_bp.route('/<algoritmo>/<run_id>', methods=['GET'])
@login_required
def visualizar_algoritmo_json(algoritmo, run_id):
    run = Run.query.filter(Run.id == run_id).first()

    if not run:
        abort(404)

    if run.user_id != current_user.id:
        abort(401)

    session['ALGORITMO'] = algoritmo
    session['FICHERO'] = os.path.join(current_app.config['CARPETA_DATASETS'], run.filename)

    with open(os.path.join(current_app.config['CARPETA_RUNS'], run.jsonfile)) as f:
        json_data = json.load(f)

    return render_template('visualizacion/' + algoritmo + '.html',
                           params=[],
                           cx=run.cx,
                           cy=run.cy,
                           ejecutar=False,
                           json_data=json_data)


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
        {"nombre": "norm", "valor": request.form.get('norm', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled')},
        {"nombre": "p_test", "valor": request.form.get('p_test')},
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
        {"nombre": "norm", "valor": request.form.get('norm', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled')},
        {"nombre": "p_test", "valor": request.form.get('p_test')},
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
        {"nombre": "norm", "valor": request.form.get('norm', 'off')},
        {"nombre": "p_unlabelled", "valor": request.form.get('p_unlabelled')},
        {"nombre": "p_test", "valor": request.form.get('p_test')},
    ]

    # Los parámetros anteriores no incluyen los propios parámetros de los clasificadores
    # (SVM, GaussianNB...), esta función lo incluye
    incorporar_clasificadores_params([clasificador1, clasificador2, clasificador3], params)

    return params


def incorporar_clasificadores_params(nombre_clasificadores, params):
    """Incluye los parámetros de los propios clasificadores
    a la lista de parámetros generales.
    """

    with open(os.path.join(os.path.dirname(__file__), os.path.normpath("static/json/parametros.json"))) as f:
        clasificadores = json.load(f)

    for i, clasificador in enumerate(nombre_clasificadores):
        for key in clasificadores[clasificador].keys():
            params.append({"nombre": f"clasificador{i + 1}_" + key,
                           "valor": request.form.get(f"clasificador{i + 1}_" + key, -1)})
