# -*- coding: utf-8 -*-

"""
medical_chatbot_web.py
Medical Triage Chatbot (Clean Version):
- Logic: Full Symptom & Medication Database
- UI: Modern Chat Interface with Blue/Red Medical Cards
- Features: Typing Animation, User Auth, History
"""
import re
import json
import random
import os
import sys
import hashlib
import time
from datetime import datetime
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import nltk
from difflib import get_close_matches
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

# NLTK resource
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'medical_chatbot_secret_key'  # Change this in production

# -------------------------
# Paths & persistence files
# -------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent / "data"
else:
    BASE_DIR = Path(__file__).parent / "data"

BASE_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)
USERS_FILE = BASE_DIR / "users.txt"
DEBUG_LOG = BASE_DIR / "debug.log"

if not USERS_FILE.exists(): USERS_FILE.touch()
if not DEBUG_LOG.exists(): DEBUG_LOG.touch()

def debug_log(message):
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} - {message}\n")
    except Exception as e:
        print(f"[Error] Could not write to debug log: {e}")

# -------------------------
# Helper: password hashing
# -------------------------
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

# -------------------------
# User storage helpers
# -------------------------
def load_users():
    users = {}
    if USERS_FILE.exists():
        for line in USERS_FILE.read_text(encoding='utf-8').splitlines():
            if ':' in line:
                u, h = line.split(':', 1)
                users[u.strip()] = h.strip()
    return users

def save_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    with USERS_FILE.open('a', encoding='utf-8') as f:
        f.write(f"{username}:{_hash(password)}\n")
    return True

# -------------------------
# FULL Training data
# -------------------------
TRAINING = [
    # Greetings
    ("hello", "greeting"), ("hi", "greeting"), ("hey", "greeting"),
    ("good morning", "greeting"), ("good evening", "greeting"), ("hey there", "greeting"),
    ("hi there", "greeting"), ("yo", "greeting"), ("greetings", "greeting"),
    ("how are you", "greeting"), ("what's up", "greeting"), ("nice to meet you", "greeting"),
    
    # Thanks
    ("thanks", "thanks"), ("thank you", "thanks"), ("thx", "thanks"), ("appreciate it", "thanks"),
    ("thank you very much", "thanks"), ("thanks a lot", "thanks"), ("i appreciate your help", "thanks"),
    ("much appreciated", "thanks"), ("you're a lifesaver", "thanks"), ("thank you for your assistance", "thanks"),
    
    # Goodbye
    ("bye", "goodbye"), ("goodbye", "goodbye"), ("see you", "goodbye"), ("talk later", "goodbye"),
    ("see ya", "goodbye"), ("later", "goodbye"), ("catch you later", "goodbye"),
    ("i have to go now", "goodbye"), ("farewell", "goodbye"), ("take care", "goodbye"),
    
    # Symptom reports - Single symptoms
    ("i have a headache", "symptom_report"), ("my head hurts", "symptom_report"),
    ("i am feeling dizzy", "symptom_report"), ("i have chest pain", "symptom_report"),
    ("i feel short of breath", "symptom_report"), ("i am coughing a lot", "symptom_report"),
    ("i have a sore throat", "symptom_report"), ("i am vomiting", "symptom_report"),
    ("i have diarrhea", "symptom_report"), ("i cut my leg", "symptom_report"),
    ("my arm is swollen", "symptom_report"), ("i have a fever", "symptom_report"),
    ("i feel faint", "symptom_report"), ("i am bleeding a lot", "symptom_report"),
    ("my back hurts", "symptom_report"), ("pain in my stomach", "symptom_report"),
    ("i twisted my ankle", "symptom_report"), ("my tooth hurts", "symptom_report"),
    ("i have a rash", "symptom_report"), ("i feel nauseous", "symptom_report"),
    ("i have muscle cramps", "symptom_report"), ("my muscles are cramping", "symptom_report"),
    ("i have eye strain", "symptom_report"), ("my eyes feel tired", "symptom_report"),
    ("i have heartburn", "symptom_report"), ("i feel burning in my chest", "symptom_report"),
    ("i have constipation", "symptom_report"), ("i can't have a bowel movement", "symptom_report"),
    ("i have insomnia", "symptom_report"), ("i can't sleep at night", "symptom_report"),
    ("i have allergies", "symptom_report"), ("i am having an allergic reaction", "symptom_report"),
    ("i have sinus pressure", "symptom_report"), ("my sinuses feel full", "symptom_report"),
    ("i have anxiety", "symptom_report"), ("i feel anxious all the time", "symptom_report"),
    ("i have fatigue", "symptom_report"), ("i feel exhausted all the time", "symptom_report"),
    ("i have joint pain", "symptom_report"), ("my joints are aching", "symptom_report"),
    ("i have ear pain", "symptom_report"), ("my ear is hurting", "symptom_report"),
    ("i have a runny nose", "symptom_report"), ("my nose keeps running", "symptom_report"),
    ("i have congestion", "symptom_report"), ("my chest feels congested", "symptom_report"),
    
    # Mixed symptoms
    ("i have fever and cough", "symptom_report"), ("headache and nausea", "symptom_report"),
    ("chest pain with dizziness", "symptom_report"), ("vomiting and diarrhea", "symptom_report"),
    ("sore throat with fever", "symptom_report"), ("back pain and leg pain", "symptom_report"),
    ("rash and itching", "symptom_report"), ("abdominal pain with vomiting", "symptom_report"),
    ("cold with body ache", "symptom_report"), ("fever and chills", "symptom_report"),
    ("cough and congestion", "symptom_report"), ("headache with light sensitivity", "symptom_report"),
    ("fatigue and muscle pain", "symptom_report"), ("joint pain and swelling", "symptom_report"),
    ("ear pain and hearing loss", "symptom_report"), ("runny nose and sneezing", "symptom_report"),
    ("sinus pressure and headache", "symptom_report"), ("anxiety and palpitations", "symptom_report"),
    ("insomnia and fatigue", "symptom_report"), ("eye strain and headache", "symptom_report"),
    ("allergies and sneezing", "symptom_report"), ("constipation and abdominal pain", "symptom_report"),
    ("muscle cramps and weakness", "symptom_report"), ("heartburn and regurgitation", "symptom_report"),
    
    # Ask advice / escalation
    ("should I see a doctor?", "ask_escalation"),
    ("do I need to go to the hospital?", "ask_escalation"),
    ("is this an emergency?", "ask_escalation"),
    ("what should I do for my fever?", "ask_advice"),
    ("how to treat headache?", "ask_advice"),
    ("do I need urgent care?", "ask_escalation"),
    ("should I call 911?", "ask_escalation"),
    ("is my condition serious?", "ask_escalation"),
    ("help me with my symptoms", "ask_advice"),
    ("what can I take for this pain", "ask_advice"),
    ("what helps muscle cramps", "ask_advice"), ("how to prevent eye strain", "ask_advice"),
    ("what helps heartburn", "ask_advice"), ("how to relieve constipation", "ask_advice"),
    ("what to do for insomnia", "ask_advice"), ("how to manage allergies", "ask_advice"),
    ("what helps sinus pressure", "ask_advice"), ("how to reduce anxiety", "ask_advice"),
    ("what should I do for fatigue", "ask_advice"), ("how to treat joint pain", "ask_advice"),
    ("what helps ear pain", "ask_advice"), ("how to stop a runny nose", "ask_advice"),
    ("what should I do for congestion", "ask_advice"), ("how to treat a cold", "ask_advice"),
    ("what helps with chills", "ask_advice"), ("how to relieve nausea", "ask_advice"),
    ("what should I do for body aches", "ask_advice"), ("how to reduce swelling", "ask_advice"),
    ("what helps with itching", "ask_advice"), ("how to treat abdominal pain", "ask_advice"),
    ("what should I do for vomiting", "ask_advice"), ("how to relieve back pain", "ask_advice"),
    ("what helps with light sensitivity", "ask_advice"), ("how to treat muscle pain", "ask_advice"),
    ("what should I do for palpitations", "ask_advice"), ("how to relieve hearing loss", "ask_advice"),
    ("what helps with sneezing", "ask_advice"), ("how to treat sinus pressure", "ask_advice"),
    ("what should I do for fatigue", "ask_advice"), ("how to reduce anxiety", "ask_advice"),
    ("what helps with insomnia", "ask_advice"), ("how to relieve eye strain", "ask_advice"),
    ("what should I do for headache", "ask_advice"), ("how to treat fever", "ask_advice"),
    ("what helps with cough", "ask_advice"), ("how to relieve congestion", "ask_advice"),
    ("is this a medical emergency", "ask_escalation"), ("should I go to the ER", "ask_escalation"),
    ("do I need an ambulance", "ask_escalation"), ("is this life threatening", "ask_escalation"),
    ("should I be worried", "ask_escalation"), ("is this serious", "ask_escalation"),
    ("do I need immediate help", "ask_escalation"), ("should I call a doctor now", "ask_escalation"),
    ("is this an emergency situation", "ask_escalation"), ("do I need to go to urgent care", "ask_escalation"),
    
    # Medication info
    ("i took paracetamol", "took_med"), ("i took ibuprofen", "took_med"),
    ("i took medicine for fever", "took_med"), ("what are side effects of ibuprofen", "med_info"),
    ("side effects of paracetamol", "med_info"), ("can i take cetirizine", "med_info"),
    ("is aspirin safe for me", "med_info"), ("what does metformin do", "med_info"),
    ("what is omeprazole used for", "med_info"), ("side effects of atorvastatin", "med_info"),
    ("can i take lisinopril", "med_info"), ("what is sertraline for", "med_info"),
    ("how does albuterol work", "med_info"), ("side effects of prednisone", "med_info"),
    ("can i take aspirin with ibuprofen", "med_info"), ("what is the dosage for metformin", "med_info"),
    ("is omeprazole safe long term", "med_info"), ("can i drink alcohol with atorvastatin", "med_info"),
    ("what are the side effects of lisinopril", "med_info"), ("how long does sertraline take to work", "med_info"),
    ("can i use albuterol every day", "med_info"), ("how should i take prednisone", "med_info"),
    ("tell me about amoxicillin", "med_info"), ("what are the side effects of amoxicillin", "med_info"),
    ("is amoxicillin an antibiotic", "med_info"), ("how does amoxicillin work", "med_info"),
    
    # Non-medical queries (to be rejected)
    ("what is the weather today", "non_medical"), ("tell me a joke", "non_medical"),
    ("who won the game", "non_medical"), ("what's your favorite movie", "non_medical"),
    ("how old are you", "non_medical"), ("do you have pets", "non_medical"),
    ("where do you live", "non_medical"), ("what's your favorite color", "non_medical"),
    ("can you sing", "non_medical"), ("do you love me", "non_medical"),
    ("what's the capital of France", "non_medical"), ("tell me about politics", "non_medical"),
    ("what's the latest news", "non_medical"), ("who is the president", "non_medical"),
    ("what's the stock market doing", "non_medical"), ("what's your favorite food", "non_medical"),
    ("do you believe in god", "non_medical"), ("what's your favorite song", "non_medical"),
    ("can you dance", "non_medical"), ("do you have a girlfriend", "non_medical"),
    ("what's your favorite book", "non_medical"), ("what's your favorite sport", "non_medical"),
    ("do you like animals", "non_medical"), ("what's your favorite TV show", "non_medical"),
    
    # General knowledge (medical only)
    ("what is a chatbot", "general_knowledge"),
    ("what is artificial intelligence", "general_knowledge"),
    ("how do chatbots work", "general_knowledge"),
    ("what is hypertension", "general_knowledge"),
    ("what is diabetes", "general_knowledge"),
    ("what is asthma", "general_knowledge"),
    ("what is a migraine", "general_knowledge"),
    ("what is cholesterol", "general_knowledge"),
    ("what is blood pressure", "general_knowledge"),
    ("what is the immune system", "general_knowledge"),
    ("what is inflammation", "general_knowledge"),
    ("what is a virus", "general_knowledge"),
    ("what is bacteria", "general_knowledge"),
    ("what is an infection", "general_knowledge"),
    ("what is a vaccine", "general_knowledge"),
    ("what is a tumor", "general_knowledge"),
    ("what is cancer", "general_knowledge"),
    ("what is chemotherapy", "general_knowledge"),
    ("what is radiation therapy", "general_knowledge"),
    ("what is physical therapy", "general_knowledge"),
    ("what is occupational therapy", "general_knowledge"),
]

