import pandas as pd
from algorithms.selftrainingclass import SelfTraining
from flask import Flask, render_template
from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
from utilidades import log_dim_reduction

app = Flask(__name__)


@app.route('/selftraining', methods=['GET'])
def selftraining():
    return render_template('selftraining.html')


@app.route('/datosselftraining', methods=['GET'])
def datosselftraining():
    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

    st = SelfTraining(clf=SVC(kernel='rbf',
                              probability=True,
                              C=1.0,
                              gamma='scale',
                              random_state=0
                              ), n=80)

    log, it = st.fit(x, y)
    return log_dim_reduction(log).to_json()


if __name__ == '__main__':
    app.run(debug=True)
