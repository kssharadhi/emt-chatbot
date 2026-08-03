# EMT-Chat: Medical Triage Assistant

EMT-Chat is an offline-capable, rule-and-classifier-assisted Medical Triage Chatbot built with Node.js, Express, and TypeScript. It provides rapid symptom evaluation, red-flag emergency detection, medication reference, and user session management.

---

## ⚡ Offline Capability

**Yes! EMT-Chat runs 100% offline.**

- **No Third-Party AI API Dependencies**: EMT-Chat uses a self-contained TF-IDF vector classifier and keyword matching engine embedded directly into the application codebase.
- **Local Data Storage**: User credentials and JSONL conversation sessions are stored locally in the `./data` directory.
- **Embedded Medical Knowledge Base**: Built-in symptom mappings, red-flag criteria, medication information, and FAQs are embedded locally in TypeScript modules.

---

## 🚀 Key Features

1. **Symptom Triage & Red-Flag Escalation**:
   - Classifies symptoms into **EMERGENCY**, **URGENT**, and **NON-URGENT** risk levels.
   - Automatically flags red-flag emergencies (e.g., severe chest pain, high fever, stroke-like symptoms, difficulty breathing) and recommends immediate care.
2. **Medication & OTC Info Lookup**:
   - Provides uses, dosage guidance, side effects, and precautions for common medications (Paracetamol, Ibuprofen, Cetirizine, Omeprazole, Metformin, Atorvastatin, Lisinopril, Sertraline, Albuterol, Prednisone, Amoxicillin, and more).
3. **Intent Classification & FAQ Matching**:
   - Uses an in-memory TF-IDF + Cosine Similarity classifier to detect user intents (greetings, symptom reports, medication queries, general questions).
4. **Session History & Admin Dashboard**:
   - Tracks chat sessions per user in local `.jsonl` files.
   - Offers user summary views and clear history features.
   - Includes an Admin Dashboard (`/admin`) for inspecting user accounts and server debug logs.

---

## 🔑 Default Credentials

- **Admin Account**:
  - **Username**: `admin`
  - **Password**: `admin123`
- **New Users**: Anyone can register a new account directly on the login page.

---

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v18+)
- npm

### 1. Install Dependencies
```bash
npm install
```

### 2. Development Mode
Run the development server with live reload:
```bash
npm run dev
```
Open `http://localhost:3000` in your web browser.

### 3. Build & Production Start
Build the bundled production JavaScript file:
```bash
npm run build
```
Start the production server:
```bash
npm start
```

---

## 📁 Project Structure

```
├── data/                    # Local database & user session logs
│   ├── users.txt            # Local user accounts (SHA-256 hashed passwords)
│   └── sessions/            # Per-user chat session logs (.jsonl)
├── public/                  # Static assets (CSS styles & client JS)
├── src/
│   ├── index.ts             # Express web server & API routes
│   ├── kb.ts                # Medical knowledge base & symptom/medication data
│   ├── classifier.ts        # In-memory TF-IDF intent classifier
│   └── triage.ts            # Triage algorithm & red-flag detection rules
├── views/                   # EJS UI templates (login, chat, summary, admin)
├── package.json
└── tsconfig.json
```

---

## ⚠️ Medical Disclaimer

*EMT-Chat is an educational and reference tool and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a physician or qualified healthcare provider with any medical questions or emergencies.*