# -------------------------
# FULL Symptom KB + synonyms
# -------------------------
SYMPTOM_KB = {
    "fever": ["Viral infection", "Bacterial infection", "Inflammatory condition"],
    "cough": ["Upper respiratory infection", "Bronchitis", "Pneumonia"],
    "chest pain": ["Cardiac ischemia (possible)", "Angina", "Musculoskeletal pain"],
    "difficulty breathing": ["Asthma exacerbation", "Pneumonia", "Pulmonary embolism"],
    "bleeding": ["Acute hemorrhage – possible emergency"],
    "severe bleeding": ["Acute hemorrhage – immediate ER"],
    "vomiting": ["Gastroenteritis", "Food poisoning"],
    "diarrhea": ["Gastroenteritis", "Food poisoning"],
    "headache": ["Tension headache", "Migraine", "Meningitis (rare)"],
    "dizziness": ["Dehydration", "Syncope", "Arrhythmia (rare)"],
    "sore throat": ["Pharyngitis", "Strep throat"],
    "leg pain": ["Sprain/strain", "Fracture (trauma)"],
    "back pain": ["Muscle strain", "Herniated disc (possible)"],
    "abdominal pain": ["Indigestion", "Gastritis", "Appendicitis (consider if severe)"],
    "tooth pain": ["Dental caries", "Pulpitis"],
    "rash": ["Allergic reaction", "Contact dermatitis"],
    "nausea": ["Gastroenteritis", "Migraine"],
    "muscle cramps": ["Dehydration", "Electrolyte imbalance", "Overexertion"],
    "eye strain": ["Digital eye strain", "Uncorrected vision", "Dry eyes"],
    "heartburn": ["GERD", "Acid reflux", "Hiatal hernia"],
    "constipation": ["Low fiber diet", "Dehydration", "Sedentary lifestyle"],
    "insomnia": ["Stress", "Poor sleep hygiene", "Caffeine intake"],
    "allergies": ["Seasonal allergies", "Food allergies", "Environmental triggers"],
    "sinus pressure": ["Sinus infection", "Allergies", "Cold"],
    "anxiety": ["Stress disorder", "Panic disorder", "Generalized anxiety"],
    "fatigue": ["Anemia", "Sleep apnea", "Chronic fatigue syndrome"],
    "joint pain": ["Arthritis", "Injury", "Autoimmune disorder"],
    "ear pain": ["Ear infection", "Earwax blockage", "Eustachian tube dysfunction"],
    "runny nose": ["Common cold", "Allergies", "Sinus infection"],
    "congestion": ["Common cold", "Flu", "Sinus infection"],
    "chills": ["Fever", "Infection", "Exposure to cold"],
    "body ache": ["Flu", "Viral infection", "Fibromyalgia"],
    "itching": ["Allergic reaction", "Skin condition", "Insect bite"],
    "swelling": ["Injury", "Infection", "Edema"],
    "light sensitivity": ["Migraine", "Eye condition", "Meningitis"],
    "muscle pain": ["Overexertion", "Infection", "Autoimmune condition"],
    "palpitations": ["Anxiety", "Arrhythmia", "Heart condition"],
    "hearing loss": ["Ear infection", "Earwax blockage", "Age-related"],
    "sneezing": ["Allergies", "Common cold", "Irritants"],
    "regurgitation": ["GERD", "Acid reflux", "Hiatal hernia"],
    "weakness": ["Fatigue", "Electrolyte imbalance", "Neurological condition"],
}

