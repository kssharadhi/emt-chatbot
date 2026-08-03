// Medical Chatbot Knowledge Base & Training Data

export interface MedInfo {
  uses: string;
  dose_note: string;
  side_effects: string[];
  cautions: string;
}

export const TRAINING: Array<[string, string]> = [
  // Greetings
  ["hello", "greeting"], ["hi", "greeting"], ["hey", "greeting"],
  ["good morning", "greeting"], ["good evening", "greeting"], ["hey there", "greeting"],
  ["hi there", "greeting"], ["yo", "greeting"], ["greetings", "greeting"],
  ["how are you", "greeting"], ["what's up", "greeting"], ["nice to meet you", "greeting"],
  
  // Thanks
  ["thanks", "thanks"], ["thank you", "thanks"], ["thx", "thanks"], ["appreciate it", "thanks"],
  ["thank you very much", "thanks"], ["thanks a lot", "thanks"], ["i appreciate your help", "thanks"],
  ["much appreciated", "thanks"], ["you're a lifesaver", "thanks"], ["thank you for your assistance", "thanks"],
  
  // Goodbye
  ["bye", "goodbye"], ["goodbye", "goodbye"], ["see you", "goodbye"], ["talk later", "goodbye"],
  ["see ya", "goodbye"], ["later", "goodbye"], ["catch you later", "goodbye"],
  ["i have to go now", "goodbye"], ["farewell", "goodbye"], ["take care", "goodbye"],
  
  // Symptom reports - Single symptoms
  ["i have a headache", "symptom_report"], ["my head hurts", "symptom_report"],
  ["i am feeling dizzy", "symptom_report"], ["i have chest pain", "symptom_report"],
  ["i feel short of breath", "symptom_report"], ["i am coughing a lot", "symptom_report"],
  ["i have a sore throat", "symptom_report"], ["i am vomiting", "symptom_report"],
  ["i have diarrhea", "symptom_report"], ["i cut my leg", "symptom_report"],
  ["my arm is swollen", "symptom_report"], ["i have a fever", "symptom_report"],
  ["i feel faint", "symptom_report"], ["i am bleeding a lot", "symptom_report"],
  ["my back hurts", "symptom_report"], ["pain in my stomach", "symptom_report"],
  ["i twisted my ankle", "symptom_report"], ["my tooth hurts", "symptom_report"],
  ["i have a rash", "symptom_report"], ["i feel nauseous", "symptom_report"],
  ["i have muscle cramps", "symptom_report"], ["my muscles are cramping", "symptom_report"],
  ["i have eye strain", "symptom_report"], ["my eyes feel tired", "symptom_report"],
  ["i have heartburn", "symptom_report"], ["i feel burning in my chest", "symptom_report"],
  ["i have constipation", "symptom_report"], ["i can't have a bowel movement", "symptom_report"],
  ["i have insomnia", "symptom_report"], ["i can't sleep at night", "symptom_report"],
  ["i have allergies", "symptom_report"], ["i am having an allergic reaction", "symptom_report"],
  ["i have sinus pressure", "symptom_report"], ["my sinuses feel full", "symptom_report"],
  ["i have anxiety", "symptom_report"], ["i feel anxious all the time", "symptom_report"],
  ["i have fatigue", "symptom_report"], ["i feel exhausted all the time", "symptom_report"],
  ["i have joint pain", "symptom_report"], ["my joints are aching", "symptom_report"],
  ["i have ear pain", "symptom_report"], ["my ear is hurting", "symptom_report"],
  ["i have a runny nose", "symptom_report"], ["my nose keeps running", "symptom_report"],
  ["i have congestion", "symptom_report"], ["my chest feels congested", "symptom_report"],
  
  // Mixed symptoms
  ["i have fever and cough", "symptom_report"], ["headache and nausea", "symptom_report"],
  ["chest pain with dizziness", "symptom_report"], ["vomiting and diarrhea", "symptom_report"],
  ["sore throat with fever", "symptom_report"], ["back pain and leg pain", "symptom_report"],
  ["rash and itching", "symptom_report"], ["abdominal pain with vomiting", "symptom_report"],
  ["cold with body ache", "symptom_report"], ["fever and chills", "symptom_report"],
  ["cough and congestion", "symptom_report"], ["headache with light sensitivity", "symptom_report"],
  ["fatigue and muscle pain", "symptom_report"], ["joint pain and swelling", "symptom_report"],
  ["ear pain and hearing loss", "symptom_report"], ["runny nose and sneezing", "symptom_report"],
  ["sinus pressure and headache", "symptom_report"], ["anxiety and palpitations", "symptom_report"],
  ["insomnia and fatigue", "symptom_report"], ["eye strain and headache", "symptom_report"],
  ["allergies and sneezing", "symptom_report"], ["constipation and abdominal pain", "symptom_report"],
  ["muscle cramps and weakness", "symptom_report"], ["heartburn and regurgitation", "symptom_report"],
  
  // Ask advice / escalation
  ["should I see a doctor?", "ask_escalation"],
  ["do I need to go to the hospital?", "ask_escalation"],
  ["is this an emergency?", "ask_escalation"],
  ["what should I do for my fever?", "ask_advice"],
  ["how to treat headache?", "ask_advice"],
  ["do I need urgent care?", "ask_escalation"],
  ["should I call 911?", "ask_escalation"],
  ["is my condition serious?", "ask_escalation"],
  ["help me with my symptoms", "ask_advice"],
  ["what can I take for this pain", "ask_advice"],
  ["what helps muscle cramps", "ask_advice"], ["how to prevent eye strain", "ask_advice"],
  ["what helps heartburn", "ask_advice"], ["how to relieve constipation", "ask_advice"],
  ["what to do for insomnia", "ask_advice"], ["how to manage allergies", "ask_advice"],
  ["what helps sinus pressure", "ask_advice"], ["how to reduce anxiety", "ask_advice"],
  ["what should I do for fatigue", "ask_advice"], ["how to treat joint pain", "ask_advice"],
  ["what helps ear pain", "ask_advice"], ["how to stop a runny nose", "ask_advice"],
  ["what should I do for congestion", "ask_advice"], ["how to treat a cold", "ask_advice"],
  ["what helps with chills", "ask_advice"], ["how to relieve nausea", "ask_advice"],
  ["what should I do for body aches", "ask_advice"], ["how to reduce swelling", "ask_advice"],
  ["what helps with itching", "ask_advice"], ["how to treat abdominal pain", "ask_advice"],
  ["what should I do for vomiting", "ask_advice"], ["how to relieve back pain", "ask_advice"],
  ["what helps with light sensitivity", "ask_advice"], ["how to treat muscle pain", "ask_advice"],
  ["what should I do for palpitations", "ask_advice"], ["how to relieve hearing loss", "ask_advice"],
  ["what helps with sneezing", "ask_advice"], ["how to treat sinus pressure", "ask_advice"],
  ["what helps with insomnia", "ask_advice"], ["how to relieve eye strain", "ask_advice"],
  ["what should I do for headache", "ask_advice"], ["how to treat fever", "ask_advice"],
  ["what helps with cough", "ask_advice"], ["how to relieve congestion", "ask_advice"],
  ["is this a medical emergency", "ask_escalation"], ["should I go to the ER", "ask_escalation"],
  ["do I need an ambulance", "ask_escalation"], ["is this life threatening", "ask_escalation"],
  ["should I be worried", "ask_escalation"], ["is this serious", "ask_escalation"],
  ["do I need immediate help", "ask_escalation"], ["should I call a doctor now", "ask_escalation"],
  ["is this an emergency situation", "ask_escalation"], ["do I need to go to urgent care", "ask_escalation"],
  
  // Medication info
  ["i took paracetamol", "took_med"], ["i took ibuprofen", "took_med"],
  ["i took medicine for fever", "took_med"], ["what are side effects of ibuprofen", "med_info"],
  ["side effects of paracetamol", "med_info"], ["can i take cetirizine", "med_info"],
  ["is aspirin safe for me", "med_info"], ["what does metformin do", "med_info"],
  ["what is omeprazole used for", "med_info"], ["side effects of atorvastatin", "med_info"],
  ["can i take lisinopril", "med_info"], ["what is sertraline for", "med_info"],
  ["how does albuterol work", "med_info"], ["side effects of prednisone", "med_info"],
  ["can i take aspirin with ibuprofen", "med_info"], ["what is the dosage for metformin", "med_info"],
  ["is omeprazole safe long term", "med_info"], ["can i drink alcohol with atorvastatin", "med_info"],
  ["what are the side effects of lisinopril", "med_info"], ["how long does sertraline take to work", "med_info"],
  ["can i use albuterol every day", "med_info"], ["how should i take prednisone", "med_info"],
  ["tell me about amoxicillin", "med_info"], ["what are the side effects of amoxicillin", "med_info"],
  ["is amoxicillin an antibiotic", "med_info"], ["how does amoxicillin work", "med_info"],
  
  // Non-medical queries
  ["what is the weather today", "non_medical"], ["tell me a joke", "non_medical"],
  ["who won the game", "non_medical"], ["what's your favorite movie", "non_medical"],
  ["how old are you", "non_medical"], ["do you have pets", "non_medical"],
  ["where do you live", "non_medical"], ["what's your favorite color", "non_medical"],
  ["can you sing", "non_medical"], ["do you love me", "non_medical"],
  ["what's the capital of France", "non_medical"], ["tell me about politics", "non_medical"],
  ["what's the latest news", "non_medical"], ["who is the president", "non_medical"],
  ["what's the stock market doing", "non_medical"], ["what's your favorite food", "non_medical"],
  ["do you believe in god", "non_medical"], ["what's your favorite song", "non_medical"],
  ["can you dance", "non_medical"], ["do you have a girlfriend", "non_medical"],
  ["what's your favorite book", "non_medical"], ["what's your favorite sport", "non_medical"],
  ["do you like animals", "non_medical"], ["what's your favorite TV show", "non_medical"],
  
  // General knowledge
  ["what is a chatbot", "general_knowledge"],
  ["what is artificial intelligence", "general_knowledge"],
  ["how do chatbots work", "general_knowledge"],
  ["what is hypertension", "general_knowledge"],
  ["what is diabetes", "general_knowledge"],
  ["what is asthma", "general_knowledge"],
  ["what is a migraine", "general_knowledge"],
  ["what is cholesterol", "general_knowledge"],
  ["what is blood pressure", "general_knowledge"],
  ["what is the immune system", "general_knowledge"],
  ["what is inflammation", "general_knowledge"],
  ["what is a virus", "general_knowledge"],
  ["what is bacteria", "general_knowledge"],
  ["what is an infection", "general_knowledge"],
  ["what is a vaccine", "general_knowledge"],
  ["what is a tumor", "general_knowledge"],
  ["what is cancer", "general_knowledge"],
  ["what is chemotherapy", "general_knowledge"],
  ["what is radiation therapy", "general_knowledge"],
  ["what is physical therapy", "general_knowledge"],
  ["what is occupational therapy", "general_knowledge"]
];

