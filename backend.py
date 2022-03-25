import pickle
import os


class Algorithms:
    # actual threshold ytbd
    ADMIT_THRESHOLD = 20

    # patient maintainance
    @staticmethod
    def generate_patient_id():
        return 1 + len(os.listdir('patients'))

    @staticmethod
    def save_patient(patient):
        with open(f"patients/{patient.id}.pickle", 'wb') as file:
            pickle.dump(patient, file)

    @staticmethod
    def load_patient(patient_id):
        with open(f"patients/{patient_id}.pickle", 'rb') as file:
            patient = pickle.load(file)
        return patient

    @staticmethod
    def load_all_patients():
        patient_list = []
        for id in os.listdir('patients'):
            patient_list.append(Algorithms.load_patient(id.strip('.pickle')))
        return patient_list

    @staticmethod
    def get_patients_from_hospital(hospital):
        patients = Algorithms.load_all_patients()
        patients_from_this_hospital = []

        for patient in patients:
            if patient.hospital == hospital:
                patients_from_this_hospital.append(patient)

        return patients_from_this_hospital

    # hospital maintainance
    @staticmethod
    def generate_hospital_id():
        return 1 + len(os.listdir('hospitals'))

    @staticmethod
    def save_hospital(hospital):
        with open(f"hospitals/{hospital.id}.pickle", 'wb') as file:
            pickle.dump(hospital, file)

    @staticmethod
    def load_hospital(hospital_id):
        with open(f"hospitals/{hospital_id}.pickle", 'rb') as file:
            hospital = pickle.load(file)
        return hospital

    @staticmethod
    def load_all_hospitals():
        hospital_list = []
        for id in os.listdir('hospitals'):
            hospital_list.append(Algorithms.load_hospital(id.strip('.pickle')))
        return hospital_list

    # hospital suggestion algorithms
    @staticmethod
    def sort_severity(patient_list, reversed=False):
        patient_list.sort(key=lambda patient: patient.get_severity_level(), reverse=reversed)
        return patient_list

    @staticmethod
    def get_manhattan_distance(obj1, obj2):
        if obj1 is None:
            return 0
        if type(obj1) == int:
            return abs(obj2.pincode - obj1)
        return abs(obj1.pincode - obj2.pincode)

    @staticmethod
    def most_vacant_hospital(hospital_list, pincode=None):
        most_vacant = hospital_list[0]
        for hospital in hospital_list:
            if hospital.current_free_beds > most_vacant.current_free_beds:
                most_vacant = hospital
                continue
            elif hospital.current_free_beds < most_vacant.current_free_beds:
                continue

            if Algorithms.get_manhattan_distance(pincode, hospital) < Algorithms.get_manhattan_distance(pincode,
                                                                                                        most_vacant):
                most_vacant = hospital

        return most_vacant

    @staticmethod
    def suggest_hospitals(patient_list, hospital_list):
        suggestions = {}
        for patient in patient_list:
            if patient.get_severity_level() < Algorithms.ADMIT_THRESHOLD:
                suggestions[patient] = None
                continue

            suggestions[patient] = Algorithms.most_vacant_hospital(hospital_list, patient.pincode)

        return suggestions


class Hospital:
    def __init__(self, id, name, pincode, addr, total_beds, free_beds):
        self.id = id
        self.name = name
        self.pincode = pincode
        self.address = addr
        self.total_beds = total_beds
        self.current_free_beds = free_beds
        self.patients = []

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other_hospital):
        if isinstance(other_hospital, Hospital):
            return self.id == other_hospital.id
        return False

    def admit_patient(self, patient):
        if self.current_free_beds == 0:
            return False

        self.patients.append(patient)
        self.current_free_beds -= 1
        patient.is_admit = True
        patient.hospital = self

        Algorithms.save_patient(patient)

    def discharge_patient(self, patient):
        if patient not in self.patients:
            raise Exception("Patient To Be Removed is Not in List!")

        self.current_free_beds += 1
        patient.is_admit = False
        patient.hospital = None
        self.patients.remove(patient)

        Algorithms.save_patient(patient)


class Patient:
    def __init__(self, id, name, age, gender, pincode, addr, phone_number, **health_params):
        '''

        Covid: [+]

        Fever: [90, 98.6], [98.6, 110]
        Cough: [0, 10]
        Breathlessness: [0, 10]
        Oxygen: [100, 0]
        HRCT: [0, 25]

        '''
        self.health = health_params
        for health_param in self.health:
            if health_param == "fever":
                self.health[health_param] = float(self.health[health_param])
                continue
            self.health[health_param] = int(self.health[health_param])

        # set patient credntials
        self.id = int(id)
        self.name = name
        self.age = int(age)
        self.gender = gender
        self.pincode = int(pincode)
        self.home_address = addr
        self.phone_number = int(phone_number)
        self.is_admit = False
        self.is_approved = False
        self.hospital = None

    def __repr__(self):
        return f"Patient: {self.name} | Age: {self.age}\n{self.health}"

    def __eq__(self, other):
        if not isinstance(other, Patient):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def get_manhattan_distance(self, hospital):
        return abs(hospital.pincode - self.pincode)

    def get_severity_level(self):
        ''' some heuristic function to calculate patient severity levels '''

        health_scores = {}

        # Fever
        if 97 <= self.health['fever'] <= 99:
            health_scores['fever'] = abs(self.health['fever'] - 98.4) * 10.0 / 1.4
        elif self.health['fever'] < 97:
            health_scores['fever'] = (abs(self.health['fever'] - 97) * 100.0 / 6.0) + 10.0
        else:
            health_scores['fever'] = (abs(self.health['fever'] - 99) * 100.0 / 9) + 6

        # Cough
        health_scores['cough'] = self.health['cough'] * 10

        # Breathlessness
        health_scores['breathlessness'] = self.health['breathlessness'] * 10

        # Oxygen Levels
        if self.health['oxygen'] >= 97:
            health_scores['oxygen'] = abs(self.health['oxygen'] - 100) * 5
        elif self.health['oxygen'] == 96:
            health_scores['oxygen'] = 35
        elif self.health['oxygen'] == 95:
            health_scores['oxygen'] = 55
        else:
            health_scores['oxygen'] = (abs(self.health['oxygen'] - 95) * 100 / 20) + 60

        # HRCT
        '''
        <7: mild
        8-17: moderate
        18+: severe

        for now, *4 is good enough
        '''
        # health_scores['hrct'] = self.health['hrct'] * 4
        if self.health['hrct'] <= 17:
            health_scores['hrct'] = self.health['hrct'] * 6
        else:
            health_scores['hrct'] = self.health['hrct'] * 5 + 15

        # caluclate severity levels
        return (
            0.20 * health_scores['breathlessness']
            + 0.45 * health_scores['hrct']
            + 0.40 * health_scores['oxygen']
            + 0.20 * health_scores['fever']
            + 0.20 * health_scores['cough']
        )