SYMPTOM_SYNONYMS = {
    "chest pain": ["chest ache", "tightness in chest", "pressure in chest"],
    "headache": ["head pain", "migraine", "pressure in head"],
    "difficulty breathing": ["shortness of breath", "cant breathe", "breathing difficulty"],
    "bleeding": ["blood loss", "blood everywhere", "severe bleeding"],
    "vomiting": ["throwing up", "emesis"],
    "diarrhea": ["loose stools", "runny stool"],
    "dizziness": ["lightheaded", "vertigo", "fainting"],
    "back pain": ["low back pain", "lumbago"],
    "abdominal pain": ["stomach ache", "belly pain", "tummy pain"],
    "tooth pain": ["toothache", "teeth pain"],
    "nausea": ["feeling sick", "queasy"],
    "muscle cramps": ["charley horse", "muscle spasm", "leg cramp"],
    "eye strain": ["tired eyes", "eye fatigue", "computer vision syndrome"],
    "heartburn": ["acid indigestion", "pyrosis", "stomach burn"],
    "constipation": ["irregular bowel", "hard stool", "difficulty passing stool"],
    "insomnia": ["sleeplessness", "can't sleep", "sleep deprivation"],
    "allergies": ["hay fever", "allergic reaction", "hypersensitivity"],
    "sinus pressure": ["sinus congestion", "sinus pain", "stuffy sinuses"],
    "anxiety": ["nervousness", "worry", "panic"],
    "fatigue": ["tiredness", "exhaustion", "lack of energy"],
    "joint pain": ["joint ache", "arthralgia", "stiff joints"],
    "ear pain": ["earache", "ear discomfort", "ear throbbing"],
    "runny nose": ["rhinorrhea", "stuffy nose", "nasal discharge"],
    "congestion": ["stuffy chest", "chest congestion", "blocked nose"],
    "chills": ["shivering", "rigors", "cold sweats"],
    "body ache": ["body pain", "muscle ache", "generalized pain"],
    "itching": ["pruritus", "scratchy", "irritated skin"],
    "swelling": ["edema", "puffiness", "inflammation"],
    "light sensitivity": ["photophobia", "light hurts eyes", "eye discomfort in light"],
    "muscle pain": ["myalgia", "muscle ache", "sore muscles"],
    "palpitations": ["heart racing", "heart pounding", "irregular heartbeat"],
    "hearing loss": ["deafness", "hard of hearing", "muffled hearing"],
    "sneezing": ["sternutation", "sneeze fit", "nasal explosion"],
    "regurgitation": ["acid reflux", "sour burps", "food coming back up"],
    "weakness": ["lethargy", "lack of strength", "powerlessness"],
}

