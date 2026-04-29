from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# =============================================================================
#  SYMPTOM -> DISEASE MAP  (expanded with neuro, autoimmune, onco, endocrine)
# =============================================================================
SYMPTOM_DISEASE_MAP = {
    # ---- Original symptoms (kept + extended with new diseases) ----
    "fever": ["Pneumonia", "COVID-19", "Malaria", "Dengue Fever", "Typhoid",
              "Tuberculosis", "Endocarditis", "Meningitis", "Leukemia", "Lymphoma",
              "Pyelonephritis", "Cholecystitis"],
    "cough": ["Pneumonia", "COVID-19", "Bronchitis", "Tuberculosis", "Asthma",
              "Lung Cancer", "Sarcoidosis", "Pulmonary Embolism"],
    "shortness of breath": ["Pneumonia", "COVID-19", "Heart Attack", "Asthma",
                            "Pulmonary Embolism", "Heart Failure", "Lung Cancer",
                            "Sarcoidosis", "Tuberculosis"],
    "chest pain": ["Heart Attack", "Pneumonia", "Angina", "Pulmonary Embolism",
                   "GERD", "Pericarditis", "Aortic Dissection"],
    "fatigue": ["Anemia", "Diabetes", "COVID-19", "Pneumonia", "Dengue Fever",
                "Hypothyroidism", "Lupus", "Multiple Sclerosis", "Leukemia",
                "Lymphoma", "Heart Failure", "Chronic Kidney Disease",
                "Liver Cirrhosis", "Tuberculosis", "Addison's Disease"],
    "headache": ["Migraine", "Hypertension", "Dengue Fever", "Malaria",
                 "Meningitis", "Stroke", "Brain Tumor", "Hyperthyroidism"],
    "nausea": ["Appendicitis", "Migraine", "Dengue Fever", "Malaria",
               "Pancreatitis", "Cholecystitis", "Meningitis", "Pyelonephritis",
               "GERD", "Heart Attack"],
    "body ache": ["Dengue Fever", "Malaria", "COVID-19", "Lupus",
                  "Rheumatoid Arthritis", "Lymphoma", "Tuberculosis"],
    "joint pain": ["Dengue Fever", "Malaria", "Rheumatoid Arthritis", "Lupus",
                   "Gout", "Sarcoidosis"],
    "abdominal pain": ["Appendicitis", "Diabetes", "Malaria", "Crohn's Disease",
                       "Pancreatitis", "Cholecystitis", "Liver Cirrhosis",
                       "Pyelonephritis", "Ovarian Cancer"],
    "increased thirst": ["Diabetes"],
    "frequent urination": ["Diabetes", "UTI", "Pyelonephritis"],
    "blurred vision": ["Diabetes", "Hypertension", "Migraine", "Multiple Sclerosis",
                       "Stroke", "Brain Tumor"],
    "rash": ["Dengue Fever", "Lupus", "Meningitis"],
    "vomiting": ["Appendicitis", "Migraine", "Malaria", "Dengue Fever",
                 "Pancreatitis", "Meningitis", "Cholecystitis", "Pyelonephritis"],
    "dizziness": ["Anemia", "Hypertension", "Migraine", "Stroke",
                  "Heart Failure", "Brain Tumor"],
    "pale skin": ["Anemia", "Leukemia", "Chronic Kidney Disease"],
    "cold sweats": ["Heart Attack", "Malaria", "Pulmonary Embolism"],
    "sensitivity to light": ["Migraine", "Meningitis"],
    "sore throat": ["COVID-19", "Lymphoma"],
    "loss of taste": ["COVID-19"],
    "chills": ["Malaria", "Pneumonia", "Dengue Fever", "Endocarditis",
               "Pyelonephritis", "Cholecystitis"],
    "high blood pressure": ["Hypertension", "Chronic Kidney Disease"],
    "palpitations": ["Heart Attack", "Hypertension", "Hyperthyroidism",
                     "Heart Failure", "Anemia"],
    "weakness": ["Anemia", "Diabetes", "Dengue Fever", "Stroke",
                 "Multiple Sclerosis", "Guillain-Barre Syndrome",
                 "Addison's Disease", "Hypothyroidism", "Leukemia"],
    "sweating": ["Malaria", "Heart Attack", "Diabetes", "Hyperthyroidism",
                 "Tuberculosis", "Lymphoma"],
    "loss of appetite": ["Dengue Fever", "Appendicitis", "Malaria",
                         "Tuberculosis", "Liver Cirrhosis", "Lung Cancer",
                         "Lymphoma", "Crohn's Disease"],
    "back pain": ["Kidney Disease", "Appendicitis", "Pyelonephritis",
                  "Pancreatitis", "Aortic Dissection"],
    "yellowing of skin": ["Dengue Fever", "Malaria", "Liver Cirrhosis",
                          "Cholecystitis", "Pancreatitis"],
    "rapid heartbeat": ["Heart Attack", "Hypertension", "Anemia",
                        "Hyperthyroidism", "Pulmonary Embolism", "Heart Failure"],

    # ---- NEW symptoms ----
    "weight loss": ["Tuberculosis", "Lung Cancer", "Lymphoma", "Leukemia",
                    "Hyperthyroidism", "Crohn's Disease", "Liver Cirrhosis",
                    "Diabetes", "HIV"],
    "weight gain": ["Hypothyroidism", "Heart Failure"],
    "night sweats": ["Tuberculosis", "Lymphoma", "Leukemia", "HIV", "Endocarditis"],
    "swollen lymph nodes": ["Lymphoma", "Leukemia", "Tuberculosis", "HIV"],
    "bruising easily": ["Leukemia", "Liver Cirrhosis"],
    "bleeding gums": ["Leukemia", "Dengue Fever"],
    "swollen joints": ["Rheumatoid Arthritis", "Gout", "Lupus"],
    "morning stiffness": ["Rheumatoid Arthritis", "Lupus"],
    "butterfly rash": ["Lupus"],
    "hair loss": ["Lupus", "Hypothyroidism"],
    "mouth ulcers": ["Lupus", "Crohn's Disease"],
    "diarrhea": ["Crohn's Disease", "HIV", "Hyperthyroidism"],
    "bloody stool": ["Crohn's Disease", "Colon Cancer"],
    "constipation": ["Hypothyroidism", "Colon Cancer"],
    "numbness": ["Multiple Sclerosis", "Stroke", "Guillain-Barre Syndrome", "Diabetes"],
    "tingling": ["Multiple Sclerosis", "Guillain-Barre Syndrome", "Diabetes"],
    "muscle weakness": ["Multiple Sclerosis", "Guillain-Barre Syndrome",
                        "Stroke", "Hypothyroidism"],
    "balance problems": ["Multiple Sclerosis", "Stroke", "Brain Tumor",
                         "Parkinson's Disease"],
    "tremor": ["Parkinson's Disease", "Hyperthyroidism"],
    "slurred speech": ["Stroke", "Multiple Sclerosis", "Brain Tumor"],
    "facial drooping": ["Stroke"],
    "seizures": ["Epilepsy", "Brain Tumor", "Meningitis", "Stroke"],
    "loss of consciousness": ["Epilepsy", "Stroke", "Heart Attack"],
    "stiff neck": ["Meningitis"],
    "confusion": ["Meningitis", "Stroke", "Liver Cirrhosis", "Brain Tumor"],
    "memory loss": ["Brain Tumor", "Stroke"],
    "leg swelling": ["Heart Failure", "Chronic Kidney Disease",
                     "Liver Cirrhosis", "Pulmonary Embolism"],
    "abdominal swelling": ["Liver Cirrhosis", "Ovarian Cancer", "Heart Failure"],
    "wheezing": ["Asthma", "Lung Cancer"],
    "coughing blood": ["Tuberculosis", "Lung Cancer", "Pulmonary Embolism"],
    "heartburn": ["GERD"],
    "burning urination": ["UTI", "Pyelonephritis"],
    "cloudy urine": ["UTI", "Pyelonephritis", "Chronic Kidney Disease"],
    "blood in urine": ["UTI", "Chronic Kidney Disease", "Kidney Disease"],
    "cold intolerance": ["Hypothyroidism"],
    "heat intolerance": ["Hyperthyroidism"],
    "skin darkening": ["Addison's Disease", "Liver Cirrhosis"],
    "low blood pressure": ["Addison's Disease", "Heart Failure"],
    "calf pain": ["Pulmonary Embolism"],
}


