import React, { useState, useRef, useEffect } from 'react';
import './index.css';

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

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
    { role: 'assistant', content: "Hello! 👋 I'm your AI Medical Assistant. Describe your symptoms in natural language and I'll help you understand what might be going on. Remember — I'm here to assist, not replace a real doctor." }
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

  const handleClear = () => {
    setPatientAge('');
    setPatientGender('');
    setSymptomDuration('');
    setSymptomsText('');
    setResults(null);
    setError(null);
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;

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
        setChatHistory(prev => [...prev, { role: 'assistant', content: "⚠️ Sorry, I couldn't reach the server. Please check your connection or try again." }]);
      }
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: "⚠️ Sorry, I couldn't reach the server. Please check your connection or try again." }]);
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    if (chatOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatHistory, chatOpen]);

  const downloadReport = () => {
    const resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;
    
    const clonedResults = resultsSection.cloneNode(true);
    
    const disclaimer = clonedResults.querySelector('.disclaimer-alert');
    if (disclaimer) disclaimer.remove();
    
    const actionButtons = clonedResults.querySelector('.results-actions');
    if (actionButtons) actionButtons.remove();
    
    const printWindow = window.open('', '_blank');
    const currentDate = new Date().toLocaleString();
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
            <head>
                <title>Medical Diagnosis Report</title>
                <style>
                    body { 
                        font-family: 'Arial', sans-serif; 
                        margin: 20px; 
                        color: #333; 
                        line-height: 1.6;
                    }
                    .header { 
                        text-align: center; 
                        margin-bottom: 30px; 
                        padding-bottom: 20px; 
                        border-bottom: 3px solid #2563eb; 
                    }
                    .header h1 { 
                        color: #2563eb; 
                        margin-bottom: 5px; 
                    }
                    .result-card { 
                        margin: 20px 0; 
                        padding: 20px; 
                        border: 2px solid #e5e7eb; 
                        border-radius: 12px; 
                        page-break-inside: avoid;
                    }
                    .probability-value { 
                        font-size: 32px; 
                        font-weight: bold; 
                        color: #2563eb; 
                    }
                    .section-title {
                        color: #374151;
                        font-weight: bold;
                        margin: 15px 0 8px 0;
                        font-size: 16px;
                    }
                    ul { margin: 10px 0; padding-left: 25px; }
                    li { margin: 5px 0; }
                    .high-risk-warning {
                        background: #fee2e2;
                        border: 2px solid #ef4444;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 15px 0;
                    }
                    .processing-summary {
                        background: #f9fafb;
                        padding: 20px;
                        border-radius: 12px;
                        margin: 20px 0;
                    }
                    .summary-grid-centered {
                        display: flex;
                        gap: 20px;
                        justify-content: center;
                        flex-wrap: wrap;
                    }
                    .summary-item {
                        background: white;
                        padding: 15px;
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        flex: 1;
                        min-width: 250px;
                    }
                    @media print { 
                        body { margin: 0; }
                        .no-print { display: none; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🧠 HealthPilot Report</h1>
                    <p><strong>Generated:</strong> ${currentDate}</p>
                </div>
                
                ${clonedResults.innerHTML.replace(/class="hidden"/g, '').replace(/hidden/g, '')}
                
                <div style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #d1d5db; padding-top: 20px;">
                    <p><strong>This report was generated by:</strong></p>
                    <p>HealthPilot v1.0</p>
                    <p>Trained on 254 diseases with 86% accuracy</p>
                    <p><em>For questions or concerns, consult with your healthcare provider</em></p>
                </div>
            </body>
        </html>
    `);
    
    printWindow.document.close();
    
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 1000);
  };

  const quickSymptoms = ["Fever", "Headache", "Cough", "Nausea", "Fatigue", "Dizziness", "Chest pain", "Shortness of breath", "Muscle aches", "Sore throat", "Runny nose", "Vomiting", "Diarrhea", "Stomach cramps", "Back pain"];

  const getSeverityClass = (severity) => {
      const severityMap = {
          'mild': 'severity-mild',
          'moderate': 'severity-moderate',
          'serious': 'severity-serious',
          'critical': 'severity-critical'
      };
      return severityMap[severity?.toLowerCase()] || 'severity-moderate';
  };
  
  const getSimpleDescription = (diseaseName) => {
      const descriptions = {
          'diabetes': 'A metabolic disorder with high blood sugar levels',
          'hypertension': 'High blood pressure condition',
          'asthma': 'Respiratory condition affecting airways',
          'anxiety': 'Mental health condition with excessive worry',
          'migraine': 'Severe headache disorder',
          'pneumonia': 'Lung infection causing breathing difficulties'
      };
      const lowerName = diseaseName?.toLowerCase() || '';
      for (const [key, description] of Object.entries(descriptions)) {
          if (lowerName.includes(key)) {
              return description;
          }
      }
      return 'Medical condition requiring professional evaluation';
  };

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <div className="logo-icon">
                <i className="fas fa-brain"></i>
              </div>
              <div className="logo-text">
                <h1>HealthPilot</h1>
                <p>Advanced AI-powered symptom analysis</p>
              </div>
            </div>
            <div className="header-stats">
              <div className="stat-card">
                <div className="stat-number">50</div>
                <div className="stat-label">Diseases</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">86%</div>
                <div className="stat-label">Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          <section className="input-section" id="inputSection" style={{ display: results && !loading ? 'none' : 'block' }}>
            <div className="dashboard-card">
              <div className="card-header">
                <div className="header-icon">
                  <i className="fas fa-user-md"></i>
                </div>
                <div className="header-content">
                  <h2>Patient Information & Symptoms</h2>
                  <p>let us analyze your symptoms using advanced AI System</p>
                </div>
              </div>

              <div className="card-body">
                <div className="patient-info-section">
                  <h3><i className="fas fa-user"></i> Patient Details</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label htmlFor="patientAge">Age *</label>
                      <input type="number" id="patientAge" placeholder="Enter age" min="1" max="120" value={patientAge} onChange={(e) => setPatientAge(e.target.value)} required />
                      <span className="form-hint">Required for accurate diagnosis</span>
                    </div>
                    <div className="form-group">
                      <label htmlFor="patientGender">Gender *</label>
                      <select id="patientGender" value={patientGender} onChange={(e) => setPatientGender(e.target.value)} required>
                        <option value="">Select gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label htmlFor="symptomDuration">Symptom Duration</label>
                      <select id="symptomDuration" value={symptomDuration} onChange={(e) => setSymptomDuration(e.target.value)}>
                        <option value="">Select duration</option>
                        <option value="few_hours">Few hours</option>
                        <option value="1_day">1 day</option>
                        <option value="2_3_days">2-3 days</option>
                        <option value="1_week">1 week</option>
                        <option value="2_weeks">2 weeks</option>
                        <option value="1_month">1 month or more</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="symptoms-section">
                  <h3><i className="fas fa-stethoscope"></i> Describe Your Symptoms</h3>

                  <div className="symptom-input-container">
                    <label htmlFor="symptomsText" className="main-label">
                      Tell us about your symptoms in detail
                    </label>
                    <textarea
                      id="symptomsText"
                      placeholder="Enter your symptoms(e.g., headache, fever, nausea) here(minimum 20 characters)..."
                      rows="8"
                      maxLength="2000"
                      value={symptomsText}
                      onChange={(e) => setSymptomsText(e.target.value)}
                    ></textarea>

                    <div className="input-stats">
                      <div className="stat-item">
                        <i className="fas fa-keyboard"></i>
                        <span>{symptomsText.length}</span> / 2000 characters
                      </div>
                      <div className="stat-item">
                        <i className="fas fa-font"></i>
                        <span>{symptomsText.trim().split(/\s+/).filter(w => w.length > 0).length}</span> words
                      </div>
                    </div>
                  </div>

                  <div className="quick-symptoms">
                    <h4><i className="fas fa-bolt"></i> Quick Add Common Symptoms</h4>
                    <div className="symptom-tags" id="commonSymptoms">
                      {quickSymptoms.map(sym => (
                        <button
                          key={sym}
                          type="button"
                          className={`symptom-tag ${symptomsText.toLowerCase().includes(sym.toLowerCase()) ? 'added' : ''}`}
                          onClick={() => setSymptomsText(prev => prev + (prev ? ', ' : '') + sym.toLowerCase())}
                        >
                          {sym}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}

                <div className="action-section">
                  <button className="btn-primary" id="analyzeBtn" disabled={loading} onClick={handleAnalyze}>
                    <i className="fas fa-brain"></i>
                    <span>{loading ? 'Analyzing...' : 'Analyze Symptoms with AI'}</span>
                    <small>Get instant diagnosis</small>
                  </button>
                  <button className="btn-secondary" id="clearBtn" onClick={handleClear}>
                    <i className="fas fa-eraser"></i>
                    <span>Clear All Fields</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          {loading && (
            <section className="analysis-section" id="analysisSection">
              <div className="dashboard-card">
                <div className="analysis-header">
                  <div className="analysis-spinner">
                    <div className="spinner-ring">
                      <div></div>
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                  </div>
                  <h2>Analyzing Your Symptoms with Our AI</h2>
                  <p>Please wait while we process your information...</p>
                  <div className="single-progress-bar">
                    <div className="progress-fill"></div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {results && !loading && (
            <section className="results-section" id="resultsSection">
              <div className="disclaimer-alert">
                <div className="alert-icon">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <div className="alert-content">
                  <h4>Important Medical Disclaimer</h4>
                  <p>This AI diagnostic tool is designed for educational and informational purposes only. It should never replace professional medical consultation, diagnosis, or treatment. Always seek advice from qualified healthcare professionals for any medical concerns.</p>
                </div>
              </div>

              <div className="dashboard-card">
                <div className="card-header">
                  <div className="header-icon success">
                    <i className="fas fa-check-circle"></i>
                  </div>
                  <div className="header-content">
                    <h2>AI Diagnosis Results</h2>
                    <p>Based on Our Model analysis of your symptoms</p>
                  </div>
                </div>

                <div className="card-body">
                  <div className="quick-diagnosis-info" style={{ background: 'linear-gradient(135deg, #f0f9ff, #e0f2fe)', border: '2px solid #0ea5e9', borderRadius: '16px', padding: '24px', marginBottom: '24px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', textAlign: 'center' }}>
                      <div>
                        <div style={{ fontSize: '36px', color: '#0284c7', fontWeight: 700 }}>{results.predictions?.length || 0}</div>
                        <div style={{ fontSize: '14px', color: '#0369a1', fontWeight: 600 }}>Possible Conditions</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '36px', color: '#0284c7', fontWeight: 700 }}>{results.predictions?.length > 0 ? results.predictions[0].probability : 0}%</div>
                        <div style={{ fontSize: '14px', color: '#0369a1', fontWeight: 600 }}>Top Match Probability</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '36px', color: '#0284c7', fontWeight: 700 }}>{results.processing_time_ms ? (results.processing_time_ms / 1000).toFixed(2) : '0'}s</div>
                        <div style={{ fontSize: '14px', color: '#0369a1', fontWeight: 600 }}>Analysis Time</div>
                      </div>
                    </div>
                  </div>

                  <div className="diagnosis-results" id="diagnosisResults" style={{ marginTop: '20px' }}>
                    {(!results.predictions || results.predictions.length === 0) ? (
                        <div className="no-results">
                            <div className="no-results-icon">🔍</div>
                            <h3>No Specific Diagnosis Found</h3>
                            <p>Our AI couldn't identify specific conditions with sufficient confidence based on the provided symptoms. Please consult a healthcare professional for proper evaluation.</p>
                        </div>
                    ) : (
                        results.predictions.map((predData, idx) => {
                          const prediction = { ...predData, ...predData.info };
                          const severityClass = getSeverityClass(prediction.severity_level);
                          const confidenceClass = `confidence-${prediction.confidence}`;
                          return (
                              <div key={idx} className="result-card slide-up" style={{ animationDelay: `${idx * 0.2}s` }}>
                                <div className="result-header">
                                    <div className="disease-info">
                                        <h4>{prediction.disease}</h4>
                                        <p className="disease-description">{getSimpleDescription(prediction.disease)}</p>
                                    </div>
                                    <div className="probability-info">
                                        <div className="probability-value">{prediction.probability}%</div>
                                        <div className={`confidence-badge ${confidenceClass}`}>
                                            {prediction.confidence} confidence
                                        </div>
                                        <div className={`severity-badge ${severityClass}`}>
                                            {prediction.severity_level || 'moderate'} severity
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="probability-bar">
                                    <div className="probability-fill" style={{ width: `${prediction.probability}%` }}></div>
                                </div>
                                
                                <div className="result-details">
                                    {prediction.primary_symptoms && prediction.primary_symptoms.length > 0 && (
                                        <div className="matched-symptoms">
                                            <h5 className="section-title">
                                                <i className="fas fa-check-circle"></i>
                                                Primary Symptoms for {prediction.disease}
                                            </h5>
                                            <div className="symptom-matches">
                                                {prediction.primary_symptoms.map((s, i) => (
                                                    <span key={i} className="symptom-match">{s.replace(/_/g, ' ')}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {prediction.immediate_advice && prediction.immediate_advice.length > 0 ? (
                                        <>
                                            <div className="recommendations">
                                                <h5 className="section-title">
                                                    <i className="fas fa-lightbulb"></i> Immediate Advice
                                                </h5>
                                                <ul>
                                                    {prediction.immediate_advice.map((adv, i) => <li key={i}>{adv}</li>)}
                                                </ul>
                                            </div>
                                            
                                            {prediction.quick_solutions && prediction.quick_solutions.length > 0 && (
                                                <div className="quick-solutions">
                                                    <h5 className="section-title">
                                                        <i className="fas fa-bolt"></i> Quick Solutions
                                                    </h5>
                                                    <ul>
                                                        {prediction.quick_solutions.map((sol, i) => <li key={i}>{sol}</li>)}
                                                    </ul>
                                                </div>
                                            )}
                                        </>
                                    ) : (
                                        <div className="recommendations">
                                            <h5 className="section-title">
                                                <i className="fas fa-lightbulb"></i> General Recommendations
                                            </h5>
                                            <ul>
                                                <li>Rest and stay hydrated</li>
                                                <li>Monitor your symptoms</li>
                                                <li>Avoid strenuous activities</li>
                                                <li>Consult a healthcare provider for proper diagnosis</li>
                                            </ul>
                                        </div>
                                    )}

                                    <div className="next-steps">
                                        <h5 className="section-title">
                                            <i className="fas fa-user-md"></i> When to Seek Medical Help
                                        </h5>
                                        <p className="help-guidance">{prediction.when_to_seek_help || 'Consult a healthcare provider if symptoms persist or worsen'}</p>
                                        {prediction.specialist_recommendation && (
                                            <p className="specialist-rec">
                                                <strong>Recommended Specialist:</strong> {prediction.specialist_recommendation}
                                            </p>
                                        )}
                                    </div>
                                </div>
                                
                                {prediction.probability > 80 && (
                                    <div className="high-risk-warning">
                                        <div className="warning-icon">⚠️</div>
                                        <div className="warning-content">
                                            <h6>High Probability Alert</h6>
                                            <p><strong>This condition shows high probability (&gt;80%). We strongly recommend consulting a healthcare provider as soon as possible for proper medical evaluation.</strong></p>
                                        </div>
                                    </div>
                                )}
                            </div>
                          );
                        })
                    )}
                  </div>
                  
                  {results.summary && (
                     <div className="result-card slide-up" style={{ animationDelay: '0.8s', marginTop: '20px', borderLeft: '4px solid #10b981', backgroundColor: '#f0fdf4' }}>
                        <div className="result-header" style={{ paddingBottom: '15px' }}>
                            <h4 style={{ color: '#065f46', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <i className="fas fa-robot"></i> AI Diagnosis Summary
                            </h4>
                        </div>
                        <div className="result-details" style={{ color: '#064e3b', lineHeight: 1.6, fontSize: '0.95rem' }} dangerouslySetInnerHTML={{ __html: results.summary.replace(/\n/g, '<br>') }}>
                        </div>
                     </div>
                  )}
                </div>
              </div>

              <div className="results-actions">
                <button className="btn-primary" id="newDiagnosisBtn" onClick={() => { setResults(null); setSymptomsText(''); }}>
                  <i className="fas fa-plus-circle"></i>
                  <span>New Diagnosis</span>
                </button>
                <button className="btn-secondary" id="downloadReportBtn" onClick={downloadReport}>
                  <i className="fas fa-download"></i>
                  <span>Download Report</span>
                </button>
              </div>
            </section>
          )}

        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h4><i className="fas fa-brain"></i> HealthPilot</h4>
              <p>Advanced AI system for medical symptom analysis, trained on 2500+ medical records and 50 unique diseases.</p>
              <div className="tech-badges">
                <span className="tech-badge">LightGBM</span>
                <span className="tech-badge">NLP Processing</span>
                <span className="tech-badge">Groq LLM</span>
              </div>
            </div>
            
            <div className="footer-section">
              <h4><i className="fas fa-chart-bar"></i> Model Performance</h4>
              <ul className="performance-list">
                <li><span className="metric">Macro F1 Score :</span> <span className="value">87</span></li>
                <li><span className="metric">Test Accuracy:</span> <span className="value">86%</span></li>
                <li><span className="metric">Top-3 Accuracy:</span> <span className="value">96.1%</span></li>
                <li><span className="metric">Response Time:</span> <span className="value">&lt;2 seconds</span></li>
              </ul>
            </div>
            
            <div className="footer-section">
              <h4><i className="fas fa-shield-alt"></i> Safety & Ethics</h4>
              <ul className="safety-list">
                <li><i className="fas fa-check"></i> Educational purpose only</li>
                <li><i className="fas fa-check"></i> Privacy-focused design</li>
                <li><i className="fas fa-check"></i> No data storage</li>
                <li><i className="fas fa-check"></i> Professional medical disclaimer</li>
              </ul>
            </div>
          </div>
          
          <div className="footer-bottom">
            <div className="footer-legal">
              <p>&copy; 2026 HealthPilot. Built for educational and research purposes.</p>
              <p><strong>Important:</strong> This system is not a substitute for professional medical advice, diagnosis, or treatment.</p>
            </div>
          </div>
        </div>
      </footer>

      <button id="chatbot-fab" className="chatbot-fab" aria-label="Open AI Doctor Chat" title="Chat with AI Doctor" onClick={() => setChatOpen(!chatOpen)}>
        <span className="chatbot-fab-icon">
          <i className="fas fa-robot"></i>
        </span>
        <span className="chatbot-fab-badge" id="chatbotBadge">1</span>
        <span className="chatbot-fab-label">AI Doctor</span>
      </button>

      {chatOpen && (
        <div className="chatbot-widget fade-in open" id="chatbotWidget" aria-hidden="false" style={{ display: 'flex' }}>
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <div className="chatbot-avatar">
                <i className="fas fa-user-md"></i>
                <span className="chatbot-online-dot"></span>
              </div>
              <div className="chatbot-header-text">
                <h4>AI Doctor</h4>
                <span className="chatbot-status">Online</span>
              </div>
            </div>
            <div className="chatbot-header-actions">
              <button id="chatbotClearBtn" className="chatbot-icon-btn" title="Clear conversation" onClick={() => setChatHistory([{ role: 'assistant', content: "Hello! 👋 I'm your AI Medical Assistant. Describe your symptoms in natural language and I'll help you understand what might be going on. Remember — I'm here to assist, not replace a real doctor." }])}>
                <i className="fas fa-trash-alt"></i>
              </button>
              <button id="chatbotCloseBtn" className="chatbot-icon-btn" title="Close chat" onClick={() => setChatOpen(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
          </div>

          <div className="chatbot-disclaimer">
            <i className="fas fa-shield-alt"></i>
            For informational purposes only. Not a substitute for professional medical advice.
          </div>

          <div className="chatbot-messages" id="chatbotMessages">
            {chatHistory.map((msg, i) => {
              const isBot = msg.role === 'assistant';
              return (
                <div key={i} className={`chat-msg ${isBot ? 'bot' : 'user'}`}>
                  <div className="chat-msg-avatar">
                    <i className={`fas ${isBot ? 'fa-user-md' : 'fa-user'}`}></i>
                  </div>
                  <div className="chat-msg-bubble" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }}></div>
                </div>
              );
            })}
            {chatLoading && (
              <div className="chatbot-typing visible" id="chatbotTyping">
                <div className="chatbot-typing-bubble">
                  <span></span><span></span><span></span>
                </div>
                <p>AI Doctor is thinking…</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chatbot-input-area">
            <div className="chatbot-input-wrapper">
              <textarea
                id="chatbotInput"
                className="chatbot-input"
                placeholder="Describe your symptoms…"
                rows="1"
                maxLength="800"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyPress={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChat(); } }}
              ></textarea>
              <button id="chatbotSend" className="chatbot-send-btn" disabled={!chatInput.trim() || chatLoading} onClick={handleSendChat}>
                <i className="fas fa-paper-plane"></i>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