# -------------------------
# FAQ knowledge base
# -------------------------
FAQ = {
    "what is fever": "Fever is a temporary increase in body temperature, often due to infection.",
    "how to treat headache": "Rest, hydration, and over-the-counter pain relief like paracetamol can help headache.",
    "what is cough": "Cough is a reflex to clear your airways; can be due to infection, allergy, or irritation.",
    "how to treat diarrhea": "Stay hydrated and consider ORS; consult doctor if persists.",
    "what is chest pain": "Chest pain can be cardiac, respiratory, or musculoskeletal; seek immediate care if severe.",
    "how to manage dizziness": "Sit or lie down until it passes; drink water and monitor symptoms.",
    "what is sore throat": "A sore throat can be caused by viral or bacterial infections; rest and hydration help.",
    "how to treat vomiting": "Stay hydrated, eat small meals, and consult a doctor if vomiting persists.",
    "what is shortness of breath": "Shortness of breath can be due to asthma, infection, or heart problems; seek urgent care if severe.",
    "how to treat mild fever": "Rest, drink plenty of fluids, and consider paracetamol if needed.",
    "what is dehydration": "Dehydration occurs when your body loses more fluids than it takes in; drink water and oral rehydration solutions.",
    "how to treat minor cuts": "Clean the wound, apply antiseptic, and cover with a bandage. Seek medical attention if bleeding persists.",
    "what is migraine": "A migraine is a severe headache often accompanied by nausea, light sensitivity, or visual changes.",
    "how to prevent cold": "Wash hands frequently, avoid close contact with sick people, and maintain a healthy lifestyle.",
    "what is influenza": "Influenza is a viral infection causing fever, cough, sore throat, and body aches; vaccination helps prevent it.",
    "when to see a doctor for fever": "Adults: persistent >3 days, >102°F (38.9°C), or with rash/breathing issues; children: follow pediatric guidance.",
    "is chest tightness serious": "Yes, treat as urgent—may indicate heart or lung issues.",
    "what is chatbot": "A chatbot is a computer program designed to simulate conversation with human users, especially over the internet.",
    "what causes muscle cramps": "Muscle cramps can be caused by dehydration, electrolyte imbalances, or overexertion.",
    "how to prevent eye strain": "Follow the 20-20-20 rule, use proper lighting, and take regular breaks from screens.",
    "what helps heartburn": "Avoid spicy foods, eat smaller meals, and don't lie down after eating.",
    "how to relieve constipation": "Increase fiber intake, drink plenty of water, and exercise regularly.",
    "what to do for insomnia": "Establish a regular sleep schedule, avoid caffeine before bed, and create a relaxing bedtime routine.",
    "how to manage allergies": "Identify and avoid triggers, use over-the-counter antihistamines, and keep windows closed during high pollen seasons.",
    "what helps sinus pressure": "Use saline nasal spray, apply warm compresses, and stay hydrated.",
    "how to reduce anxiety": "Practice deep breathing exercises, exercise regularly, and consider mindfulness meditation.",
    "what is fatigue": "Fatigue is a feeling of constant tiredness or weakness that can be physical, mental, or both.",
    "how to treat joint pain": "Rest, apply ice or heat, and consider over-the-counter pain relievers. See a doctor if persistent.",
    "what causes ear pain": "Ear pain can be caused by ear infections, earwax blockage, or changes in pressure.",
    "how to stop a runny nose": "Stay hydrated, use saline nasal spray, and consider antihistamines if allergies are the cause.",
    "what is congestion": "Congestion is the buildup of fluid in tissues, often in the chest or nasal passages, making it hard to breathe.",
    "how to treat body aches": "Rest, stay hydrated, and consider over-the-counter pain relievers. Seek medical attention if severe.",
    "what causes chills": "Chills are often caused by fever, exposure to cold, or bacterial/viral infections.",
    "how to relieve itching": "Apply cold compress, take antihistamines, and avoid scratching. See a doctor if persistent.",
    "what causes swelling": "Swelling can be caused by injury, infection, inflammation, or fluid retention.",
    "how to treat light sensitivity": "Rest in a dark room, avoid bright lights, and consider sunglasses. See a doctor if severe.",
    "what causes muscle pain": "Muscle pain can be caused by overexertion, injury, infection, or certain medications.",
    "how to manage palpitations": "Practice relaxation techniques, avoid caffeine, and see a doctor if frequent.",
    "what causes hearing loss": "Hearing loss can be caused by aging, noise exposure, ear infections, or certain medications.",
    "how to stop sneezing": "Identify and avoid triggers, use saline nasal spray, and consider antihistamines.",
    "what causes regurgitation": "Regurgitation is often caused by GERD, acid reflux, or hiatal hernia.",
    "how to treat weakness": "Rest, stay hydrated, and eat a balanced diet. See a doctor if persistent or severe.",
    "what is hypertension": "Hypertension, or high blood pressure, is a condition where the force of blood against artery walls is too high.",
    "what is diabetes": "Diabetes is a chronic condition that affects how your body processes blood sugar (glucose).",
    "what is asthma": "Asthma is a condition that causes airways to narrow and swell, producing extra mucus and making breathing difficult.",
    "what is cholesterol": "Cholesterol is a waxy substance found in your blood that your body needs to build healthy cells, but high levels can increase heart disease risk.",
    "what is blood pressure": "Blood pressure is the force of blood pushing against artery walls as your heart pumps blood.",
    "what is the immune system": "The immune system is your body's defense against infectious organisms and other invaders.",
    "what is inflammation": "Inflammation is your body's response to injury or infection, causing redness, heat, swelling, and pain.",
    "what is a virus": "A virus is a small infectious agent that replicates only inside the living cells of an organism.",
    "what is bacteria": "Bacteria are single-celled microorganisms that can live in diverse environments, some cause disease while others are beneficial.",
    "what is an infection": "An infection occurs when harmful organisms like bacteria or viruses invade your body and multiply.",
    "what is a vaccine": "A vaccine is a biological preparation that provides immunity to a particular infectious disease.",
    "what is a tumor": "A tumor is an abnormal mass of tissue that forms when cells grow and divide more than they should or do not die when they should.",
    "what is cancer": "Cancer is a disease in which abnormal cells divide uncontrollably and destroy body tissue.",
    "what is chemotherapy": "Chemotherapy is a drug treatment that uses powerful chemicals to kill fast-growing cells in your body.",
    "what is radiation therapy": "Radiation therapy uses high-energy particles or waves to destroy or damage cancer cells.",
    "what is physical therapy": "Physical therapy is treatment to restore, maintain, and make the most of a patient's mobility, function, and well-being.",
    "what is occupational therapy": "Occupational therapy helps people participate in the activities they want and need to do through the therapeutic use of everyday activities.",
}

# -------------------------
# FULL Medications & side effects
# -------------------------
MEDICATIONS = {
    "paracetamol": {
        "uses": "Pain relief, fever reduction.",
        "dose_note": "Follow label; avoid exceeding maximum daily dose.",
        "side_effects": ["Nausea", "Rash (rare)", "Liver damage if overdosed"],
        "cautions": "Avoid combining with other acetaminophen-containing products."
    },
    "ibuprofen": {
        "uses": "Pain relief, anti-inflammatory.",
        "dose_note": "Take with food; follow label.",
        "side_effects": ["Stomach upset", "Heartburn", "Increased bleeding risk"],
        "cautions": "Avoid if you have ulcers/kidney disease unless advised by a clinician."
    },
    "cetirizine": {
        "uses": "Allergy relief (antihistamine).",
        "dose_note": "Once daily typical adult dose.",
        "side_effects": ["Drowsiness", "Dry mouth"],
        "cautions": "May cause sedation; avoid driving if drowsy."
    },
    "ondansetron": {
        "uses": "Nausea/vomiting (by prescription).",
        "dose_note": "Use only as prescribed.",
        "side_effects": ["Headache", "Constipation"],
        "cautions": "Can affect heart rhythm in susceptible people."
    },
    "aspirin": {
        "uses": "Pain relief, fever reduction, blood thinner.",
        "dose_note": "Follow label; avoid in children under 18.",
        "side_effects": ["Stomach irritation", "Increased bleeding risk", "Tinnitus"],
        "cautions": "Avoid if allergic, with bleeding disorders, or during pregnancy."
    },
    "omeprazole": {
        "uses": "Reduces stomach acid production.",
        "dose_note": "Take before breakfast; may take several days to work.",
        "side_effects": ["Headache", "Nausea", "Diarrhea", "Vitamin B12 deficiency with long-term use"],
        "cautions": "Long-term use requires monitoring; may interact with other medications."
    },
    "metformin": {
        "uses": "Controls blood sugar in type 2 diabetes.",
        "dose_note": "Take with meals to reduce stomach upset.",
        "side_effects": ["Stomach upset", "Diarrhea", "Metallic taste", "Vitamin B12 deficiency"],
        "cautions": "Avoid in severe kidney disease; monitor blood sugar regularly."
    },
    "atorvastatin": {
        "uses": "Lowers cholesterol levels.",
        "dose_note": "Take once daily; can be taken any time of day.",
        "side_effects": ["Muscle pain", "Liver enzyme elevation", "Digestive problems"],
        "cautions": "Avoid grapefruit; monitor liver function; report muscle pain."
    },
    "lisinopril": {
        "uses": "Lowers blood pressure, protects kidneys in diabetes.",
        "dose_note": "Take once daily; can be taken with or without food.",
        "side_effects": ["Dry cough", "Dizziness", "Increased potassium", "Taste changes"],
        "cautions": "Avoid during pregnancy; monitor kidney function and potassium."
    },
    "sertraline": {
        "uses": "Treats depression, anxiety, OCD.",
        "dose_note": "Take once daily; may take 4-6 weeks for full effect.",
        "side_effects": ["Nausea", "Insomnia", "Sexual dysfunction", "Dry mouth"],
        "cautions": "Avoid with MAO inhibitors; monitor for worsening depression."
    },
    "albuterol": {
        "uses": "Relieves asthma attacks and COPD symptoms.",
        "dose_note": "Use as needed for breathing problems; shake well before use.",
        "side_effects": ["Tremor", "Rapid heartbeat", "Nervousness", "Headache"],
        "cautions": "Overuse can worsen symptoms; clean inhaler regularly."
    },
    "prednisone": {
        "uses": "Reduces inflammation, treats autoimmune conditions.",
        "dose_note": "Take with food to prevent stomach upset; taper dose when stopping.",
        "side_effects": ["Increased appetite", "Mood changes", "Insomnia", "Increased infection risk"],
        "cautions": "Don't stop suddenly; avoid live vaccines; monitor blood sugar."
    },
    "amoxicillin": {
        "uses": "Antibiotic for bacterial infections.",
        "dose_note": "Take as prescribed; complete full course.",
        "side_effects": ["Diarrhea", "Nausea", "Rash", "Yeast infection"],
        "cautions": "Report severe diarrhea or allergic reaction."
    },
    "hydrochlorothiazide": {
        "uses": "Diuretic for high blood pressure and fluid retention.",
        "dose_note": "Take in morning to avoid nighttime urination.",
        "side_effects": ["Frequent urination", "Dizziness", "Electrolyte imbalance"],
        "cautions": "Monitor potassium levels; may increase blood sugar."
    },
    "simvastatin": {
        "uses": "Lowers cholesterol levels.",
        "dose_note": "Take in evening; avoid grapefruit.",
        "side_effects": ["Muscle pain", "Headache", "Nausea", "Liver enzyme elevation"],
        "cautions": "Report muscle pain; monitor liver function."
    },
    "losartan": {
        "uses": "Lowers blood pressure, protects kidneys.",
        "dose_note": "Take once daily with or without food.",
        "side_effects": ["Dizziness", "Fatigue", "Hyperkalemia"],
        "cautions": "Avoid during pregnancy; monitor potassium levels."
    },
    "fluoxetine": {
        "uses": "Treats depression, anxiety, OCD.",
        "dose_note": "Take once daily; may take 4-6 weeks for full effect.",
        "side_effects": ["Nausea", "Insomnia", "Headache", "Sexual dysfunction"],
        "cautions": "Avoid with MAO inhibitors; monitor for worsening depression."
    },
    "levothyroxine": {
        "uses": "Treats hypothyroidism.",
        "dose_note": "Take on empty stomach in morning; wait 30-60 min before eating.",
        "side_effects": ["Palpitations", "Weight loss", "Heat intolerance"],
        "cautions": "Monitor thyroid levels regularly; report heart symptoms."
    },
    "gabapentin": {
        "uses": "Treats nerve pain and seizures.",
        "dose_note": "Take as prescribed; do not stop suddenly.",
        "side_effects": ["Dizziness", "Drowsiness", "Fatigue", "Peripheral edema"],
        "cautions": "Avoid alcohol; may cause suicidal thoughts."
    },
    "furosemide": {
        "uses": "Diuretic for fluid retention and high blood pressure.",
        "dose_note": "Take as prescribed; may need to take in morning.",
        "side_effects": ["Frequent urination", "Dizziness", "Electrolyte imbalance"],
        "cautions": "Monitor potassium levels; may cause dehydration."
    },
    "diphenhydramine": {
        "uses": "Allergy relief, sleep aid, motion sickness prevention.",
        "dose_note": "Follow label instructions; take with food if stomach upset occurs.",
        "side_effects": ["Drowsiness", "Dizziness", "Dry mouth", "Blurred vision"],
        "cautions": "Avoid alcohol and driving; may cause confusion in elderly."
    },
}

