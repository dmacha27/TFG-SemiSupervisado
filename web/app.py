import os
import json

import pandas as pd
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.svm import SVC
from werkzeug.utils import secure_filename

from algoritmos import SelfTraining
from algoritmos import CoTraining
from algoritmos.utilidades import DatasetLoader
from algoritmos.utilidades import log_dim_reduction

app = Flask(__name__)
app.config.update(SESSION_COOKIE_SAMESITE='Strict')
app.config['CARPETA_DATASETS'] = 'datasets'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/', methods=['GET'])
def inicio():
    session.clear()
    return render_template('inicio.html')


@app.route('/sel_selftraining')
def sel_selftraining():
    session['ALGORITMO'] = 'selftraining'
    return redirect('/subida')


@app.route('/subida', methods=['GET', 'POST'])
def subida():
    if request.method == 'POST':

        file = request.files['archivo']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            session['FICHERO'] = os.path.join(app.config['CARPETA_DATASETS'], filename)
            file.save(os.path.join(app.config['CARPETA_DATASETS'], filename))

    return render_template('subida.html', alg=session['ALGORITMO'])


@app.route('/selftrainingc', methods=['GET'])
def configuracion():
    dl = DatasetLoader(session['FICHERO'])
    return render_template('selftrainingconfig.html', caracteristicas=dl.features())


@app.route('/selftraining', methods=['GET', 'POST'])
def selftraining():
    return render_template('selftraining.html', n=request.form['n'],
                           th=request.form['th'], n_iter=request.form['n_iter'], target=request.form['target'])


@app.route('/selftrainingd', methods=['GET', 'POST'])
def datosselftraining():
    n = int(request.form['n'])
    th = int(request.form['th'])
    n_iter = int(request.form['n_iter'])

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, _ = dl.get_x_y()
    print(mapa)
    st = SelfTraining(clf=SVC(kernel='rbf',
                              probability=True,
                              C=1.0,
                              gamma='scale',
                              random_state=0
                              ), n=n, n_iter=n_iter)

    log, it = st.fit(x, y)

    info = {'log': log_dim_reduction(log).to_json(),
            'mapa': json.dumps(mapa)}

    return json.dumps(info)


@app.route('/cotrainingd', methods=['GET'])
def datoscotraining():
    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

    st = CoTraining(clf1=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ),
                    clf2=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ), p=1, n=3, u=30, n_iter=100)

    log, it = st.fit(x, y)
    return log_dim_reduction(log).to_json()


if __name__ == '__main__':
    app.run(debug=True)
