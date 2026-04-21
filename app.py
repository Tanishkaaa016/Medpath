from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

SYMPTOM_DISEASE_MAP = {
    "fever": ["Pneumonia", "COVID-19", "Malaria", "Dengue Fever", "Typhoid"],
    "cough": ["Pneumonia", "COVID-19", "Bronchitis"],
    "shortness of breath": ["Pneumonia", "COVID-19", "Heart Attack"],
    "chest pain": ["Heart Attack", "Pneumonia", "Angina"],
    "fatigue": ["Anemia", "Diabetes", "COVID-19", "Pneumonia", "Dengue Fever"],
    "headache": ["Migraine", "Hypertension", "Dengue Fever", "Malaria"],
    "nausea": ["Appendicitis", "Migraine", "Dengue Fever", "Malaria"],
    "body ache": ["Dengue Fever", "Malaria", "COVID-19"],
    "joint pain": ["Dengue Fever", "Malaria"],
    "abdominal pain": ["Appendicitis", "Diabetes", "Malaria"],
    "increased thirst": ["Diabetes"],
    "frequent urination": ["Diabetes"],
    "blurred vision": ["Diabetes", "Hypertension", "Migraine"],
    "rash": ["Dengue Fever"],
    "vomiting": ["Appendicitis", "Migraine", "Malaria", "Dengue Fever"],
    "dizziness": ["Anemia", "Hypertension", "Migraine"],
    "pale skin": ["Anemia"],
    "cold sweats": ["Heart Attack", "Malaria"],
    "sensitivity to light": ["Migraine"],
    "sore throat": ["COVID-19"],
    "loss of taste": ["COVID-19"],
    "chills": ["Malaria", "Pneumonia", "Dengue Fever"],
    "high blood pressure": ["Hypertension"],
    "palpitations": ["Heart Attack", "Hypertension"],
    "weakness": ["Anemia", "Diabetes", "Dengue Fever"],
    "sweating": ["Malaria", "Heart Attack", "Diabetes"],
    "loss of appetite": ["Dengue Fever", "Appendicitis", "Malaria"],
    "back pain": ["Kidney Disease", "Appendicitis"],
    "yellowing of skin": ["Dengue Fever", "Malaria"],
    "rapid heartbeat": ["Heart Attack", "Hypertension", "Anemia"],
}

