from flask import Flask, render_template, request, redirect
from backend import *
import random

app = Flask(__name__, template_folder='server_templates', static_folder='static')
suggestions = {}
hospital_list = []


@app.route('/')
def index():
    global suggestions, hospital_list
    unadmitted_patient_list = [patient for patient in Algorithms.load_all_patients() if not patient.is_approved]
    hospital_list = Algorithms.load_all_hospitals()
    suggestions = Algorithms.suggest_hospitals(unadmitted_patient_list, hospital_list)

    return render_template('server_index.html', suggestion_list=suggestions, num_patients=len(suggestions), hospital_list=hospital_list)


@app.route('/approve-patients', methods=['POST'])
def approve_patients():
    global suggestions, hospital_list

    patient_id, hospital_id = list(dict(request.form).items())[0]
    patient = Algorithms.load_patient(patient_id)

    if not hospital_id == 'home-isolation':
        hospital = Algorithms.load_hospital(hospital_id)
        patient.hospital = hospital

    patient.is_approved = True
    Algorithms.save_patient(patient)

    del suggestions[patient]

    return render_template('server_index.html', suggestion_list=suggestions, num_patients=len(suggestions), hospital_list=hospital_list)






if __name__ == "__main__":
    # app.run(port=random.randint(1000, 9000))
    app.run(port=2378)