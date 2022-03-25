from flask import Flask, render_template, request
from backend import *

app = Flask(__name__, template_folder='hospital_templates', static_folder='static')
this_hospital = Algorithms.load_hospital(1)
new_patients = []
existing_patients = []


@app.route('/')
def index():
    global new_patients, existing_patients

    new_patients = []
    existing_patients = []

    all_patients = Algorithms.get_patients_from_hospital(this_hospital)

    for patient in all_patients:
        if patient.is_admit:
            existing_patients.append(patient)
        else:
            new_patients.append(patient)

    return render_template('hospital_index.html', existing_patients=existing_patients, new_patients=new_patients, hospital=this_hospital)


@app.route('/admit-patient', methods=['POST'])
def admit_patient():
    global this_hospital

    # the form obj should be like: {'admit': id}
    patient_id = dict(request.form)['admit']
    patient_to_be_admitted = Algorithms.load_patient(patient_id)

    assert patient_to_be_admitted in new_patients

    new_patients.remove(patient_to_be_admitted)
    existing_patients.append(patient_to_be_admitted)

    this_hospital.admit_patient(patient_to_be_admitted)
    Algorithms.save_hospital(this_hospital)

    return render_template('hospital_index.html', existing_patients=existing_patients, new_patients=new_patients, hospital=this_hospital)


@app.route('/remove-patient', methods=['POST'])
def remove_patient():
    global this_hospital

    # the form obj should be like: {'remove': id}
    patient_id = dict(request.form)['remove']
    patient_to_be_removed = Algorithms.load_patient(patient_id)

    assert patient_to_be_removed in existing_patients

    existing_patients.remove(patient_to_be_removed)
    this_hospital.discharge_patient(patient_to_be_removed)

    Algorithms.save_hospital(this_hospital)

    return render_template('hospital_index.html', existing_patients=existing_patients, new_patients=new_patients, hospital=this_hospital)



if __name__ == "__main__":
    app.run(port=4289)