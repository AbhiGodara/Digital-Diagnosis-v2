# HealthPilot 🩺

[![Frontend Deployment](https://img.shields.io/badge/Frontend-Vercel-brightgreen?style=for-the-badge&logo=vercel)](https://healthpilot-mocha.vercel.app/)
[![Backend Deployment](https://img.shields.io/badge/Backend-Render-blue?style=for-the-badge&logo=render)](https://healthpilot-mocha.vercel.app/)

HealthPilot is an AI-powered medical diagnosis assistant. It processes free-text input of patient symptoms, extracts the key symptoms using a Large Language Model (LLM), and passes them through a Machine Learning Classifier (LightGBM) to generate a top-3 diseases prediction along with medical advice and recommendations. 

**🚀 Live Application**: [https://healthpilot-mocha.vercel.app/](https://healthpilot-mocha.vercel.app/)

---

## 🌟 Features
- **Intelligent Symptom Parsing**: Uses a state-of-the-art LLM (Llama-3.3-70b via Groq) to correctly extract medical symptoms from raw sentences and handles negations.
- **Fast & Accurate Classification**: Utilizes a highly-optimized LightGBM model trained on a comprehensive symptom-disease dataset to predict up to 41 unique diseases.
- **Natural Language Summaries**: Re-packages the prediction outputs, condition severity, immediate advice, and specialist recommendations into an easy-to-understand, empathetic summary for the user.
- **AI Doctor Chatbot**: An integrated Langchain conversational agent to support interactive symptom tracking, conversational queries, and medical guidance.
- **Medical Report Downloads**: Generate and print/download a fully structured, clinical-grade medical report containing your diagnosis summary and risk alerts.

---

## 📐 Architecture Pipeline
1. **User Input** (Free Text via React UI Dashboard or Chatbot)
2. **Django API Endpoint** → Receives the POST payload.
3. **LLM Call #1** → Translates text to a standardized symptom list.
4. **Binary Vector** → Encodes symptoms to a format acceptable by the ML model.
5. **LightGBM Model** → Selects top 3 disease predictions.
6. **Knowledge Base Lookup** → Fetches detailed medical knowledge for predicted diseases.
7. **LLM Call #2** → Compiles everything into a patient-friendly summary or chatbot reply.

---

## 🛠️ Requirements & Setup
1. **Python Environment**: Ensure you are running Python 3.10+
2. **Create / Activate conda environment**
   ```bash
   conda create -n DDenv python=3.11
   conda activate DDenv
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**
   Create a `.env` file in the root directory (see `.env.example` for details):
   ```env
   GROQ_API_KEY="your_groq_api_key_here"
   LLM_MODEL_NAME="llama-3.3-70b-versatile"
   ```

---

## 💻 Running the Application Locally
### Backend (Django)
```bash
conda activate DDenv
cd django_backend
python manage.py runserver 8000
```

### Frontend (React + Vite)
Open a new terminal:
```bash
cd react_frontend
npm install
npm run dev
```

---

## 🌐 Production Deployment
HealthPilot is designed to be fully modular and is easily deployable to cloud services:

* **Frontend (React)**: Deployed on [Vercel](https://vercel.com) using Vite presets.
  * Live URL: [https://healthpilot-mocha.vercel.app/](https://healthpilot-mocha.vercel.app/)
  * Connection string: Configured via the `VITE_API_BASE` environment variable.
* **Backend (Django)**: Deployed on [Render](https://render.com) using a `gunicorn` WSGI production server wrapper.
  * Configured with persistent environment variables for the Groq LLM API client.

---

## 📂 Project Structure
- `django_backend/`: Django backend project containing the API endpoints.
- `backend/`: Core service components, AI clients, models.
- `react_frontend/`: React + Vite frontend application.
- `chatbot/`: Langchain conversational agent.
- `data/`: Datasets, parsed symptom lists, and processed data.
- `models/`: Trained model binaries (LightGBM and LabelEncoder).
- `evaluation/` & `tests/`: Scripts to evaluate model behavior and unit testing.
- `archive/`: Legacy code (old FastAPI implementations).

*Disclaimer: This is an AI-generated analysis and NOT a substitute for professional medical diagnosis.*