# -------------------------
# Mapping Symptoms to OTC Meds
# -------------------------
SYMPTOM_OTC_SUGGESTIONS = {
    "fever": ["paracetamol", "ibuprofen", "aspirin"],
    "headache": ["paracetamol", "ibuprofen", "aspirin"],
    "muscle pain": ["ibuprofen", "paracetamol"],
    "back pain": ["ibuprofen", "paracetamol"],
    "joint pain": ["ibuprofen"],
    "tooth pain": ["ibuprofen", "paracetamol"],
    "abdominal pain": ["paracetamol"], 
    "allergies": ["cetirizine", "diphenhydramine"],
    "runny nose": ["cetirizine"],
    "sneezing": ["cetirizine"],
    "itching": ["cetirizine", "diphenhydramine"],
    "heartburn": ["omeprazole"],
    "regurgitation": ["omeprazole"],
    "insomnia": ["diphenhydramine"],
    "cough": ["albuterol"], 
    "difficulty breathing": ["albuterol"],
    "rash": ["cetirizine"],
    "inflammation": ["ibuprofen", "prednisone"],
    "nausea": ["ondansetron"],
    "vomiting": ["ondansetron"]
}

# -------------------------
# Red-flags
# -------------------------
REDFLAGS = [
    (re.compile(r"\b(chest pain|pressure in chest)\b", re.I), "Chest pain / pressure"),
    (re.compile(r"\b(difficulty breathing|shortness of breath|cant breathe|can't breathe)\b", re.I), "Difficulty breathing / respiratory distress"),
    (re.compile(r"\b(bleeding a lot|severe bleeding|blood everywhere)\b", re.I), "Severe external bleeding"),
    (re.compile(r"\b(unconscious|fainting|lost consciousness|not responding)\b", re.I), "Loss of consciousness"),
    (re.compile(r"\b(weak on one side|slurred speech|facial droop)\b", re.I), "Stroke-like symptoms"),
    (re.compile(r"\b(suicidal|want to die|kill myself)\b", re.I), "Self-harm / suicidal ideation"),
    (re.compile(r"\b(severe headache|worst headache)\b", re.I), "Severe headache"),
    (re.compile(r"\b(allergic reaction|anaphylaxis)\b", re.I), "Severe allergic reaction"),
    (re.compile(r"\b(confusion|disoriented)\b", re.I), "Confusion / disorientation"),
    (re.compile(r"\b(high fever|very high temperature)\b", re.I), "High fever"),
    # Fever temperature conditions
    (re.compile(r"\bfever (of |over |above )?10[0-9]\b", re.I), "High fever (100°F or above)"),
    (re.compile(r"\btemperature (of |over |above )?10[0-9]\b", re.I), "High temperature (100°F or above)"),
]

# -------------------------
# ML Model
# -------------------------
vectorizer = TfidfVectorizer()
clf = LogisticRegression(max_iter=500)

# -------------------------
# Train and predict
# -------------------------
def train_intent_model():
    texts = [t for t,_ in TRAINING]
    labels = [l for _,l in TRAINING]
    X = vectorizer.fit_transform(texts)
    clf.fit(X, labels)
    debug_log("Intent model trained successfully")

def predict_intent(text):
    X = vectorizer.transform([text])
    label = clf.predict(X)[0]
    conf = float(max(clf.predict_proba(X)[0])) if hasattr(clf, 'predict_proba') else 1.0
    debug_log(f"Predicted intent: {label} with confidence: {conf}")
    if any(k in text.lower() for k in ["side effect", "side effects", "can i take", "medication", "dose", "tell me about", "information about"]):
        label = "med_info"
        debug_log("Overrode intent to med_info based on keywords")
    return label, conf

