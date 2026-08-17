"""Generate the synthetic patient_records.csv used by the document-loader notebook.

The data is fictional and exists only to give the loader and splitter examples
something realistic to chunk. Deterministic: same seed, same file.
"""

import csv
import random
from pathlib import Path

SEED = 42
RECORD_COUNT = 600
OUTPUT = Path(__file__).parent / "patient_records.csv"

# condition -> (symptom phrasings, treatment options, doctor note options)
CONDITIONS = {
    "Influenza": (
        ["Fever, cough, sore throat", "High temperature, body aches, chills",
         "Sudden fever, dry cough, exhaustion", "Sore throat, congestion, muscle pain"],
        ["Rest, fluids, antiviral medication", "Oseltamivir, bed rest, hydration",
         "Symptomatic care, paracetamol, fluids"],
        ["Patient shows signs of seasonal flu.", "Advised isolation for five days.",
         "Flu swab positive; monitor for secondary infection.",
         "Symptoms consistent with influenza A."],
    ),
    "Atrial Fibrillation": (
        ["Dizziness, irregular heartbeat, fatigue", "Palpitations, lightheadedness, breathlessness",
         "Fluttering chest sensation, weakness", "Irregular pulse, reduced exercise tolerance"],
        ["Blood thinners, beta-blockers", "Anticoagulation, rate control medication",
         "Warfarin, metoprolol, cardiology follow-up"],
        ["Irregular heartbeat detected; cardiology referral made.",
         "ECG confirms atrial fibrillation.", "Started on anticoagulation; review in two weeks.",
         "Stroke risk assessed; CHA2DS2-VASc score recorded."],
    ),
    "Angina": (
        ["Chest pain, shortness of breath", "Chest tightness on exertion, breathlessness",
         "Pressure behind the sternum, relieved by rest", "Exertional chest discomfort, jaw pain"],
        ["Nitroglycerin, aspirin, lifestyle changes", "Antianginal therapy, statin, smoking cessation",
         "GTN spray, beta-blocker, cardiac rehabilitation"],
        ["Recommend further cardiovascular evaluation.", "Stress test scheduled.",
         "Stable angina; medical management started.",
         "Advised urgent review if pain occurs at rest."],
    ),
    "Diabetes Mellitus": (
        ["Frequent urination, thirst, fatigue", "Excessive thirst, blurred vision, weight loss",
         "Increased appetite, slow-healing wounds", "Polyuria, polydipsia, tiredness"],
        ["Insulin therapy, diet control", "Metformin, dietary counselling, exercise plan",
         "Glucose monitoring, lifestyle modification"],
        ["Blood sugar levels elevated; initiate monitoring.",
         "HbA1c above target; treatment escalated.", "Referred to diabetes education programme.",
         "Annual retinal and foot screening arranged."],
    ),
    "Migraine": (
        ["Severe headache, nausea, light sensitivity", "Throbbing one-sided head pain, visual aura",
         "Headache with vomiting, sound sensitivity", "Pulsating headache lasting several hours"],
        ["Pain relief, rest in a dark room", "Triptans, antiemetic, trigger avoidance",
         "Prophylactic propranolol, hydration"],
        ["Classic migraine presentation.", "Headache diary advised to identify triggers.",
         "Aura reported before onset.", "Consider prophylaxis if frequency increases."],
    ),
    "Irritable Bowel Syndrome": (
        ["Abdominal pain, bloating, diarrhea", "Cramping, alternating constipation and diarrhea",
         "Bloating relieved by defecation, urgency", "Lower abdominal discomfort, irregular stools"],
        ["Diet changes, antispasmodic medication", "Low FODMAP diet, fibre supplementation",
         "Mebeverine, stress management, dietary review"],
        ["IBS symptoms; recommend low FODMAP diet.", "Red flag symptoms absent.",
         "Coeliac screen negative.", "Symptoms fluctuate with stress; reassurance given."],
    ),
    "Eczema": (
        ["Skin rash, itching, redness", "Dry scaly patches, intense itching",
         "Inflamed skin on elbows and knees", "Recurrent itchy rash, worse at night"],
        ["Topical corticosteroids, moisturizers", "Emollients, short steroid course",
         "Antihistamines, barrier cream, trigger avoidance"],
        ["Patient has recurring skin rash; allergy test suggested.",
         "Flare likely triggered by detergent change.",
         "Skin barrier compromised; emollient use reinforced.",
         "No signs of secondary bacterial infection."],
    ),
    "Rheumatoid Arthritis": (
        ["Joint pain, swelling, stiffness", "Morning stiffness lasting over an hour, swollen joints",
         "Symmetrical joint pain in hands and wrists", "Painful swollen knuckles, fatigue"],
        ["Anti-inflammatory drugs, physiotherapy", "Methotrexate, folic acid, rheumatology follow-up",
         "NSAIDs, physiotherapy, joint protection advice"],
        ["Early stages of rheumatoid arthritis detected.",
         "Rheumatoid factor positive.", "DAS28 score recorded at baseline.",
         "Referred to rheumatology for DMARD initiation."],
    ),
    "Tuberculosis": (
        ["Persistent cough, weight loss, night sweats", "Chronic cough with blood, fever",
         "Prolonged cough over three weeks, appetite loss", "Night sweats, fatigue, low-grade fever"],
        ["Antibiotics for 6-9 months", "Standard four-drug anti-TB regimen",
         "Directly observed therapy, contact tracing"],
        ["Signs of TB; sputum test recommended.", "Chest X-ray shows upper lobe changes.",
         "Notified to public health; contacts to be screened.",
         "Treatment adherence counselling provided."],
    ),
    "Herniated Disc": (
        ["Sharp back pain, numbness in legs", "Lower back pain radiating down one leg",
         "Shooting leg pain, tingling in the foot", "Back pain worsened by sitting, leg weakness"],
        ["Physical therapy, pain management", "Analgesia, physiotherapy, activity modification",
         "Neuropathic pain relief, core strengthening"],
        ["MRI suggested to confirm disc herniation.", "Straight leg raise positive on the right.",
         "No red flag neurology; conservative management.",
         "Refer to spinal surgery if no improvement in six weeks."],
    ),
    "Asthma": (
        ["Wheezing, breathlessness, chest tightness", "Night-time cough, wheeze after exercise",
         "Shortness of breath, audible wheeze", "Recurrent cough worse in cold air"],
        ["Inhaled corticosteroid, salbutamol reliever", "Preventer inhaler, spacer, technique review",
         "Bronchodilator therapy, asthma action plan"],
        ["Peak flow reduced; inhaler technique reviewed.",
         "Asthma control questionnaire completed.", "Trigger appears to be cold weather.",
         "Stepped up preventer therapy."],
    ),
    "Hypertension": (
        ["Headache, dizziness, blurred vision", "Often asymptomatic; found on routine check",
         "Occasional headache, nosebleeds", "Fatigue, elevated readings at home"],
        ["ACE inhibitor, salt reduction", "Amlodipine, lifestyle modification",
         "Diuretic therapy, home BP monitoring"],
        ["Blood pressure consistently above target.",
         "Ambulatory monitoring arranged.", "Cardiovascular risk score calculated.",
         "Advised reduced salt intake and regular exercise."],
    ),
    "Gastroesophageal Reflux": (
        ["Heartburn, acid taste, regurgitation", "Burning chest pain after meals",
         "Night-time cough, sour taste in mouth", "Discomfort worse lying flat"],
        ["Proton pump inhibitor, dietary advice", "Omeprazole, weight loss, avoid late meals",
         "Antacids, elevation of bed head"],
        ["Symptoms respond to PPI trial.", "No alarm features; endoscopy not indicated.",
         "Advised to avoid caffeine and spicy food.",
         "Review in eight weeks."],
    ),
    "Anemia": (
        ["Fatigue, pallor, shortness of breath", "Tiredness, dizziness on standing",
         "Weakness, cold hands, brittle nails", "Reduced exercise tolerance, pale conjunctiva"],
        ["Iron supplementation, dietary advice", "Ferrous sulphate, vitamin C with doses",
         "Investigate underlying cause, iron replacement"],
        ["Haemoglobin below reference range.",
         "Ferritin low; iron deficiency confirmed.", "Dietary iron intake discussed.",
         "Repeat full blood count in three months."],
    ),
    "Urinary Tract Infection": (
        ["Burning on urination, frequency, urgency", "Lower abdominal pain, cloudy urine",
         "Painful urination, foul-smelling urine", "Frequency with suprapubic discomfort"],
        ["Short course antibiotics, increased fluids", "Nitrofurantoin, hydration advice",
         "Trimethoprim, urine culture sent"],
        ["Dipstick positive for nitrites and leucocytes.",
         "Uncomplicated lower UTI.", "Advised to return if fever or flank pain develops.",
         "Culture sent before starting antibiotics."],
    ),
    "Hypothyroidism": (
        ["Fatigue, weight gain, cold intolerance", "Dry skin, hair thinning, low mood",
         "Constipation, sluggishness, puffy face", "Tiredness despite adequate sleep"],
        ["Levothyroxine replacement", "Thyroid hormone replacement, periodic TSH checks",
         "Levothyroxine titration, annual review"],
        ["TSH elevated with low free T4.", "Started on replacement; recheck in six weeks.",
         "Symptoms improving on current dose.", "Thyroid antibodies positive."],
    ),
    "Osteoarthritis": (
        ["Joint pain worse with activity, stiffness", "Knee pain on stairs, crepitus",
         "Aching hips after walking, reduced range", "Stiff joints easing after movement"],
        ["Analgesia, weight management, physiotherapy", "Paracetamol, topical NSAIDs, exercise",
         "Joint protection advice, strengthening programme"],
        ["X-ray shows joint space narrowing.",
         "Conservative management appropriate.", "Weight reduction discussed.",
         "Consider orthopaedic referral if function declines."],
    ),
    "Pneumonia": (
        ["Productive cough, fever, chest pain", "Breathlessness, high fever, green sputum",
         "Cough with pleuritic pain, rigors", "Fever, rapid breathing, fatigue"],
        ["Antibiotics, rest, fluids", "Amoxicillin, hydration, review in 48 hours",
         "Oral antibiotics, oxygen if saturations fall"],
        ["Crackles heard at the right base.",
         "CURB-65 score low; managed in community.", "Chest X-ray confirms consolidation.",
         "Safety netting advice given."],
    ),
    "Allergic Rhinitis": (
        ["Sneezing, runny nose, itchy eyes", "Nasal congestion, watery eyes, seasonal pattern",
         "Blocked nose, postnasal drip", "Itchy palate, repeated sneezing outdoors"],
        ["Antihistamine, nasal steroid spray", "Loratadine, allergen avoidance",
         "Intranasal corticosteroid, saline rinse"],
        ["Symptoms follow a seasonal pattern.",
         "Likely pollen trigger.", "Nasal spray technique demonstrated.",
         "Consider allergy testing if poorly controlled."],
    ),
    "Depression": (
        ["Low mood, loss of interest, poor sleep", "Persistent sadness, low energy, poor appetite",
         "Difficulty concentrating, early waking", "Hopelessness, social withdrawal"],
        ["Talking therapy referral, regular review", "SSRI, psychological therapy",
         "Structured exercise, counselling, follow-up"],
        ["PHQ-9 score in moderate range.",
         "Risk assessed; no immediate safety concerns.", "Referred for cognitive behavioural therapy.",
         "Review arranged in two weeks."],
    ),
}

DOCTORS = ["Dr. Mehta", "Dr. Iyer", "Dr. Kapoor", "Dr. Rao", "Dr. Fernandes",
           "Dr. Banerjee", "Dr. Nair", "Dr. Chawla"]


def main() -> None:
    rng = random.Random(SEED)
    names = list(CONDITIONS)
    rows = []

    for i in range(RECORD_COUNT):
        diagnosis = names[i % len(names)]
        symptoms, treatments, notes = CONDITIONS[diagnosis]
        note = rng.choice(notes)
        rows.append({
            "patient_id": f"PT-{1000 + i}",
            "symptoms": rng.choice(symptoms),
            "diagnosis": diagnosis,
            "treatment": rng.choice(treatments),
            "doctor_notes": f"{note} Reviewed by {rng.choice(DOCTORS)}.",
        })

    rng.shuffle(rows)
    for i, row in enumerate(rows):
        row["patient_id"] = f"PT-{1000 + i}"

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["patient_id", "symptoms", "diagnosis", "treatment", "doctor_notes"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} records to {OUTPUT.name}")


if __name__ == "__main__":
    main()