DISEASE_PATHS = {
    "Pneumonia": {
        "severity": "High",
        "color": "#ff6b35",
        "icon": "🫁",
        "description": "Bacterial or viral lung infection causing fluid in air sacs, impairing gas exchange.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Elevated WBC indicates infection", "icon": "🩸"},
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Visualize lung consolidation and opacities", "icon": "📷"},
            ],
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Primary imaging modality", "icon": "📷"},
                {"test": "Sputum Culture", "cost": 600, "time_hrs": 48, "purpose": "Identify causative bacterial organism", "icon": "🔬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "WBC and inflammatory markers", "icon": "🩸"},
                {"test": "C-Reactive Protein", "cost": 350, "time_hrs": 6, "purpose": "Quantify systemic inflammation", "icon": "⚗️"},
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Confirm pneumonic infiltrate", "icon": "📷"},
                {"test": "Blood Culture", "cost": 800, "time_hrs": 72, "purpose": "Rule out bacteremia", "icon": "🧪"},
            ],
        ]
    },
    "COVID-19": {
        "severity": "High",
        "color": "#7c3aed",
        "icon": "🦠",
        "description": "SARS-CoV-2 coronavirus respiratory illness affecting lungs and multiple organ systems.",
        "paths": [
            [
                {"test": "RT-PCR Test", "cost": 1500, "time_hrs": 24, "purpose": "Gold standard nucleic acid detection", "icon": "🧬"},
            ],
            [
                {"test": "Rapid Antigen Test", "cost": 300, "time_hrs": 0.5, "purpose": "Quick initial COVID screening", "icon": "⚡"},
                {"test": "RT-PCR Test", "cost": 1500, "time_hrs": 24, "purpose": "Confirmatory test for antigen positive", "icon": "🧬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Check lymphopenia pattern", "icon": "🩸"},
                {"test": "CT Scan (Chest)", "cost": 3000, "time_hrs": 2, "purpose": "Ground-glass opacities visualization", "icon": "🖥️"},
                {"test": "RT-PCR Test", "cost": 1500, "time_hrs": 24, "purpose": "Definitive molecular confirmation", "icon": "🧬"},
            ],
        ]
    },
    "Malaria": {
        "severity": "High",
        "color": "#059669",
        "icon": "🦟",
        "description": "Plasmodium parasite infection from Anopheles mosquito bite affecting red blood cells.",
        "paths": [
            [
                {"test": "Rapid Diagnostic Test (RDT)", "cost": 200, "time_hrs": 1, "purpose": "Plasmodium antigen detection", "icon": "⚡"},
                {"test": "Peripheral Blood Smear", "cost": 300, "time_hrs": 4, "purpose": "Microscopic species identification", "icon": "🔬"},
            ],
            [
                {"test": "Peripheral Blood Smear", "cost": 300, "time_hrs": 4, "purpose": "Direct parasite visualization", "icon": "🔬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Hemolytic anemia and thrombocytopenia", "icon": "🩸"},
                {"test": "Rapid Diagnostic Test (RDT)", "cost": 200, "time_hrs": 1, "purpose": "Rapid malaria antigen confirmation", "icon": "⚡"},
                {"test": "PCR for Malaria", "cost": 1200, "time_hrs": 12, "purpose": "Definitive species identification", "icon": "🧬"},
            ],
        ]
    },
    "Dengue Fever": {
        "severity": "High",
        "color": "#dc2626",
        "icon": "🌡️",
        "description": "Aedes mosquito-borne viral fever causing platelet drop and potential hemorrhage.",
        "paths": [
            [
                {"test": "NS1 Antigen Test", "cost": 500, "time_hrs": 4, "purpose": "Early dengue detection (Days 1–5)", "icon": "🧫"},
                {"test": "Dengue IgM/IgG", "cost": 600, "time_hrs": 6, "purpose": "Serological confirmation of infection", "icon": "🔬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Platelet count monitoring", "icon": "🩸"},
                {"test": "NS1 Antigen Test", "cost": 500, "time_hrs": 4, "purpose": "Early viral antigen detection", "icon": "🧫"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Monitor platelets and hematocrit", "icon": "🩸"},
                {"test": "NS1 Antigen Test", "cost": 500, "time_hrs": 4, "purpose": "Dengue antigen detection", "icon": "🧫"},
                {"test": "Liver Function Tests", "cost": 700, "time_hrs": 8, "purpose": "Assess hepatic involvement", "icon": "⚗️"},
            ],
        ]
    },
    "Heart Attack": {
        "severity": "Critical",
        "color": "#ff0040",
        "icon": "❤️",
        "description": "Myocardial infarction — coronary artery blockage causing cardiac muscle necrosis.",
        "paths": [
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "ST elevation / LBBB detection", "icon": "📈"},
                {"test": "Troponin I/T Test", "cost": 800, "time_hrs": 1, "purpose": "Cardiac muscle damage biomarker", "icon": "🩸"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Immediate cardiac rhythm assessment", "icon": "📈"},
                {"test": "Troponin I/T Test", "cost": 800, "time_hrs": 1, "purpose": "Confirm myocardial injury", "icon": "🩸"},
                {"test": "Echocardiogram", "cost": 2000, "time_hrs": 2, "purpose": "Wall motion abnormality evaluation", "icon": "🫀"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Initial cardiac screening", "icon": "📈"},
                {"test": "Troponin I/T Test", "cost": 800, "time_hrs": 1, "purpose": "Cardiac enzymes elevation", "icon": "🩸"},
                {"test": "Coronary Angiography", "cost": 15000, "time_hrs": 3, "purpose": "Visualize coronary artery blockage", "icon": "🔍"},
            ],
        ]
    },
    "Diabetes": {
        "severity": "Medium",
        "color": "#0891b2",
        "icon": "🩺",
        "description": "Metabolic disorder with chronic hyperglycemia due to insulin resistance or deficiency.",
        "paths": [
            [
                {"test": "Fasting Blood Glucose", "cost": 150, "time_hrs": 8, "purpose": "Screen for hyperglycemia", "icon": "💉"},
                {"test": "HbA1c Test", "cost": 400, "time_hrs": 6, "purpose": "3-month average glucose level", "icon": "🩸"},
            ],
            [
                {"test": "Fasting Blood Glucose", "cost": 150, "time_hrs": 8, "purpose": "Initial glucose measurement", "icon": "💉"},
                {"test": "Oral Glucose Tolerance Test", "cost": 350, "time_hrs": 3, "purpose": "Assess glucose metabolism curve", "icon": "📊"},
                {"test": "HbA1c Test", "cost": 400, "time_hrs": 6, "purpose": "Long-term glycemic control", "icon": "🩸"},
            ],
            [
                {"test": "Random Blood Glucose", "cost": 100, "time_hrs": 1, "purpose": "Immediate glucose screening", "icon": "⚡"},
                {"test": "HbA1c Test", "cost": 400, "time_hrs": 6, "purpose": "Confirm chronic diabetes", "icon": "🩸"},
                {"test": "Urine Microalbumin", "cost": 500, "time_hrs": 4, "purpose": "Early diabetic nephropathy detection", "icon": "🧪"},
            ],
        ]
    },
    "Appendicitis": {
        "severity": "Critical",
        "color": "#f59e0b",
        "icon": "⚠️",
        "description": "Inflamed appendix requiring urgent surgical intervention to prevent perforation.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Leukocytosis indicates infection", "icon": "🩸"},
                {"test": "Ultrasound Abdomen", "cost": 800, "time_hrs": 1, "purpose": "Appendix visualization and graded compression", "icon": "📡"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "WBC count for acute infection", "icon": "🩸"},
                {"test": "CT Scan Abdomen", "cost": 3000, "time_hrs": 2, "purpose": "Definitive appendicitis diagnosis", "icon": "🖥️"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Initial infection markers", "icon": "🩸"},
                {"test": "C-Reactive Protein", "cost": 350, "time_hrs": 6, "purpose": "Inflammation confirmation", "icon": "⚗️"},
                {"test": "Ultrasound Abdomen", "cost": 800, "time_hrs": 1, "purpose": "Real-time appendix imaging", "icon": "📡"},
                {"test": "CT Scan Abdomen", "cost": 3000, "time_hrs": 2, "purpose": "Pre-surgical planning", "icon": "🖥️"},
            ],
        ]
    },
    "Migraine": {
        "severity": "Medium",
        "color": "#8b5cf6",
        "icon": "🧠",
        "description": "Neurological disorder causing recurring severe headaches with aura and sensory disturbances.",
        "paths": [
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Clinical migraine assessment", "icon": "🩺"},
                {"test": "MRI Brain", "cost": 5000, "time_hrs": 2, "purpose": "Exclude structural causes", "icon": "🧲"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Assess headache pattern and triggers", "icon": "🩺"},
            ],
            [
                {"test": "Blood Pressure Measurement", "cost": 50, "time_hrs": 0.1, "purpose": "Rule out hypertensive headache", "icon": "💊"},
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Comprehensive neuro assessment", "icon": "🩺"},
                {"test": "CT Scan Brain", "cost": 2500, "time_hrs": 1, "purpose": "Exclude secondary pathology", "icon": "🖥️"},
            ],
        ]
    },
    "Anemia": {
        "severity": "Medium",
        "color": "#e879f9",
        "icon": "💊",
        "description": "Deficiency in RBCs or hemoglobin reducing oxygen-carrying capacity of blood.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Hemoglobin, hematocrit, MCV measurement", "icon": "🩸"},
                {"test": "Iron Studies", "cost": 600, "time_hrs": 6, "purpose": "Serum iron, ferritin, TIBC", "icon": "⚗️"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "RBC indices and morphology", "icon": "🩸"},
                {"test": "Peripheral Blood Smear", "cost": 300, "time_hrs": 4, "purpose": "RBC shape and size analysis", "icon": "🔬"},
                {"test": "Vitamin B12 / Folate", "cost": 700, "time_hrs": 8, "purpose": "Nutritional deficiency assessment", "icon": "💊"},
            ],
        ]
    },
    "Hypertension": {
        "severity": "Medium",
        "color": "#f97316",
        "icon": "💓",
        "description": "Persistently elevated arterial blood pressure causing cardiovascular organ damage.",
        "paths": [
            [
                {"test": "Blood Pressure Measurement", "cost": 50, "time_hrs": 0.1, "purpose": "Confirm persistent BP elevation", "icon": "🩺"},
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Left ventricular hypertrophy detection", "icon": "📈"},
                {"test": "Lipid Profile", "cost": 400, "time_hrs": 6, "purpose": "Cardiovascular risk stratification", "icon": "⚗️"},
            ],
            [
                {"test": "Blood Pressure Measurement", "cost": 50, "time_hrs": 0.1, "purpose": "Primary hypertension diagnosis", "icon": "🩺"},
                {"test": "Kidney Function Tests", "cost": 500, "time_hrs": 6, "purpose": "Exclude renovascular hypertension", "icon": "🧪"},
            ],
        ]
    },
}