# -------------------------
# Symptom extraction
# -------------------------
def extract_symptoms(text):
    text = text.lower()
    found = set()
    fever_temp = None
    
    fever_patterns = [
        re.compile(r"\bfever (of |over |above )?(\d{1,3})\.?(\d*)\b", re.I),
        re.compile(r"\btemperature (of |over |above )?(\d{1,3})\.?(\d*)\b", re.I),
        re.compile(r"\btemp (of |over |above )?(\d{1,3})\.?(\d*)\b", re.I)
    ]
    
    for pattern in fever_patterns:
        match = pattern.search(text)
        if match:
            try:
                temp = float(match.group(2))
                if match.group(3): temp += float(f"0.{match.group(3)}")
                fever_temp = temp
                found.add("fever")
                break
            except (ValueError, IndexError): continue
    
    for symptom in SYMPTOM_KB.keys():
        if symptom in text: found.add(symptom)
        for syn in SYMPTOM_SYNONYMS.get(symptom, []):
            if syn in text: found.add(symptom)
            
    words = re.findall(r'\b\w+\b', text)
    for word in words:
        match = get_close_matches(word, SYMPTOM_KB.keys(), n=1, cutoff=0.85)
        if match: found.add(match[0])
        
    if re.search(r"\b(fever|temperature|hot)\b", text) and "fever" not in found:
        found.add("fever")
        
    m = re.search(r"\bpain (in|on) my (\w+)", text)
    if m:
        region = m.group(2)
        mapping = {'stomach': 'abdominal pain', 'belly': 'abdominal pain', 'back': 'back pain', 'tooth': 'tooth pain', 'leg': 'leg pain'}
        found.add(mapping.get(region, region))
        
    return list(found), fever_temp

def emergency_alert(text):
    alerts = []
    for pattern, desc in REDFLAGS:
        if pattern.search(text): alerts.append(desc)
    return alerts

# -------------------------
# Logic
# -------------------------
def run_triage(symptoms, text, fever_temp=None):
    explanation = []
    
    # Priority 1: High Fever Check
    if fever_temp is not None:
        if fever_temp >= 100.0:
            explanation.append(f"High fever detected: {fever_temp}°F")
            probable = {s: SYMPTOM_KB.get(s, ["Symptom noted"]) for s in symptoms}
            return {"triage_level": "EMERGENCY", "recommendation": "Seek immediate emergency care.", "explanation": explanation, "probable_conditions": probable, "alerts": []}
        else:
            explanation.append(f"Low-grade fever detected: {fever_temp}°F")
            probable = {s: SYMPTOM_KB.get(s, ["Symptom noted"]) for s in symptoms}
            return {"triage_level": "NON-URGENT", "recommendation": "Rest, hydrate, and monitor symptoms.", "explanation": explanation, "probable_conditions": probable, "alerts": []}
    
    # Priority 2: Red Flags
    alerts = emergency_alert(text)
    if alerts:
        explanation.append(f"RED-FLAG triggered: {', '.join(alerts)}")
        probable = {s: SYMPTOM_KB.get(s, ["Symptom noted"]) for s in symptoms}
        return {"triage_level": "EMERGENCY", "recommendation": "Seek immediate emergency care.", "explanation": explanation, "probable_conditions": probable, "alerts": alerts}
    
    # Priority 3: Severity Words
    if any(word in text.lower() for word in ["severe", "very bad", "worst pain", "unbearable"]):
        explanation.append("User reports severe symptoms.")
        probable = {s: SYMPTOM_KB.get(s, ["Symptom noted"]) for s in symptoms}
        return {"triage_level": "URGENT", "recommendation": "See urgent care.", "explanation": explanation, "probable_conditions": probable, "alerts": []}
    
    probable = {s: SYMPTOM_KB.get(s, ["Symptom noted"]) for s in symptoms}
    
    # Specific Logic Combinations
    if any(k in ["chest pain","difficulty breathing","bleeding","severe bleeding","loss of consciousness"] for k in symptoms):
        return {"triage_level": "URGENT", "recommendation": "Immediate clinical review.", "probable_conditions": probable, "explanation": explanation, "alerts": []}
    
    if "fever" in symptoms and ("vomiting" in symptoms or "diarrhea" in symptoms):
        return {"triage_level": "URGENT", "recommendation": "Arrange medical review.", "probable_conditions": probable, "explanation": explanation, "alerts": []}
    
    if "chest pain" in symptoms and "dizziness" in symptoms:
        return {"triage_level": "URGENT", "recommendation": "Seek immediate medical attention.", "probable_conditions": probable, "explanation": explanation, "alerts": []}
    
    # Default Non-Urgent
    return {"triage_level": "NON-URGENT", "recommendation": "Self-care and GP review if symptoms persist.", "probable_conditions": probable, "explanation": explanation, "alerts": []}

# -------------------------
# Formatted HTML Replies
# -------------------------
def medication_reply_html(text: str) -> str:
    t = text.lower()
    found = None
    for med in MEDICATIONS.keys():
        if med in t: found = med; break
        med_words = med.split()
        if all(word in t for word in med_words): found = med; break
            
    if not found:
        return "Tell me the medication name (e.g., 'side effects of ibuprofen')."
        
    info = MEDICATIONS[found]
    se_str = ", ".join(info.get("side_effects", []))
    
    # Medical Card HTML
    html = f"<div class='med-card' style='border-left-color: #8e44ad;'>"
    html += f"<span class='med-title'>💊 {found.title()}</span>"
    html += f"<b>Uses:</b> {info['uses']}<br>"
    html += f"<b>Dose:</b> {info['dose_note']}<br>"
    html += f"<b>Side Effects:</b> {se_str}<br>"
    html += f"<b>Caution:</b> {info['cautions']}</div>"
    return html

def pretty_print_triage_html(triage_result):
    lines = []
    symptoms = triage_result.get("probable_conditions", {})
    
    if symptoms:
        lines.append("<strong>Symptoms noted:</strong>")
        for s, conds in symptoms.items():
            lines.append(f"• {s.title()}: {', '.join(conds[:2])}")
    
    level = triage_result.get('triage_level','N/A')
    alert_class = "med-alert" if level in ["EMERGENCY", "URGENT"] else "med-card"
    
    lines.append(f"<div class='{alert_class}'>")
    lines.append(f"<span class='med-title'>TRIAGE: {level}</span>")
    lines.append(f"{triage_result.get('recommendation','')}")
    
    alerts = triage_result.get("alerts", [])
    if alerts:
        lines.append(f"<br><br><strong>⚠️ ALERT:</strong> {', '.join(alerts)}")
    lines.append("</div>")

    # Meds
    suggested_meds = set()
    for s in symptoms.keys():
        if s in SYMPTOM_OTC_SUGGESTIONS:
            for med_key in SYMPTOM_OTC_SUGGESTIONS[s]:
                if med_key in MEDICATIONS:
                    suggested_meds.add(med_key)
    
    if suggested_meds:
        lines.append("<br><strong>💊 Suggested Medications:</strong><br><span style='font-size:0.8em;color:#666'>(Consult a doctor first)</span>")
        for med_key in suggested_meds:
            info = MEDICATIONS[med_key]
            se_str = ", ".join(info.get("side_effects", []))
            lines.append(f"<div class='med-card'>")
            lines.append(f"<span class='med-title'>{med_key.title()}</span>")
            lines.append(f"<b>Uses:</b> {info['uses']}<br>")
            lines.append(f"<b>Dose:</b> {info['dose_note']}<br>")
            lines.append(f"<b>Side Effects:</b> {se_str}")
            lines.append("</div>")

    return "".join(lines)

