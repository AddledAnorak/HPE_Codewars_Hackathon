from flask import Flask, render_template, request
from backend import *
import random

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    return render_template('client_index.html')


@app.route('/form-submitted', methods=['POST'])
def after_submission():
    patient_data = dict(request.form)
    patient = Patient(
        Algorithms.generate_patient_id(),
        patient_data['name-inp'],
        patient_data['age-inp'],
        patient_data['gender-inp'],
        patient_data['pincode-inp'],
        patient_data['addr-inp'],
        patient_data['phone-num-inp'],
        fever=patient_data['fever-inp'],
        cough=patient_data['cough-inp'],
        breathlessness=patient_data['breathlessness-inp'],
        oxygen=patient_data['oxygen-inp'],
        hrct=patient_data['hrct-inp']
    )

    Algorithms.save_patient(patient)

    return render_template('submission_successful.html')


if __name__ == "__main__":
    # app.run(port=random.randint(1000, 9000))
    app.run(port=8390)