def build_all_paths(disease_name):
    paths = DISEASE_PATHS[disease_name]["paths"]
    result = []
    for i, path in enumerate(paths):
        result.append({
            "path_id": i + 1,
            "nodes": ["START"] + [t["test"] for t in path] + [f"✓ {disease_name}"],
            "tests": path,
            "total_cost": sum(t["cost"] for t in path),
            "total_time": round(sum(t["time_hrs"] for t in path), 1),
            "num_tests": len(path)
        })
    return result


def bfs_optimal(disease_name):
    paths = build_all_paths(disease_name)
    return min(paths, key=lambda p: p["num_tests"])


def ucs_optimal(disease_name):
    paths = build_all_paths(disease_name)
    return min(paths, key=lambda p: p["total_cost"])


def astar_optimal(disease_name):
    paths = build_all_paths(disease_name)
    # A* heuristic: cost + time penalty (time * 50 INR equivalent urgency cost)
    return min(paths, key=lambda p: p["total_cost"] + p["total_time"] * 50)


def get_candidate_diseases(symptoms):
    symptoms_lower = [s.lower().strip() for s in symptoms]
    scores = {}
    matched_symptoms = {}

    for symptom in symptoms_lower:
        for known_sym, diseases in SYMPTOM_DISEASE_MAP.items():
            if symptom in known_sym or known_sym in symptom or known_sym == symptom:
                for disease in diseases:
                    if disease in DISEASE_PATHS:
                        scores[disease] = scores.get(disease, 0) + 1
                        if disease not in matched_symptoms:
                            matched_symptoms[disease] = []
                        if known_sym not in matched_symptoms[disease]:
                            matched_symptoms[disease].append(known_sym)

    sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_diseases[:5], matched_symptoms


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', [])
    algorithm = data.get('algorithm', 'bfs')

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    candidates, matched = get_candidate_diseases(symptoms)

    if not candidates:
        return jsonify({"error": "No matching diseases found. Try different symptoms."}), 404

    results = []
    for disease, score in candidates:
        info = DISEASE_PATHS[disease]
        all_paths = build_all_paths(disease)

        if algorithm == 'bfs':
            optimal = bfs_optimal(disease)
            algo_label = "BFS — Minimum Tests"
        elif algorithm == 'ucs':
            optimal = ucs_optimal(disease)
            algo_label = "UCS — Minimum Cost"
        else:
            optimal = astar_optimal(disease)
            algo_label = "A* — Optimal Speed + Cost"

        total_diseases = len(SYMPTOM_DISEASE_MAP)
        confidence = min(95, round((score / max(len(symptoms), 1)) * 80 + 15))

        results.append({
            "disease": disease,
            "confidence": confidence,
            "severity": info["severity"],
            "color": info["color"],
            "icon": info["icon"],
            "description": info["description"],
            "algorithm": algo_label,
            "optimal_path": optimal,
            "all_paths": all_paths,
            "matched_symptoms": matched.get(disease, []),
        })

    return jsonify({
        "symptoms": symptoms,
        "algorithm": algorithm,
        "results": results,
        "top_diagnosis": results[0] if results else None
    })


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({"symptoms": sorted(SYMPTOM_DISEASE_MAP.keys())})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