def canned_reply(intent, text, symptoms, triage_result):
    if intent == "greeting": return random.choice(["Hi! Describe your symptoms or ask advice.", "Hello! How can I help you?"])
    if intent == "thanks": return "You're welcome! Stay safe."
    if intent == "goodbye": return "Goodbye! Stay safe."
    if intent == "med_info": return medication_reply_html(text)
    if intent == "symptom_report": return pretty_print_triage_html(triage_result)
    return "I'm a medical assistant. Please ask about symptoms, medications, or medical advice."

# -------------------------
# Session logging
# -------------------------
_current_session_path = None
_current_user = None

def start_session(username: str):
    global _current_session_path, _current_user
    _current_user = username
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    _current_session_path = SESSIONS_DIR / f"{username}_{ts}.jsonl"
    with _current_session_path.open('a', encoding='utf-8') as f:
        f.write(json.dumps({"event":"session_start","user":username,"time":datetime.now().isoformat()})+"\n")

def log_event(event: str, payload: dict):
    if _current_session_path is None: return
    record = {"event": event, "time": datetime.now().isoformat(), "user": _current_user}
    record.update(payload)
    with _current_session_path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# -------------------------
# User session management
# -------------------------
def get_user_sessions(username):
    return list(SESSIONS_DIR.glob(f"{username}_*.jsonl"))

def get_session_content(session_file):
    content = []
    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try: content.append(json.loads(line))
            except json.JSONDecodeError: continue
    return content

def delete_user_sessions(username):
    deleted = 0
    for session_file in SESSIONS_DIR.glob(f"{username}_*.jsonl"):
        session_file.unlink(); deleted += 1
    return deleted

# -------------------------
# Web Routes
# -------------------------
@app.route('/')
def index():
    if 'username' in session: return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if not username or not password: return render_template('login.html', error="Missing credentials.")
    users = load_users()
    if username in users and users[username] == _hash(password):
        session['username'] = username
        start_session(username)
        return redirect(url_for('chat'))
    else:
        return render_template('login.html', error="Invalid username or password.")

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if save_user(username, password):
        return render_template('login.html', success=f"User {username} registered!")
    else:
        return render_template('login.html', error="Username exists.")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'username' not in session: return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'])

@app.route('/summary')
def summary():
    if 'username' not in session: return redirect(url_for('index'))
    username = session['username']
    sessions = get_user_sessions(username)
    all_history = []
    for session_file in sessions:
        content = get_session_content(session_file)
        for entry in content:
            if entry.get('event') == 'message':
                all_history.append({
                    'timestamp': entry.get('time'),
                    'user_message': entry.get('text'),
                    'bot_response': entry.get('reply')
                })
    return render_template('summary.html', username=username, history=all_history)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    if 'username' not in session: return redirect(url_for('index'))
    delete_user_sessions(session['username'])
    return redirect(url_for('summary'))

@app.route('/admin')
def admin():
    if 'username' not in session or session['username'] != 'admin': return redirect(url_for('index'))
    users = load_users()
    all_sessions = []
    for session_file in SESSIONS_DIR.glob("*.jsonl"):
        content = get_session_content(session_file)
        all_sessions.append({'file': session_file.name, 'username': session_file.stem.split('_')[0], 'content': content})
    debug_logs = []
    if DEBUG_LOG.exists():
        with open(DEBUG_LOG, 'r', encoding='utf-8') as f: debug_logs = f.readlines()
    return render_template('admin.html', users=list(users.keys()), sessions=all_sessions, debug_logs=debug_logs)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session: return jsonify({"error": "Not logged in"}), 401
    user_message = request.json.get('message', '').strip()
    if not user_message: return jsonify({"error": "Empty message"}), 400
    
    # FAQ check
    for q, a in FAQ.items():
        if q in user_message.lower():
            log_event("faq", {"q": q, "a": a})
            return jsonify({"response": a})
    
    lower_user = user_message.lower().strip()
    intent, conf = predict_intent(user_message)
    
    # Overrides
    if any(w in lower_user for w in ["hello","hi","hey"]): intent = "greeting"
    elif any(w in lower_user for w in ["thank","thanks"]): intent = "thanks"
    elif any(w in lower_user for w in ["bye","goodbye"]): intent = "goodbye"
    
    symptoms, fever_temp = extract_symptoms(user_message) if intent=="symptom_report" else ([], None)
    
    if symptoms: 
        intent = "symptom_report" # Force intent if symptoms found
        triage_result = run_triage(symptoms, user_message, fever_temp)
        reply = pretty_print_triage_html(triage_result)
    elif intent == "med_info":
        reply = medication_reply_html(user_message)
    else:
        reply = canned_reply(intent, user_message, symptoms, {})
        
    log_event("message", {"intent": intent, "text": user_message, "reply": reply})
    return jsonify({"response": reply})

