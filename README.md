# Digital Diagnosis v2

Digital Diagnosis v2 is an AI-powered medical diagnosis assistant. It processes free-text input of patient symptoms, extracts the key symptoms using a Large Language Model (LLM), and passes them through a Machine Learning Classifier (LightGBM) to generate a top-3 diseases prediction along with medical advice and recommendations. 

## Features
- **Intelligent Symptom Parsing**: Uses a state-of-the-art LLM to correctly extract medical symptoms from raw sentences and handles negations.
- **Fast & Accurate Classification**: Utilizes a highly-optimized LightGBM model trained on a comprehensive symptom-disease dataset to predict up to 41 unique diseases.
- **Natural Language Summaries**: Re-packages the prediction outputs, condition severity, immediate advice, and specialist recommendations into an easy-to-understand, empathetic summary for the user.

## Architecture Pipeline
1. **User Input** (Free Text + Profile Metadata)
2. **LLM Call #1** → Translates text to a standardized symptom list
3. **Binary Vector** → Encodes symptoms to a format acceptable by the ML model
4. **LightGBM Model** → Selects top 3 disease predictions
5. **Knowledge Base Lookup** → Fetches detailed medical knowledge for predicted diseases
6. **LLM Call #2** → Compiles everything into a patient-friendly summary

## Requirements & Setup
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
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY="your_groq_api_key_here"
   LLM_MODEL_NAME="llama-3.3-70b-versatile"
   # ... include other variables like LANGCHAIN setups if you use LangSmith
   ```

## Running the Application
### Backend (FastAPI)
```bash
conda activate DDenv
uvicorn backend.main:app --reload --port 8000
```

### Frontend (Streamlit)
```bash
conda activate DDenv
cd frontend
streamlit run app.py
```

## Structure
- `backend/`: Core service components, AI clients, models, and FastAPI app.
- `frontend/`: Streamlit frontend application.
- `data/`: Datasets, parsed symptom lists, and processed data.
- `models/`: Trained model binaries (LightGBM and LabelEncoder).
- `evaluation/` & `tests/`: Scripts to evaluate model behavior and unit testing.

*Disclaimer: This is an AI-generated analysis and NOT a substitute for professional medical diagnosis.*