export const SYMPTOM_KB: Record<string, string[]> = {
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
  "weakness": ["Fatigue", "Electrolyte imbalance", "Neurological condition"]
};

export const SYMPTOM_SYNONYMS: Record<string, string[]> = {
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
  "weakness": ["lethargy", "lack of strength", "powerlessness"]
};

export const FAQ: Record<string, string> = {
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
  "what is occupational therapy": "Occupational therapy helps people participate in the activities they want and need to do through the therapeutic use of everyday activities."
};

export const MEDICATIONS: Record<string, MedInfo> = {
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
  }
};

export const SYMPTOM_OTC_SUGGESTIONS: Record<string, string[]> = {
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
};

export const REDFLAGS: Array<[RegExp, string]> = [
  [/\b(chest pain|pressure in chest)\b/i, "Chest pain / pressure"],
  [/\b(difficulty breathing|shortness of breath|cant breathe|can't breathe)\b/i, "Difficulty breathing / respiratory distress"],
  [/\b(bleeding a lot|severe bleeding|blood everywhere)\b/i, "Severe external bleeding"],
  [/\b(unconscious|fainting|lost consciousness|not responding)\b/i, "Loss of consciousness"],
  [/\b(weak on one side|slurred speech|facial droop)\b/i, "Stroke-like symptoms"],
  [/\b(suicidal|want to die|kill myself)\b/i, "Self-harm / suicidal ideation"],
  [/\b(severe headache|worst headache)\b/i, "Severe headache"],
  [/\b(allergic reaction|anaphylaxis)\b/i, "Severe allergic reaction"],
  [/\b(confusion|disoriented)\b/i, "Confusion / disorientation"],
  [/\b(high fever|very high temperature)\b/i, "High fever"],
  [/\bfever (of |over |above )?10[0-9]\b/i, "High fever (100°F or above)"],
  [/\btemperature (of |over |above )?10[0-9]\b/i, "High temperature (100°F or above)"]
];