# -------------------------
# Main entry (Generates UI Files)
# -------------------------
if __name__ == "__main__":
    train_intent_model()
    
    templates_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    css_dir = static_dir / "css"
    js_dir = static_dir / "js"
    
    for d in [templates_dir, static_dir, css_dir, js_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # 1. Login HTML (Exhibition Style)
    with open(templates_dir / "login.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EMT-Chat Login</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="login-bg">
    <div class="login-container">
        <h1>🏥 EMT-Chat</h1>
        <p style="color:#7f8c8d; margin-bottom:20px;">Medical Triage Assistant</p>
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        {% if success %}<div class="alert alert-success">{{ success }}</div>{% endif %}
        <form action="/login" method="post" id="loginForm">
            <div class="form-group"><input type="text" name="username" placeholder="Username" required></div>
            <div class="form-group"><input type="password" name="password" placeholder="Password" required></div>
            <button type="submit" class="btn btn-primary btn-block">Login</button>
            <button type="button" class="btn btn-link" onclick="toggleReg()">Need an account? Register</button>
        </form>
        <form action="/register" method="post" id="regForm" style="display:none">
            <div class="form-group"><input type="text" name="username" placeholder="Choose Username" required></div>
            <div class="form-group"><input type="password" name="password" placeholder="Choose Password" required></div>
            <button type="submit" class="btn btn-success btn-block">Register</button>
            <button type="button" class="btn btn-link" onclick="toggleReg()">Back to Login</button>
        </form>
    </div>
    <script>function toggleReg(){var l=document.getElementById('loginForm');var r=document.getElementById('regForm');if(l.style.display==='none'){l.style.display='block';r.style.display='none';}else{l.style.display='none';r.style.display='block';}}</script>
</body>
</html>""")

    # 2. Chat HTML (With Chips REMOVED)
    with open(templates_dir / "chat.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EMT-Chat</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="chat-container">
            <div class="chat-header">
                <h2>🏥 EMT-Chat</h2>
                <div class="header-controls">
                    <span>{{ username }}</span>
                    <a href="/summary" class="btn-sm" style="background:#3498db; margin-right:5px;">History</a>
                    <a href="/logout" class="btn-sm">Logout</a>
                </div>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    <div class="message-content">Hello! I'm your Medical Triage Assistant.<br>Tell me your symptoms or ask about medications.</div>
                </div>
            </div>
            <div class="chat-input">
                <form id="message-form">
                    <input type="text" id="message-input" placeholder="Type your symptoms..." autocomplete="off" required>
                    <button type="submit" class="btn btn-send">Send</button>
                </form>
            </div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>""")

    # 3. Style CSS (Exhibition Polish)
    with open(css_dir / "style.css", "w", encoding="utf-8") as f:
        f.write("""body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f0f2f5;margin:0}.container{max-width:900px;margin:20px auto}
/* Login */
.login-bg{background:linear-gradient(135deg,#3498db,#8e44ad);height:100vh;display:flex;align-items:center;justify-content:center}
.login-container{background:white;padding:40px;border-radius:10px;width:100%;max-width:400px;box-shadow:0 10px 25px rgba(0,0,0,0.2);text-align:center}
.btn-block{width:100%;margin-top:10px}.btn-link{background:none;border:none;color:#3498db;cursor:pointer;margin-top:10px;text-decoration:underline}
/* Chat */
.chat-container{background:white;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.1);display:flex;flex-direction:column;height:85vh;overflow:hidden}
.chat-header{background:#2c3e50;color:white;padding:15px 20px;display:flex;justify-content:space-between;align-items:center}
.chat-header h2{margin:0;font-size:1.2rem}.btn-sm{background:#e74c3c;color:white;padding:5px 10px;border-radius:4px;text-decoration:none;font-size:0.9rem}
/* Messages */
.chat-messages{flex:1;overflow-y:auto;padding:20px;background:#f9f9f9}
.message{margin-bottom:20px;display:flex;animation:fadeIn 0.3s ease-out}
.user-message{justify-content:flex-end}.bot-message{justify-content:flex-start}
.message-content{max-width:80%;padding:12px 16px;border-radius:12px;line-height:1.5;font-size:15px}
.user-message .message-content{background:#3498db;color:white;border-bottom-right-radius:2px}
.bot-message .message-content{background:#fff;color:#333;border:1px solid #e0e0e0;border-bottom-left-radius:2px;box-shadow:0 1px 2px rgba(0,0,0,0.05)}
/* Input */
.chat-input{padding:20px;border-top:1px solid #eee;background:white}
#message-form{display:flex;gap:10px}
#message-input{flex:1;padding:12px;border:1px solid #ddd;border-radius:25px;outline:none;padding-left:20px}
.btn-send{background:#27ae60;color:white;border:none;padding:0 25px;border-radius:25px;cursor:pointer;font-weight:bold}
.btn-send:hover{background:#219150}
/* Utils */
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.typing-indicator{display:none;padding:10px;margin-bottom:10px;margin-left:10px}
.typing-dot{height:8px;width:8px;margin:0 2px;background-color:#bdc3c7;border-radius:50%;display:inline-block;animation:typing 1.4s infinite ease-in-out both}
.typing-dot:nth-child(1){animation-delay:-0.32s}.typing-dot:nth-child(2){animation-delay:-0.16s}
@keyframes typing{0%,80%,100%{transform:scale(0)}40%{transform:scale(1)}}
.med-card,.med-alert{background:#fff;border-left:5px solid #3498db;padding:12px;margin-top:10px;border-radius:4px;box-shadow:0 2px 5px rgba(0,0,0,0.05);font-size:0.95rem}
.med-alert{border-left-color:#e74c3c;background-color:#fff5f5}
.med-title{font-weight:bold;display:block;margin-bottom:5px;color:#2c3e50;text-transform:uppercase;font-size:0.85rem;letter-spacing:0.5px}
.form-group input{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;margin-bottom:15px}
.btn-primary{background:#3498db;border:none;padding:10px;color:white;border-radius:4px;cursor:pointer}
.btn-success{background:#2ecc71;border:none;padding:10px;color:white;border-radius:4px;cursor:pointer}
.alert{padding:10px;border-radius:4px;margin-bottom:10px;font-size:0.9rem}
.alert-danger{background:#f8d7da;color:#721c24}.alert-success{background:#d4edda;color:#155724}
/* Summary */
.summary-container{max-width:1000px;margin:30px auto;background:#fff;border-radius:10px;box-shadow:0 5px 15px rgba(0,0,0,0.1);padding:20px}
.history-table table{width:100%;border-collapse:collapse;margin-top:20px}
.history-table th,.history-table td{padding:12px;text-align:left;border-bottom:1px solid #ddd}
.history-table th{background:#f8f9fa}
""")

    # 4. Script JS (With Typing Animation)
    with open(js_dir / "script.js", "w", encoding="utf-8") as f:
        f.write("""document.addEventListener('DOMContentLoaded',function(){const form=document.getElementById('message-form');const input=document.getElementById('message-input');const chat=document.getElementById('chat-messages');
const typingDiv=document.createElement('div');typingDiv.className='typing-indicator';typingDiv.innerHTML='<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';chat.appendChild(typingDiv);
form.addEventListener('submit',function(e){e.preventDefault();const msg=input.value.trim();if(!msg)return;
addMessage(msg,'user');input.value='';typingDiv.style.display='block';chat.appendChild(typingDiv);chat.scrollTop=chat.scrollHeight;
fetch('/send_message',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})})
.then(r=>r.json()).then(d=>{setTimeout(()=>{typingDiv.style.display='none';addMessage(d.response||d.error,'bot');},400);})
.catch(e=>{typingDiv.style.display='none';addMessage("Error connecting to server.",'bot');});});
function addMessage(h,s){const r=document.createElement('div');r.className=`message ${s}-message`;const b=document.createElement('div');b.className='message-content';if(s==='user'){b.textContent=h;}else{b.innerHTML=h;}r.appendChild(b);chat.insertBefore(r,typingDiv);chat.scrollTop=chat.scrollHeight;}});""")

    # 5. Summary & Admin Templates
    with open(templates_dir / "summary.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Summary</title><link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}"></head><body>
<div class="container"><div class="summary-container"><div class="chat-header"><h2>History: {{ username }}</h2><a href="/chat" class="btn-sm">Back</a></div>
<form action="/delete_history" method="post" style="margin-top:20px"><button class="btn-sm" style="background:#e74c3c;border:none;cursor:pointer">Clear History</button></form>
<div class="history-table"><table><thead><tr><th>Time</th><th>User</th><th>Bot</th></tr></thead><tbody>
{% for e in history %}<tr><td>{{ e.timestamp }}</td><td>{{ e.user_message }}</td><td>{{ e.bot_response|striptags }}</td></tr>{% endfor %}
</tbody></table></div></div></div></body></html>""")
        
    with open(templates_dir / "admin.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html><html><head><title>Admin</title><link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}"></head><body>
<div class="container"><div class="summary-container"><h2>Admin Dashboard</h2><a href="/chat" class="btn-sm">Back</a>
<h3>Users</h3><ul>{% for u in users %}<li>{{ u }}</li>{% endfor %}</ul>
<h3>Debug Logs</h3><pre style="background:#eee;padding:10px;height:300px;overflow:auto">{% for l in debug_logs %}{{ l }}{% endfor %}</pre>
</div></div></body></html>""")

    # Create admin user if not exists
    users = load_users()
    if 'admin' not in users:
        with open(USERS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"admin:{_hash('admin123')}\n")
        debug_log("Created default admin user")
    
    print("Code loaded. Assets generated. Starting server...")
    app.run(debug=True, host='127.0.0.1', port=5000)