# =============================================================================
#  DISEASE PATHS  (each disease has 2-3 diagnostic paths)
# =============================================================================
DISEASE_PATHS = {
    "Pneumonia": {
        "severity": "High", "color": "#ff6b35", "icon": "🫁",
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
        "severity": "High", "color": "#7c3aed", "icon": "🦠",
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
        "severity": "High", "color": "#059669", "icon": "🦟",
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
        "severity": "High", "color": "#dc2626", "icon": "🌡️",
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
        "severity": "Critical", "color": "#ff0040", "icon": "❤️",
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
        "severity": "Medium", "color": "#0891b2", "icon": "🩺",
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
        "severity": "Critical", "color": "#f59e0b", "icon": "⚠️",
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
        "severity": "Medium", "color": "#8b5cf6", "icon": "🧠",
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
        "severity": "Medium", "color": "#e879f9", "icon": "💊",
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
        "severity": "Medium", "color": "#f97316", "icon": "💓",
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
    "Tuberculosis": {
        "severity": "High", "color": "#a16207", "icon": "🦠",
        "description": "Mycobacterium tuberculosis pulmonary infection — chronic, granulomatous, and contagious.",
        "paths": [
            [
                {"test": "Mantoux Tuberculin Skin Test", "cost": 200, "time_hrs": 48, "purpose": "Cell-mediated immune reactivity to TB", "icon": "💉"},
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Cavitary lesions / upper lobe infiltrates", "icon": "📷"},
            ],
            [
                {"test": "Sputum AFB Smear", "cost": 300, "time_hrs": 6, "purpose": "Acid-fast bacilli microscopy", "icon": "🔬"},
                {"test": "GeneXpert MTB/RIF", "cost": 1800, "time_hrs": 4, "purpose": "Rapid PCR + rifampicin resistance", "icon": "🧬"},
            ],
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Initial pulmonary screening", "icon": "📷"},
                {"test": "Sputum AFB Smear", "cost": 300, "time_hrs": 6, "purpose": "Bacillary load assessment", "icon": "🔬"},
                {"test": "Sputum Culture (LJ medium)", "cost": 1500, "time_hrs": 720, "purpose": "Gold-standard mycobacterial culture", "icon": "🧫"},
                {"test": "HIV Test", "cost": 400, "time_hrs": 4, "purpose": "Co-infection screening", "icon": "🩸"},
            ],
        ]
    },
    "Lupus": {
        "severity": "High", "color": "#be185d", "icon": "🦋",
        "description": "Systemic Lupus Erythematosus — multi-organ autoimmune disease producing anti-nuclear antibodies.",
        "paths": [
            [
                {"test": "ANA (Antinuclear Antibody)", "cost": 900, "time_hrs": 24, "purpose": "SLE screening test", "icon": "🧪"},
                {"test": "Anti-dsDNA Antibody", "cost": 1200, "time_hrs": 48, "purpose": "Highly specific for SLE", "icon": "🔬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Cytopenias common in SLE", "icon": "🩸"},
                {"test": "ANA (Antinuclear Antibody)", "cost": 900, "time_hrs": 24, "purpose": "Initial autoimmune screen", "icon": "🧪"},
                {"test": "Complement C3/C4", "cost": 800, "time_hrs": 12, "purpose": "Decreased in active lupus", "icon": "⚗️"},
            ],
            [
                {"test": "ANA (Antinuclear Antibody)", "cost": 900, "time_hrs": 24, "purpose": "Pan-autoimmune screening", "icon": "🧪"},
                {"test": "Anti-dsDNA Antibody", "cost": 1200, "time_hrs": 48, "purpose": "Lupus specificity confirmation", "icon": "🔬"},
                {"test": "Anti-Smith Antibody", "cost": 1100, "time_hrs": 48, "purpose": "Highly specific SLE marker", "icon": "🧫"},
                {"test": "Urine Routine + ACR", "cost": 400, "time_hrs": 4, "purpose": "Lupus nephritis screening", "icon": "🧪"},
            ],
        ]
    },
    "Multiple Sclerosis": {
        "severity": "High", "color": "#6366f1", "icon": "🧠",
        "description": "Autoimmune demyelination of CNS white matter causing relapsing neurological deficits.",
        "paths": [
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Document focal deficits", "icon": "🩺"},
                {"test": "MRI Brain + Spine (with contrast)", "cost": 8000, "time_hrs": 3, "purpose": "T2 hyperintense demyelinating plaques", "icon": "🧲"},
            ],
            [
                {"test": "MRI Brain + Spine (with contrast)", "cost": 8000, "time_hrs": 3, "purpose": "Dissemination in space/time", "icon": "🧲"},
                {"test": "Lumbar Puncture (CSF)", "cost": 2500, "time_hrs": 6, "purpose": "Oligoclonal bands detection", "icon": "💉"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Baseline deficit mapping", "icon": "🩺"},
                {"test": "MRI Brain + Spine (with contrast)", "cost": 8000, "time_hrs": 3, "purpose": "Demyelinating lesion confirmation", "icon": "🧲"},
                {"test": "Lumbar Puncture (CSF)", "cost": 2500, "time_hrs": 6, "purpose": "Oligoclonal bands + IgG index", "icon": "💉"},
                {"test": "Visual Evoked Potentials", "cost": 1500, "time_hrs": 2, "purpose": "Optic nerve demyelination", "icon": "📈"},
            ],
        ]
    },
    "Crohn's Disease": {
        "severity": "High", "color": "#9a3412", "icon": "🌀",
        "description": "Chronic transmural inflammatory bowel disease affecting any GI tract segment.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Anemia + leukocytosis", "icon": "🩸"},
                {"test": "Fecal Calprotectin", "cost": 1500, "time_hrs": 24, "purpose": "Intestinal inflammation marker", "icon": "🧪"},
                {"test": "Colonoscopy + Biopsy", "cost": 8000, "time_hrs": 3, "purpose": "Skip lesions, granulomas", "icon": "🔍"},
            ],
            [
                {"test": "C-Reactive Protein", "cost": 350, "time_hrs": 6, "purpose": "Systemic inflammation", "icon": "⚗️"},
                {"test": "Colonoscopy + Biopsy", "cost": 8000, "time_hrs": 3, "purpose": "Direct visualization + histology", "icon": "🔍"},
            ],
            [
                {"test": "Fecal Calprotectin", "cost": 1500, "time_hrs": 24, "purpose": "IBD vs IBS differentiation", "icon": "🧪"},
                {"test": "MR Enterography", "cost": 7000, "time_hrs": 4, "purpose": "Small bowel involvement", "icon": "🧲"},
                {"test": "Colonoscopy + Biopsy", "cost": 8000, "time_hrs": 3, "purpose": "Definitive diagnosis", "icon": "🔍"},
            ],
        ]
    },
    "Pulmonary Embolism": {
        "severity": "Critical", "color": "#ef4444", "icon": "🫀",
        "description": "Sudden occlusion of pulmonary artery by thromboembolus — life-threatening cardiopulmonary emergency.",
        "paths": [
            [
                {"test": "D-Dimer", "cost": 600, "time_hrs": 2, "purpose": "Sensitive screening for thrombosis", "icon": "🩸"},
                {"test": "CT Pulmonary Angiography", "cost": 6000, "time_hrs": 2, "purpose": "Definitive PE imaging", "icon": "🖥️"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "S1Q3T3 pattern / RV strain", "icon": "📈"},
                {"test": "D-Dimer", "cost": 600, "time_hrs": 2, "purpose": "Exclude low-risk PE", "icon": "🩸"},
                {"test": "CT Pulmonary Angiography", "cost": 6000, "time_hrs": 2, "purpose": "Visualize clot in pulmonary tree", "icon": "🖥️"},
            ],
            [
                {"test": "D-Dimer", "cost": 600, "time_hrs": 2, "purpose": "Thrombotic activity screen", "icon": "🩸"},
                {"test": "Doppler Lower Limb USG", "cost": 1200, "time_hrs": 1, "purpose": "DVT source identification", "icon": "📡"},
                {"test": "V/Q Scan", "cost": 4500, "time_hrs": 3, "purpose": "Alternative to CTPA in renal failure", "icon": "☢️"},
            ],
        ]
    },
    "Sarcoidosis": {
        "severity": "Medium", "color": "#16a34a", "icon": "🌿",
        "description": "Multisystem granulomatous disease with non-caseating granulomas, commonly affecting lungs.",
        "paths": [
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Bilateral hilar lymphadenopathy", "icon": "📷"},
                {"test": "Serum ACE Level", "cost": 900, "time_hrs": 24, "purpose": "Elevated in active sarcoidosis", "icon": "⚗️"},
            ],
            [
                {"test": "HRCT Chest", "cost": 4500, "time_hrs": 2, "purpose": "Perilymphatic micronodules", "icon": "🖥️"},
                {"test": "Bronchoscopy + Biopsy", "cost": 7000, "time_hrs": 4, "purpose": "Non-caseating granulomas", "icon": "🔍"},
            ],
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Initial screening", "icon": "📷"},
                {"test": "Serum ACE Level", "cost": 900, "time_hrs": 24, "purpose": "Granulomatous activity", "icon": "⚗️"},
                {"test": "HRCT Chest", "cost": 4500, "time_hrs": 2, "purpose": "Detailed parenchymal pattern", "icon": "🖥️"},
                {"test": "Transbronchial Biopsy", "cost": 7500, "time_hrs": 5, "purpose": "Histopathological confirmation", "icon": "🔬"},
            ],
        ]
    },
    "Stroke": {
        "severity": "Critical", "color": "#dc2626", "icon": "🧠",
        "description": "Acute focal neurological deficit from ischemic occlusion or hemorrhagic rupture of cerebral vessels.",
        "paths": [
            [
                {"test": "CT Scan Brain (non-contrast)", "cost": 2500, "time_hrs": 0.5, "purpose": "Rule out hemorrhage immediately", "icon": "🖥️"},
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 0.5, "purpose": "NIH Stroke Scale scoring", "icon": "🩺"},
            ],
            [
                {"test": "CT Scan Brain (non-contrast)", "cost": 2500, "time_hrs": 0.5, "purpose": "Acute hemorrhage exclusion", "icon": "🖥️"},
                {"test": "CT Angiography", "cost": 5000, "time_hrs": 1, "purpose": "Large vessel occlusion detection", "icon": "🖥️"},
                {"test": "MRI Brain (DWI)", "cost": 6000, "time_hrs": 2, "purpose": "Acute infarct localization", "icon": "🧲"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 0.5, "purpose": "Rapid deficit assessment", "icon": "🩺"},
                {"test": "CT Scan Brain (non-contrast)", "cost": 2500, "time_hrs": 0.5, "purpose": "First-line imaging", "icon": "🖥️"},
                {"test": "Carotid Doppler USG", "cost": 2000, "time_hrs": 1, "purpose": "Identify embolic source", "icon": "📡"},
                {"test": "ECG + Echocardiogram", "cost": 2300, "time_hrs": 2, "purpose": "Cardioembolic source workup", "icon": "🫀"},
            ],
        ]
    },
    "Hypothyroidism": {
        "severity": "Medium", "color": "#0ea5e9", "icon": "❄️",
        "description": "Underactive thyroid producing insufficient T3/T4 — slows metabolism systemically.",
        "paths": [
            [
                {"test": "TSH (Thyroid Stimulating Hormone)", "cost": 400, "time_hrs": 6, "purpose": "Most sensitive screening test", "icon": "🧪"},
                {"test": "Free T4", "cost": 500, "time_hrs": 6, "purpose": "Confirm hypothyroid state", "icon": "⚗️"},
            ],
            [
                {"test": "TSH (Thyroid Stimulating Hormone)", "cost": 400, "time_hrs": 6, "purpose": "Primary hypothyroid marker", "icon": "🧪"},
                {"test": "Free T4", "cost": 500, "time_hrs": 6, "purpose": "Hormone level confirmation", "icon": "⚗️"},
                {"test": "Anti-TPO Antibody", "cost": 800, "time_hrs": 24, "purpose": "Hashimoto's autoimmune cause", "icon": "🔬"},
            ],
        ]
    },
    "Hyperthyroidism": {
        "severity": "Medium", "color": "#f59e0b", "icon": "🔥",
        "description": "Excess thyroid hormone production causing hypermetabolic state — Graves' is most common cause.",
        "paths": [
            [
                {"test": "TSH (Thyroid Stimulating Hormone)", "cost": 400, "time_hrs": 6, "purpose": "Suppressed in hyperthyroidism", "icon": "🧪"},
                {"test": "Free T3 + Free T4", "cost": 900, "time_hrs": 6, "purpose": "Elevated thyroid hormones", "icon": "⚗️"},
            ],
            [
                {"test": "TSH + Free T4", "cost": 700, "time_hrs": 6, "purpose": "Initial thyroid panel", "icon": "🧪"},
                {"test": "TSH Receptor Antibody", "cost": 1500, "time_hrs": 48, "purpose": "Confirm Graves' disease", "icon": "🔬"},
                {"test": "Thyroid Uptake Scan", "cost": 3500, "time_hrs": 4, "purpose": "Differentiate cause", "icon": "☢️"},
            ],
        ]
    },
    "Chronic Kidney Disease": {
        "severity": "High", "color": "#65a30d", "icon": "🫘",
        "description": "Progressive irreversible loss of nephron function over months to years.",
        "paths": [
            [
                {"test": "Serum Creatinine + eGFR", "cost": 300, "time_hrs": 4, "purpose": "Glomerular filtration estimate", "icon": "🩸"},
                {"test": "Urine ACR", "cost": 400, "time_hrs": 4, "purpose": "Proteinuria quantification", "icon": "🧪"},
            ],
            [
                {"test": "Kidney Function Tests", "cost": 500, "time_hrs": 6, "purpose": "BUN, creatinine, electrolytes", "icon": "🧪"},
                {"test": "Renal Ultrasound", "cost": 1500, "time_hrs": 1, "purpose": "Kidney size + obstruction", "icon": "📡"},
                {"test": "Urine Routine + ACR", "cost": 400, "time_hrs": 4, "purpose": "Glomerular vs tubular pattern", "icon": "🧪"},
            ],
            [
                {"test": "Serum Creatinine + eGFR", "cost": 300, "time_hrs": 4, "purpose": "Stage CKD severity", "icon": "🩸"},
                {"test": "Urine ACR", "cost": 400, "time_hrs": 4, "purpose": "Albuminuria assessment", "icon": "🧪"},
                {"test": "Renal Biopsy", "cost": 12000, "time_hrs": 24, "purpose": "Histopathological diagnosis", "icon": "🔬"},
            ],
        ]
    },
    "Liver Cirrhosis": {
        "severity": "High", "color": "#a16207", "icon": "🟫",
        "description": "End-stage hepatic fibrosis with regenerative nodules — disrupts liver architecture and function.",
        "paths": [
            [
                {"test": "Liver Function Tests", "cost": 700, "time_hrs": 8, "purpose": "AST, ALT, bilirubin, albumin", "icon": "⚗️"},
                {"test": "Abdominal Ultrasound", "cost": 1200, "time_hrs": 1, "purpose": "Nodular liver + splenomegaly", "icon": "📡"},
            ],
            [
                {"test": "Liver Function Tests", "cost": 700, "time_hrs": 8, "purpose": "Hepatic synthetic function", "icon": "⚗️"},
                {"test": "FibroScan (Elastography)", "cost": 2500, "time_hrs": 1, "purpose": "Non-invasive fibrosis staging", "icon": "📡"},
                {"test": "Hepatitis B+C Serology", "cost": 1500, "time_hrs": 12, "purpose": "Identify viral etiology", "icon": "🧪"},
            ],
            [
                {"test": "Liver Function Tests", "cost": 700, "time_hrs": 8, "purpose": "Baseline hepatic profile", "icon": "⚗️"},
                {"test": "Abdominal Ultrasound", "cost": 1200, "time_hrs": 1, "purpose": "Initial morphologic imaging", "icon": "📡"},
                {"test": "Liver Biopsy", "cost": 8000, "time_hrs": 24, "purpose": "Definitive histological staging", "icon": "🔬"},
            ],
        ]
    },
    "Asthma": {
        "severity": "Medium", "color": "#06b6d4", "icon": "💨",
        "description": "Chronic reversible airway inflammation with bronchospasm and hyperresponsiveness.",
        "paths": [
            [
                {"test": "Peak Flow Measurement", "cost": 100, "time_hrs": 0.25, "purpose": "Airflow limitation screening", "icon": "🌬️"},
                {"test": "Spirometry (PFT)", "cost": 1500, "time_hrs": 1, "purpose": "FEV1/FVC + reversibility", "icon": "📊"},
            ],
            [
                {"test": "Spirometry (PFT)", "cost": 1500, "time_hrs": 1, "purpose": "Confirm obstructive pattern", "icon": "📊"},
                {"test": "Bronchodilator Reversibility", "cost": 800, "time_hrs": 1, "purpose": ">12% FEV1 improvement", "icon": "💊"},
            ],
            [
                {"test": "Spirometry (PFT)", "cost": 1500, "time_hrs": 1, "purpose": "Pulmonary function testing", "icon": "📊"},
                {"test": "Allergy Panel (IgE)", "cost": 2000, "time_hrs": 24, "purpose": "Atopic trigger identification", "icon": "🧪"},
                {"test": "FeNO Test", "cost": 1200, "time_hrs": 0.5, "purpose": "Airway eosinophilic inflammation", "icon": "🌬️"},
            ],
        ]
    },
    "GERD": {
        "severity": "Low", "color": "#14b8a6", "icon": "🔥",
        "description": "Gastroesophageal reflux of acidic content causing mucosal injury and heartburn.",
        "paths": [
            [
                {"test": "Clinical PPI Trial", "cost": 200, "time_hrs": 168, "purpose": "Empirical therapeutic test", "icon": "💊"},
            ],
            [
                {"test": "Upper GI Endoscopy", "cost": 4500, "time_hrs": 2, "purpose": "Visualize esophagitis", "icon": "🔍"},
                {"test": "Esophageal Biopsy", "cost": 1500, "time_hrs": 48, "purpose": "Exclude Barrett's esophagus", "icon": "🔬"},
            ],
            [
                {"test": "24-hour pH Monitoring", "cost": 5000, "time_hrs": 24, "purpose": "Quantify acid exposure time", "icon": "📊"},
                {"test": "Esophageal Manometry", "cost": 4000, "time_hrs": 2, "purpose": "Lower esophageal sphincter tone", "icon": "📈"},
            ],
        ]
    },
    "UTI": {
        "severity": "Low", "color": "#0891b2", "icon": "💧",
        "description": "Bacterial infection of urinary tract — usually E. coli ascending from urethra to bladder.",
        "paths": [
            [
                {"test": "Urine Routine + Microscopy", "cost": 200, "time_hrs": 2, "purpose": "Pyuria + bacteriuria", "icon": "🧪"},
            ],
            [
                {"test": "Urine Routine", "cost": 200, "time_hrs": 2, "purpose": "Initial screening", "icon": "🧪"},
                {"test": "Urine Culture + Sensitivity", "cost": 800, "time_hrs": 48, "purpose": "Organism + antibiotic guidance", "icon": "🧫"},
            ],
        ]
    },
    "Pyelonephritis": {
        "severity": "High", "color": "#0369a1", "icon": "🫘",
        "description": "Ascending bacterial infection involving renal parenchyma — can cause sepsis.",
        "paths": [
            [
                {"test": "Urine Culture + Sensitivity", "cost": 800, "time_hrs": 48, "purpose": "Confirm uropathogen", "icon": "🧫"},
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Leukocytosis with left shift", "icon": "🩸"},
            ],
            [
                {"test": "Urine Routine + Culture", "cost": 1000, "time_hrs": 48, "purpose": "Pyuria + bacterial growth", "icon": "🧪"},
                {"test": "Renal Ultrasound", "cost": 1500, "time_hrs": 1, "purpose": "Exclude obstruction/abscess", "icon": "📡"},
                {"test": "Blood Culture", "cost": 800, "time_hrs": 72, "purpose": "Detect bacteremia", "icon": "🧪"},
            ],
        ]
    },
    "Endocarditis": {
        "severity": "Critical", "color": "#b91c1c", "icon": "🫀",
        "description": "Microbial infection of cardiac endothelium / valves — produces vegetations and emboli.",
        "paths": [
            [
                {"test": "Blood Culture (3 sets)", "cost": 2400, "time_hrs": 72, "purpose": "Identify bloodstream organism", "icon": "🧪"},
                {"test": "Transthoracic Echocardiogram", "cost": 2000, "time_hrs": 1, "purpose": "Detect vegetations", "icon": "🫀"},
            ],
            [
                {"test": "Blood Culture (3 sets)", "cost": 2400, "time_hrs": 72, "purpose": "Persistent bacteremia confirmation", "icon": "🧪"},
                {"test": "Transesophageal Echo (TEE)", "cost": 8000, "time_hrs": 2, "purpose": "High-sensitivity vegetation imaging", "icon": "🫀"},
                {"test": "ESR + CRP", "cost": 500, "time_hrs": 6, "purpose": "Inflammatory activity", "icon": "⚗️"},
            ],
        ]
    },
    "Meningitis": {
        "severity": "Critical", "color": "#7c2d12", "icon": "🧠",
        "description": "Inflammation of meninges — bacterial form is rapidly fatal without urgent antibiotics.",
        "paths": [
            [
                {"test": "Lumbar Puncture (CSF Analysis)", "cost": 2500, "time_hrs": 4, "purpose": "Cell count, protein, glucose", "icon": "💉"},
                {"test": "CSF Gram Stain + Culture", "cost": 1500, "time_hrs": 48, "purpose": "Identify causative organism", "icon": "🧫"},
            ],
            [
                {"test": "CT Scan Brain", "cost": 2500, "time_hrs": 1, "purpose": "Rule out raised ICP before LP", "icon": "🖥️"},
                {"test": "Lumbar Puncture (CSF Analysis)", "cost": 2500, "time_hrs": 4, "purpose": "CSF biochemistry + cytology", "icon": "💉"},
                {"test": "Blood Culture", "cost": 800, "time_hrs": 72, "purpose": "Concurrent bacteremia", "icon": "🧪"},
            ],
        ]
    },
    "Epilepsy": {
        "severity": "High", "color": "#9333ea", "icon": "⚡",
        "description": "Recurrent unprovoked seizures from abnormal synchronized cortical neuronal activity.",
        "paths": [
            [
                {"test": "EEG (Electroencephalogram)", "cost": 2000, "time_hrs": 2, "purpose": "Epileptiform discharges", "icon": "📈"},
                {"test": "MRI Brain (epilepsy protocol)", "cost": 6000, "time_hrs": 2, "purpose": "Structural lesion search", "icon": "🧲"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Seizure semiology classification", "icon": "🩺"},
                {"test": "EEG (Electroencephalogram)", "cost": 2000, "time_hrs": 2, "purpose": "Interictal spikes", "icon": "📈"},
                {"test": "Video EEG Monitoring", "cost": 12000, "time_hrs": 48, "purpose": "Capture ictal activity", "icon": "📹"},
            ],
        ]
    },
    "Parkinson's Disease": {
        "severity": "High", "color": "#475569", "icon": "🧓",
        "description": "Progressive degeneration of dopaminergic substantia nigra neurons — bradykinesia, tremor, rigidity.",
        "paths": [
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "UPDRS motor score", "icon": "🩺"},
                {"test": "MRI Brain", "cost": 5000, "time_hrs": 2, "purpose": "Exclude vascular parkinsonism", "icon": "🧲"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Cardinal sign assessment", "icon": "🩺"},
                {"test": "Levodopa Challenge Test", "cost": 800, "time_hrs": 4, "purpose": "Dopaminergic responsiveness", "icon": "💊"},
                {"test": "DAT-Scan (SPECT)", "cost": 18000, "time_hrs": 4, "purpose": "Striatal dopamine deficit", "icon": "☢️"},
            ],
        ]
    },
    "Rheumatoid Arthritis": {
        "severity": "High", "color": "#db2777", "icon": "🦴",
        "description": "Chronic symmetric inflammatory polyarthritis with synovial pannus and joint destruction.",
        "paths": [
            [
                {"test": "Rheumatoid Factor (RF)", "cost": 600, "time_hrs": 24, "purpose": "RA serology screening", "icon": "🧪"},
                {"test": "Anti-CCP Antibody", "cost": 1200, "time_hrs": 48, "purpose": "Highly specific for RA", "icon": "🔬"},
            ],
            [
                {"test": "ESR + CRP", "cost": 500, "time_hrs": 6, "purpose": "Inflammatory activity", "icon": "⚗️"},
                {"test": "Anti-CCP Antibody", "cost": 1200, "time_hrs": 48, "purpose": "RA confirmation", "icon": "🔬"},
                {"test": "Joint X-Ray (Hands)", "cost": 800, "time_hrs": 2, "purpose": "Erosions + joint space loss", "icon": "📷"},
            ],
            [
                {"test": "Rheumatoid Factor (RF)", "cost": 600, "time_hrs": 24, "purpose": "Initial autoimmune screen", "icon": "🧪"},
                {"test": "Anti-CCP Antibody", "cost": 1200, "time_hrs": 48, "purpose": "Specific RA antibody", "icon": "🔬"},
                {"test": "MRI Hands (with contrast)", "cost": 7000, "time_hrs": 2, "purpose": "Early synovitis + erosions", "icon": "🧲"},
            ],
        ]
    },
    "Gout": {
        "severity": "Medium", "color": "#eab308", "icon": "🦶",
        "description": "Monosodium urate crystal deposition arthritis — typically affects first MTP joint acutely.",
        "paths": [
            [
                {"test": "Serum Uric Acid", "cost": 250, "time_hrs": 4, "purpose": "Hyperuricemia screening", "icon": "🩸"},
                {"test": "Joint Aspiration + Polarized Microscopy", "cost": 1500, "time_hrs": 4, "purpose": "Negatively birefringent crystals", "icon": "🔬"},
            ],
            [
                {"test": "Serum Uric Acid", "cost": 250, "time_hrs": 4, "purpose": "Baseline uric acid level", "icon": "🩸"},
                {"test": "Joint Ultrasound", "cost": 1500, "time_hrs": 1, "purpose": "Double-contour sign", "icon": "📡"},
            ],
        ]
    },
    "Pancreatitis": {
        "severity": "High", "color": "#ea580c", "icon": "🔥",
        "description": "Acute inflammation of pancreas with autodigestion by activated proteolytic enzymes.",
        "paths": [
            [
                {"test": "Serum Lipase", "cost": 600, "time_hrs": 4, "purpose": "More specific than amylase", "icon": "⚗️"},
                {"test": "Serum Amylase", "cost": 400, "time_hrs": 4, "purpose": "Pancreatic enzyme elevation", "icon": "⚗️"},
            ],
            [
                {"test": "Serum Lipase", "cost": 600, "time_hrs": 4, "purpose": "Confirm pancreatic injury", "icon": "⚗️"},
                {"test": "Abdominal Ultrasound", "cost": 1200, "time_hrs": 1, "purpose": "Gallstone etiology screen", "icon": "📡"},
                {"test": "CT Scan Abdomen (with contrast)", "cost": 4500, "time_hrs": 2, "purpose": "Necrosis + complications", "icon": "🖥️"},
            ],
        ]
    },
    "Leukemia": {
        "severity": "Critical", "color": "#be123c", "icon": "🩸",
        "description": "Malignant clonal proliferation of hematopoietic precursors crowding out normal marrow.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Cytopenias + blasts on differential", "icon": "🩸"},
                {"test": "Peripheral Blood Smear", "cost": 300, "time_hrs": 4, "purpose": "Identify blast cells", "icon": "🔬"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Initial blood screening", "icon": "🩸"},
                {"test": "Bone Marrow Aspiration + Biopsy", "cost": 6000, "time_hrs": 24, "purpose": "Confirm leukemic infiltration", "icon": "🦴"},
                {"test": "Flow Cytometry (Immunophenotyping)", "cost": 8000, "time_hrs": 48, "purpose": "Subtype classification", "icon": "🧫"},
                {"test": "Cytogenetics (Karyotype)", "cost": 5000, "time_hrs": 168, "purpose": "Prognostic chromosomal markers", "icon": "🧬"},
            ],
        ]
    },
    "Lymphoma": {
        "severity": "Critical", "color": "#7e22ce", "icon": "🩺",
        "description": "Malignant proliferation of lymphocytes in lymphoid tissue — Hodgkin or non-Hodgkin types.",
        "paths": [
            [
                {"test": "Complete Blood Count (CBC) + LDH", "cost": 500, "time_hrs": 4, "purpose": "Tumor burden assessment", "icon": "🩸"},
                {"test": "Excisional Lymph Node Biopsy", "cost": 9000, "time_hrs": 24, "purpose": "Histological subtyping", "icon": "🔬"},
            ],
            [
                {"test": "CT Scan (Neck/Chest/Abdomen)", "cost": 7000, "time_hrs": 3, "purpose": "Stage nodal involvement", "icon": "🖥️"},
                {"test": "Excisional Lymph Node Biopsy", "cost": 9000, "time_hrs": 24, "purpose": "Reed-Sternberg / lymphoid pattern", "icon": "🔬"},
                {"test": "PET-CT Scan", "cost": 22000, "time_hrs": 4, "purpose": "Metabolic staging (Ann Arbor)", "icon": "☢️"},
            ],
        ]
    },
    "Cholecystitis": {
        "severity": "High", "color": "#facc15", "icon": "🟡",
        "description": "Acute inflammation of gallbladder, usually due to cystic duct obstruction by gallstones.",
        "paths": [
            [
                {"test": "Abdominal Ultrasound", "cost": 1200, "time_hrs": 1, "purpose": "Gallstones + wall thickening", "icon": "📡"},
                {"test": "Liver Function Tests", "cost": 700, "time_hrs": 8, "purpose": "Bilirubin + ALP elevation", "icon": "⚗️"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Leukocytosis", "icon": "🩸"},
                {"test": "Abdominal Ultrasound", "cost": 1200, "time_hrs": 1, "purpose": "Sonographic Murphy's sign", "icon": "📡"},
                {"test": "HIDA Scan", "cost": 4500, "time_hrs": 3, "purpose": "Cystic duct obstruction confirmation", "icon": "☢️"},
            ],
        ]
    },
    "Typhoid": {
        "severity": "High", "color": "#a16207", "icon": "🌡️",
        "description": "Salmonella typhi enteric fever with sustained fever and bacteremia.",
        "paths": [
            [
                {"test": "Widal Test", "cost": 250, "time_hrs": 8, "purpose": "Salmonella agglutinin titres", "icon": "🧪"},
                {"test": "Blood Culture", "cost": 800, "time_hrs": 72, "purpose": "Definitive typhoid diagnosis", "icon": "🧫"},
            ],
            [
                {"test": "Complete Blood Count (CBC)", "cost": 200, "time_hrs": 4, "purpose": "Leukopenia + relative bradycardia", "icon": "🩸"},
                {"test": "Blood Culture", "cost": 800, "time_hrs": 72, "purpose": "Gold standard", "icon": "🧫"},
                {"test": "Stool Culture", "cost": 600, "time_hrs": 72, "purpose": "Convalescent shedding", "icon": "🧫"},
            ],
        ]
    },
    "Bronchitis": {
        "severity": "Low", "color": "#0891b2", "icon": "🌬️",
        "description": "Inflammation of bronchial mucosa — acute viral or chronic smoker-related.",
        "paths": [
            [
                {"test": "Clinical Examination", "cost": 300, "time_hrs": 0.5, "purpose": "Auscultatory wheeze + cough", "icon": "🩺"},
            ],
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Exclude pneumonia", "icon": "📷"},
                {"test": "Sputum Examination", "cost": 400, "time_hrs": 6, "purpose": "Bacterial superinfection", "icon": "🔬"},
            ],
        ]
    },
    "Angina": {
        "severity": "High", "color": "#dc2626", "icon": "💔",
        "description": "Transient myocardial ischemia from coronary insufficiency on exertion.",
        "paths": [
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Resting ischemic changes", "icon": "📈"},
                {"test": "Treadmill Stress Test", "cost": 2500, "time_hrs": 1, "purpose": "Inducible ischemia", "icon": "📊"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Baseline tracing", "icon": "📈"},
                {"test": "Stress Echocardiogram", "cost": 4500, "time_hrs": 2, "purpose": "Wall motion under stress", "icon": "🫀"},
                {"test": "Coronary Angiography", "cost": 15000, "time_hrs": 3, "purpose": "Define coronary anatomy", "icon": "🔍"},
            ],
        ]
    },
    "Pericarditis": {
        "severity": "High", "color": "#b91c1c", "icon": "🫀",
        "description": "Inflammation of pericardial sac causing sharp positional chest pain and friction rub.",
        "paths": [
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Diffuse ST elevation + PR depression", "icon": "📈"},
                {"test": "Echocardiogram", "cost": 2000, "time_hrs": 1, "purpose": "Pericardial effusion", "icon": "🫀"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Classic pericarditis pattern", "icon": "📈"},
                {"test": "ESR + CRP", "cost": 500, "time_hrs": 6, "purpose": "Inflammatory activity", "icon": "⚗️"},
                {"test": "Cardiac MRI", "cost": 9000, "time_hrs": 3, "purpose": "Pericardial enhancement", "icon": "🧲"},
            ],
        ]
    },
    "Aortic Dissection": {
        "severity": "Critical", "color": "#991b1b", "icon": "💢",
        "description": "Tear in aortic intima with blood dissecting into media — surgical emergency.",
        "paths": [
            [
                {"test": "CT Angiography (Aorta)", "cost": 6000, "time_hrs": 1, "purpose": "Definitive imaging of intimal flap", "icon": "🖥️"},
            ],
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Widened mediastinum", "icon": "📷"},
                {"test": "CT Angiography (Aorta)", "cost": 6000, "time_hrs": 1, "purpose": "Confirm + classify Stanford type", "icon": "🖥️"},
                {"test": "Transesophageal Echo (TEE)", "cost": 8000, "time_hrs": 2, "purpose": "Bedside dissection assessment", "icon": "🫀"},
            ],
        ]
    },
    "Heart Failure": {
        "severity": "High", "color": "#ef4444", "icon": "💗",
        "description": "Impaired ventricular pump function causing congestion and reduced cardiac output.",
        "paths": [
            [
                {"test": "BNP / NT-proBNP", "cost": 1200, "time_hrs": 4, "purpose": "Cardiac stretch biomarker", "icon": "🩸"},
                {"test": "Echocardiogram", "cost": 2000, "time_hrs": 1, "purpose": "Ejection fraction measurement", "icon": "🫀"},
            ],
            [
                {"test": "ECG (Electrocardiogram)", "cost": 300, "time_hrs": 0.25, "purpose": "Underlying rhythm/ischemia", "icon": "📈"},
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Cardiomegaly + pulmonary edema", "icon": "📷"},
                {"test": "Echocardiogram", "cost": 2000, "time_hrs": 1, "purpose": "Systolic + diastolic function", "icon": "🫀"},
                {"test": "BNP / NT-proBNP", "cost": 1200, "time_hrs": 4, "purpose": "Severity stratification", "icon": "🩸"},
            ],
        ]
    },
    "Lung Cancer": {
        "severity": "Critical", "color": "#52525b", "icon": "🫁",
        "description": "Malignant pulmonary neoplasm — small-cell or non-small-cell histology.",
        "paths": [
            [
                {"test": "Chest X-Ray", "cost": 500, "time_hrs": 2, "purpose": "Suspicious lung mass", "icon": "📷"},
                {"test": "CT Scan (Chest)", "cost": 3000, "time_hrs": 2, "purpose": "Characterize lesion + nodes", "icon": "🖥️"},
                {"test": "CT-Guided Biopsy", "cost": 6000, "time_hrs": 2, "purpose": "Histopathological diagnosis", "icon": "🔬"},
            ],
            [
                {"test": "Sputum Cytology", "cost": 800, "time_hrs": 24, "purpose": "Malignant cells in sputum", "icon": "🔬"},
                {"test": "PET-CT Scan", "cost": 22000, "time_hrs": 4, "purpose": "Staging + distant metastasis", "icon": "☢️"},
                {"test": "Bronchoscopy + Biopsy", "cost": 7000, "time_hrs": 4, "purpose": "Tissue diagnosis", "icon": "🔍"},
            ],
        ]
    },
    "Brain Tumor": {
        "severity": "Critical", "color": "#581c87", "icon": "🧠",
        "description": "Intracranial neoplasm — primary or metastatic — causing focal deficits + raised ICP.",
        "paths": [
            [
                {"test": "MRI Brain (with contrast)", "cost": 6000, "time_hrs": 2, "purpose": "Lesion characterization", "icon": "🧲"},
            ],
            [
                {"test": "CT Scan Brain", "cost": 2500, "time_hrs": 1, "purpose": "Initial screening", "icon": "🖥️"},
                {"test": "MRI Brain (with contrast)", "cost": 6000, "time_hrs": 2, "purpose": "Definitive imaging", "icon": "🧲"},
                {"test": "Stereotactic Biopsy", "cost": 18000, "time_hrs": 24, "purpose": "Histological tumor type", "icon": "🔬"},
            ],
        ]
    },
    "Guillain-Barre Syndrome": {
        "severity": "Critical", "color": "#0e7490", "icon": "🦵",
        "description": "Acute autoimmune demyelinating polyneuropathy with ascending paralysis.",
        "paths": [
            [
                {"test": "Nerve Conduction Study", "cost": 2500, "time_hrs": 2, "purpose": "Demyelinating pattern", "icon": "📈"},
                {"test": "Lumbar Puncture (CSF)", "cost": 2500, "time_hrs": 4, "purpose": "Albuminocytologic dissociation", "icon": "💉"},
            ],
            [
                {"test": "Neurological Examination", "cost": 500, "time_hrs": 1, "purpose": "Ascending weakness + areflexia", "icon": "🩺"},
                {"test": "Nerve Conduction Study + EMG", "cost": 3500, "time_hrs": 2, "purpose": "Confirm demyelination", "icon": "📈"},
                {"test": "Lumbar Puncture (CSF)", "cost": 2500, "time_hrs": 4, "purpose": "Elevated protein, normal cells", "icon": "💉"},
            ],
        ]
    },
    "Addison's Disease": {
        "severity": "High", "color": "#854d0e", "icon": "🌑",
        "description": "Primary adrenal insufficiency — deficient cortisol + aldosterone production.",
        "paths": [
            [
                {"test": "Morning Cortisol", "cost": 600, "time_hrs": 6, "purpose": "Baseline adrenal function", "icon": "🧪"},
                {"test": "ACTH Stimulation Test", "cost": 2500, "time_hrs": 2, "purpose": "Definitive adrenal insufficiency", "icon": "💉"},
            ],
            [
                {"test": "Serum Electrolytes", "cost": 300, "time_hrs": 4, "purpose": "Hyponatremia + hyperkalemia", "icon": "⚗️"},
                {"test": "Morning Cortisol + ACTH", "cost": 1200, "time_hrs": 6, "purpose": "Primary vs secondary", "icon": "🧪"},
                {"test": "ACTH Stimulation Test", "cost": 2500, "time_hrs": 2, "purpose": "Confirmatory test", "icon": "💉"},
            ],
        ]
    },
    "HIV": {
        "severity": "High", "color": "#16a34a", "icon": "🎗️",
        "description": "Human immunodeficiency virus infection — progressive CD4 T-cell depletion.",
        "paths": [
            [
                {"test": "HIV Rapid Antibody Test", "cost": 300, "time_hrs": 0.5, "purpose": "Initial screening", "icon": "⚡"},
                {"test": "HIV ELISA + Western Blot", "cost": 1500, "time_hrs": 24, "purpose": "Confirmatory testing", "icon": "🧪"},
            ],
            [
                {"test": "HIV ELISA", "cost": 800, "time_hrs": 12, "purpose": "Antibody screening", "icon": "🧪"},
                {"test": "HIV Viral Load (PCR)", "cost": 3500, "time_hrs": 48, "purpose": "Quantify viraemia", "icon": "🧬"},
                {"test": "CD4 Count", "cost": 1500, "time_hrs": 12, "purpose": "Immune status staging", "icon": "🩸"},
            ],
        ]
    },
    "Colon Cancer": {
        "severity": "Critical", "color": "#7c2d12", "icon": "🩸",
        "description": "Adenocarcinoma of colon — typically arises from adenomatous polyps.",
        "paths": [
            [
                {"test": "Fecal Occult Blood Test", "cost": 300, "time_hrs": 4, "purpose": "Initial screening", "icon": "🧪"},
                {"test": "Colonoscopy + Biopsy", "cost": 8000, "time_hrs": 3, "purpose": "Direct visualization + histology", "icon": "🔍"},
            ],
            [
                {"test": "Colonoscopy + Biopsy", "cost": 8000, "time_hrs": 3, "purpose": "Definitive diagnosis", "icon": "🔍"},
                {"test": "CEA (Carcinoembryonic Antigen)", "cost": 800, "time_hrs": 24, "purpose": "Tumor marker baseline", "icon": "🧪"},
                {"test": "CT Scan (Abdomen/Pelvis)", "cost": 4000, "time_hrs": 2, "purpose": "Staging + metastasis", "icon": "🖥️"},
            ],
        ]
    },
    "Ovarian Cancer": {
        "severity": "Critical", "color": "#a21caf", "icon": "🎗️",
        "description": "Epithelial ovarian malignancy — often presents late with abdominal distension.",
        "paths": [
            [
                {"test": "Pelvic Ultrasound", "cost": 1500, "time_hrs": 1, "purpose": "Adnexal mass characterization", "icon": "📡"},
                {"test": "CA-125 Tumor Marker", "cost": 1200, "time_hrs": 24, "purpose": "Ovarian cancer marker", "icon": "🧪"},
            ],
            [
                {"test": "Transvaginal Ultrasound", "cost": 2000, "time_hrs": 1, "purpose": "Detailed ovarian imaging", "icon": "📡"},
                {"test": "CA-125 + HE4", "cost": 2200, "time_hrs": 24, "purpose": "ROMA score", "icon": "🧪"},
                {"test": "CT Scan (Abdomen/Pelvis)", "cost": 4000, "time_hrs": 2, "purpose": "Staging workup", "icon": "🖥️"},
            ],
        ]
    },
    "Kidney Disease": {
        "severity": "High", "color": "#65a30d", "icon": "🫘",
        "description": "Generic structural/functional kidney impairment — overlaps with CKD spectrum.",
        "paths": [
            [
                {"test": "Serum Creatinine + eGFR", "cost": 300, "time_hrs": 4, "purpose": "GFR estimation", "icon": "🩸"},
                {"test": "Urine Routine", "cost": 200, "time_hrs": 2, "purpose": "Proteinuria + hematuria", "icon": "🧪"},
            ],
            [
                {"test": "Kidney Function Tests", "cost": 500, "time_hrs": 6, "purpose": "Comprehensive renal panel", "icon": "🧪"},
                {"test": "Renal Ultrasound", "cost": 1500, "time_hrs": 1, "purpose": "Structural assessment", "icon": "📡"},
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
    """BFS — Breadth-First Search.
    Goal: reach diagnosis in the FEWEST diagnostic steps (shallowest path in the search tree).
    Models a clinician who wants the QUICKEST screening: minimum number of tests.
    Tie-breakers: lowest time, then lowest cost.
    """
    paths = build_all_paths(disease_name)
    return min(paths, key=lambda p: (p["num_tests"], p["total_time"], p["total_cost"]))


def ucs_optimal(disease_name):
    """UCS — Uniform Cost Search.
    Goal: minimise CUMULATIVE MONETARY COST (₹), regardless of path length.
    Models a budget-constrained pathway: cheapest workup wins, even if it needs more tests.
    Tie-breakers: prefer MORE tests (more thorough for the same money), then lower time.
    """
    paths = build_all_paths(disease_name)
    return min(paths, key=lambda p: (p["total_cost"], -p["num_tests"], p["total_time"]))


def astar_optimal(disease_name):
    """A* Search — informed search using f(n) = g(n) + h(n).
       g(n) = real time-to-diagnosis (hours), the actual cost incurred so far.
       h(n) = heuristic estimate of remaining diagnostic uncertainty:
              h(n) = (max_tests_in_any_path − tests_in_this_path) × confidence_weight
              + cost_efficiency_term
       So a path with FEWER tests has HIGHER heuristic (less corroboration ⇒ more uncertainty).
    Goal: best clinical balance — fastest path that still confirms the diagnosis with
    sufficient confidence. Often picks a moderately longer, well-rounded path that gets
    to a confident diagnosis quickly.
    """
    paths = build_all_paths(disease_name)
    if not paths:
        return None
    max_tests = max(p["num_tests"] for p in paths)
    min_cost = min(p["total_cost"] for p in paths) or 1

    def f_score(p):
        # g(n): elapsed clinical time (each hour of delay = ₹300 of patient risk)
        g = p["total_time"] * 300
        # h(n): uncertainty heuristic — penalty for skipping corroborating tests
        uncertainty_penalty = (max_tests - p["num_tests"]) * 2000
        # cost-efficiency: relative cost above the cheapest option
        cost_overhead = (p["total_cost"] - min_cost) * 0.4
        return g + uncertainty_penalty + cost_overhead

    # Tie-breaker: prefer the path with the lowest TIME (urgency wins ties)
    return min(paths, key=lambda p: (f_score(p), p["total_time"], -p["num_tests"]))


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


@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    return jsonify({
        "count": len(DISEASE_PATHS),
        "diseases": sorted(DISEASE_PATHS.keys())
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
