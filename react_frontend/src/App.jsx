import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const API_BASE = "http://localhost:8000/api";

function App() {
  const [patientAge, setPatientAge] = useState('');
  const [patientGender, setPatientGender] = useState('');
  const [symptomDuration, setSymptomDuration] = useState('');
  const [symptomsText, setSymptomsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Chatbot State
  const [chatOpen, setChatOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: "Hello! I am your AI Medical Assistant. 👋 Describe your symptoms and I'll help you understand what might be going on." }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const sessionId = useRef("session_" + Math.random().toString(36).substring(7)).current;

  const handleAnalyze = async () => {
    if (!symptomsText || symptomsText.length < 10) {
      setError("Please describe your symptoms in more detail (at least 10 characters).");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/diagnose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms_text: symptomsText,
          patient_age: patientAge ? parseInt(patientAge) : 30,
          patient_gender: patientGender || 'unknown',
          symptom_duration: symptomDuration || 'unknown'
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || "An error occurred");
      }
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatHistory(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: userMessage.content })
      });
      const data = await response.json();
      if (response.ok && data.reply) {
        setChatHistory(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        setChatHistory(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an issue." }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: "Network error occurred." }]);
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    if (chatOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory, chatOpen]);

  const quickSymptoms = ["Fever", "Headache", "Cough", "Nausea", "Fatigue", "Dizziness", "Chest Pain", "Shortness of Breath"];

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <h1>⚕️ Digital Diagnosis AI</h1>
          <p>Advanced AI-powered symptom analysis & prediction</p>
        </div>
      </header>

      <main className="main-content">
        <div className="card form-card">
          <h2>Patient Details</h2>
          <div className="form-row">
            <div className="input-group">
              <label>Age</label>
              <input type="number" value={patientAge} onChange={e => setPatientAge(e.target.value)} placeholder="e.g. 35" />
            </div>
            <div className="input-group">
              <label>Gender</label>
              <select value={patientGender} onChange={e => setPatientGender(e.target.value)}>
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="input-group">
              <label>Duration</label>
              <select value={symptomDuration} onChange={e => setSymptomDuration(e.target.value)}>
                <option value="">Select...</option>
                <option value="few_hours">Few hours</option>
                <option value="1_day">1 day</option>
                <option value="2_3_days">2-3 days</option>
                <option value="1_week">1 week</option>
                <option value="more">More than 1 week</option>
              </select>
            </div>
          </div>

          <h2>Symptoms</h2>
          <textarea
            className="symptoms-input"
            rows={5}
            value={symptomsText}
            onChange={e => setSymptomsText(e.target.value)}
            placeholder="Describe your symptoms in detail (e.g. I have had a high fever for 2 days, bad headache, keep coughing...)"
          />
          <div className="quick-tags">
            {quickSymptoms.map(sym => (
              <button 
                key={sym} 
                className="tag-btn" 
                onClick={() => setSymptomsText(prev => prev + (prev ? ', ' : '') + sym.toLowerCase())}
              >
                + {sym}
              </button>
            ))}
          </div>

          {error && <div className="error-box">{error}</div>}

          <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Symptoms"}
          </button>
        </div>

        {results && (
          <div className="card results-card fade-in">
            <h2>AI Diagnosis Results</h2>
            <div className="summary-box">
              <h3>🤖 AI Summary</h3>
              <p>{results.summary}</p>
            </div>

            <h3>Top Predictions</h3>
            <div className="predictions-list">
              {results.predictions.map((pred, i) => (
                <div key={i} className="prediction-item">
                  <div className="prediction-header">
                    <h4>#{i + 1} {pred.disease.toUpperCase()}</h4>
                    <span className="prob-badge">{pred.probability}%</span>
                  </div>
                  <div className="prediction-info">
                    <p><strong>Severity:</strong> <span className={`sev-${pred.info.severity_level}`}>{pred.info.severity_level}</span></p>
                    <p><strong>Specialist:</strong> {pred.info.specialist_recommendation}</p>
                    <p><strong>Immediate Advice:</strong> {pred.info.immediate_advice?.join(', ')}</p>
                    <p><strong>When to seek help:</strong> {pred.info.when_to_seek_help}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="disclaimer">
              ⚠️ Medical Disclaimer: This AI tool is for educational purposes only. Not professional medical advice.
            </div>
          </div>
        )}
      </main>

      <button className="chatbot-fab" onClick={() => setChatOpen(!chatOpen)}>
        💬 AI Doctor
      </button>

      {chatOpen && (
        <div className="chatbot-widget fade-in">
          <div className="chatbot-header">
            <h4>AI Medical Assistant</h4>
            <button className="close-btn" onClick={() => setChatOpen(false)}>×</button>
          </div>
          <div className="chatbot-messages">
            {chatHistory.map((msg, i) => (
              <div key={i} className={`msg ${msg.role}`}>
                <div className="msg-bubble">{msg.content}</div>
              </div>
            ))}
            {chatLoading && <div className="msg assistant"><div className="msg-bubble typing">...</div></div>}
            <div ref={messagesEndRef} />
          </div>
          <div className="chatbot-input">
            <input 
              type="text" 
              value={chatInput} 
              onChange={e => setChatInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSendChat()}
              placeholder="Type your message..."
            />
            <button onClick={handleSendChat}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
