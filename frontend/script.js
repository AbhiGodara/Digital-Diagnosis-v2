class MedicalDiagnosisApp {
    constructor() {
        // API Configuration
        this.API_BASE_URL = 'http://127.0.0.1:8000/api';
        
        // App State
        this.currentStep = 'input';
        this.isAnalyzing = false;
        this.diagnosisHistory = this.loadHistory();
        
        // Medical terms for real-time detection
        // this.medicalTerms = [
        //     'fever', 'headache', 'cough', 'nausea', 'fatigue', 'dizziness', 'pain',
        //     'breathing', 'chest', 'stomach', 'throat', 'muscle', 'joint', 'back',
        //     'weakness', 'vomiting', 'diarrhea', 'constipation', 'rash', 'swelling'
        // ];
        
        // Initialize the app
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Medical Diagnosis App...');
        
        // Setup all event listeners
        this.setupEventListeners();
        
        // Setup form validation
        this.setupFormValidation();
        
        // Load history
        this.displayHistory();
        
        // Check API connection
        this.checkAPIConnection();
        
        console.log('✅ App initialized successfully!');
    }
    
    setupEventListeners() {
        // Form input events
        document.getElementById('symptomsText').addEventListener('input', () => {
            this.handleSymptomInput();
        });
        
        document.getElementById('patientAge').addEventListener('input', (e) => {
            if (e.target.value < 0) e.target.value = ''; // Prevent negative
            this.validateForm();
        });
        
        document.getElementById('patientGender').addEventListener('change', () => {
            this.validateForm();
        });

        document.getElementById('symptomDuration').addEventListener('change', () => {
            this.validateForm();
        });
        
        // Button events
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.startDiagnosis();
        });
        
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearForm();
        });
        
        document.getElementById('newDiagnosisBtn')?.addEventListener('click', () => {
            this.resetToInput();
        });
        
        document.getElementById('downloadReportBtn')?.addEventListener('click', () => {
            this.downloadReport();
        });
        
        // Symptom tag events (quick add symptoms)
        document.querySelectorAll('.symptom-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                this.addSymptomTag(e.target.dataset.symptom);
            });
        });
    }
    
    handleSymptomInput() {
        const textarea = document.getElementById('symptomsText');
        const text = textarea.value;
        
        // Update text statistics
        this.updateTextStats(text);
        
        // Validate form
        this.validateForm();
        
        // Real-time medical term detection
        // this.highlightMedicalTerms(text);
    }
    
    updateTextStats(text) {
        const charCount = text.length;
        const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
        // const medicalTermCount = this.countMedicalTerms(text);
        
        // Update display
        document.getElementById('charCount').textContent = charCount;
        document.getElementById('wordCount').textContent = wordCount;
        // document.getElementById('medicalTerms').textContent = medicalTermCount;
        
        // Color coding for medical terms
        // const medicalTermsElement = document.getElementById('medicalTerms');
        // if (medicalTermCount >= 5) {
        //     medicalTermsElement.style.color = '#10b981'; // Green - Excellent
        // } else if (medicalTermCount >= 3) {
        //     medicalTermsElement.style.color = '#f59e0b'; // Orange - Good
        // } else if (medicalTermCount >= 1) {
        //     medicalTermsElement.style.color = '#ef4444'; // Red - Needs more
        // } else {
        //     medicalTermsElement.style.color = '#6b7280'; // Gray - None detected
        // }
    }
    
    // countMedicalTerms(text) {
    //     const lowerText = text.toLowerCase();
    //     let count = 0;
        
    //     this.medicalTerms.forEach(term => {
    //         if (lowerText.includes(term)) {
    //             count++;
    //         }
    //     });
        
    //     return count;
    // }
    
    // highlightMedicalTerms(text) {
    //     // Visual feedback for detected medical terms
    //     const detectedTerms = [];
    //     const lowerText = text.toLowerCase();
        
    //     this.medicalTerms.forEach(term => {
    //         if (lowerText.includes(term)) {
    //             detectedTerms.push(term);
    //         }
    //     });
        
    //     // You could add visual highlighting here if needed
    //     console.log('Detected medical terms:', detectedTerms);
    // }
    
    validateForm() {
        const symptoms = document.getElementById('symptomsText').value.trim();
        const age = document.getElementById('patientAge').value;
        const gender = document.getElementById('patientGender').value;
        const duration = document.getElementById('symptomDuration').value;
        
        // Validation rules
        const hasValidSymptoms = symptoms.length >= 20; // At least 20 characters
        const hasValidAge = age && parseInt(age) >= 1 && parseInt(age) <= 120;
        const hasValidGender = gender !== '';
        const hasValidDuration = duration !== '';
        
        const isFormValid = hasValidSymptoms && hasValidAge && hasValidGender && hasValidDuration;
        
        // Update button state
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = !isFormValid;
        
        // Visual feedback
        if (isFormValid) {
            analyzeBtn.classList.remove('disabled');
        } else {
            analyzeBtn.classList.add('disabled');
        }
        
        return isFormValid;
    }
    
    addSymptomTag(symptom) {
        const textarea = document.getElementById('symptomsText');
        const currentText = textarea.value.toLowerCase();
        
        // Check if symptom already exists
        if (!currentText.includes(symptom.toLowerCase())) {
            const newText = textarea.value ? `${textarea.value}, ${symptom}` : symptom;
            textarea.value = newText;
            
            // Visual feedback
            const clickedTag = event.target;
            clickedTag.classList.add('added');
            clickedTag.style.backgroundColor = '#10b981';
            
            setTimeout(() => {
                clickedTag.classList.remove('added');
                clickedTag.style.backgroundColor = '';
            }, 1500);
            
            // Update stats
            this.handleSymptomInput();
        }
    }
    
    clearForm() {
        // Clear all form fields
        document.getElementById('symptomsText').value = '';
        // document.getElementById('patientAge').value = '';
        // document.getElementById('patientGender').value = '';
        // document.getElementById('symptomDuration').value = '';
        
        // Reset stats
        this.updateTextStats('');
        this.validateForm();
        
        console.log('🧹 Form cleared');
    }
    
    async checkAPIConnection() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                console.log('🟢 API connection successful');
            } else {
                console.warn('🟡 API connection issues:', data);
                this.showAlert('API service may have issues', 'warning');
            }
        } catch (error) {
            console.error('🔴 Cannot connect to API:', error);
            this.showAlert('Cannot connect to diagnosis service. Please check if the server is running.', 'error');
        }
    }
    
    async startDiagnosis() {
        if (this.isAnalyzing) {
            console.log('⏳ Diagnosis already in progress...');
            return;
        }
        
        // Validate form
        if (!this.validateForm()) {
            this.showAlert('Please fill in all required fields correctly', 'warning');
            return;
        }
        
        // Get form data
        const symptoms = document.getElementById('symptomsText').value.trim();
        const age = document.getElementById('patientAge').value;
        const gender = document.getElementById('patientGender').value;
        const duration = document.getElementById('symptomDuration').value;
        
        console.log('🔬 Starting diagnosis process...');
        
        this.isAnalyzing = true;
        this.showSection('analysis');
        
        try {
            // Show loading animation for 3 seconds
            await this.delay(2000);
            
            // Call diagnosis API
            const diagnosisResults = await this.callDiagnosisAPI({
                symptoms_text: symptoms,
                patient_age: parseInt(age),
                patient_gender: gender,
                symptom_duration: duration
            });
            
            // Display results
            this.displayResults(diagnosisResults);
            
            // Save to history
            this.saveDiagnosisToHistory({
                timestamp: new Date().toISOString(),
                symptoms: symptoms,
                patient_info: { age, gender, duration },
                results: diagnosisResults
            });
            
            console.log('✅ Diagnosis completed successfully');
            
        } catch (error) {
            console.error('❌ Diagnosis failed:', error);
            this.showAlert(`Diagnosis failed: ${error.message}`, 'error');
            this.resetToInput();
        } finally {
            this.isAnalyzing = false;
        }
    }
    
    async callDiagnosisAPI(requestData) {
        console.log('📡 Calling diagnosis API with data:', requestData);
        
        const response = await fetch(`${this.API_BASE_URL}/diagnose`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred during diagnosis');
        }
        
        console.log('📊 API Response received:', data);
        return data;
    }
    
    displayResults(data) {
        console.log('🎯 Displaying diagnosis results...');
        
        this.showSection('results');
        
        // Update confidence display
        // this.updateConfidenceDisplay(data.confidence || 50);
        
        // Display processing summary
        this.displayProcessingSummary(data);
        
        // Display main diagnosis results
        this.displayDiagnosisResults(data.predictions || []);
        
        // Display AI summary
        if (data.summary) {
            this.displaySummary(data.summary);
        }
        
        // Check for high-probability warnings
        this.checkForHighRiskWarnings(data.predictions || []);
    }
    
    // updateConfidenceDisplay(confidence) {
    //     const confidenceValue = document.getElementById('confidenceValue');
    //     const confidenceCircle = document.getElementById('confidenceCircle');
        
    //     if (confidenceValue) {
    //         confidenceValue.textContent = `${confidence}%`;
    //     }
        
    //     if (confidenceCircle) {
    //         // Determine color based on confidence level
    //         let color = '#ef4444'; // Red for low confidence
    //         if (confidence >= 70) {
    //             color = '#10b981'; // Green for high confidence
    //         } else if (confidence >= 50) {
    //             color = '#f59e0b'; // Orange for medium confidence
    //         }
            
    //         // Update circular progress
    //         confidenceCircle.style.background = 
    //             `conic-gradient(${color} ${confidence}%, rgba(255, 255, 255, 0.3) 0)`;
    //     }
    // }
    
    displayProcessingSummary(data) {
        // Update quick stats
        const totalPredictions = data.predictions?.length || 0;
        const topProbability = data.predictions?.[0]?.probability || 0;
        const processingTime = data.processing_time || 0;
        // const keywordsCount = data.extracted_keywords?.length || 0;
        
        // Update display
        document.getElementById('totalPredictions').textContent = totalPredictions;
        document.getElementById('topProbability').textContent = topProbability + '%';
        document.getElementById('processingTime').textContent = processingTime + 's';
        // document.getElementById('keywordsCount').textContent = keywordsCount;
    }
    
    displayDiagnosisResults(predictions) {
        const resultsContainer = document.getElementById('diagnosisResults');
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }
        
        resultsContainer.innerHTML = '';
        
        if (!predictions || predictions.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">🔍</div>
                    <h3>No Specific Diagnosis Found</h3>
                    <p>Our AI couldn't identify specific conditions with sufficient confidence based on the provided symptoms. Please consult a healthcare professional for proper evaluation.</p>
                </div>
            `;
            return;
        }
        
        console.log(`📋 Displaying ${predictions.length} diagnosis results`);
        
        predictions.forEach((prediction, index) => {
            // Unpack info block to support existing UI templating structure
            if (prediction.info) {
                Object.assign(prediction, prediction.info);
            }

            const resultCard = this.createResultCard(prediction, index);
            resultsContainer.appendChild(resultCard);
            
            // Animate probability bar with delay
            setTimeout(() => {
                const probabilityFill = resultCard.querySelector('.probability-fill');
                if (probabilityFill) {
                    probabilityFill.style.width = `${prediction.probability}%`;
                }
            }, 600 + (index * 200));
        });
    }
    
    createResultCard(prediction, index) {
        const card = document.createElement('div');
        card.className = 'result-card slide-up';
        card.style.animationDelay = `${index * 0.2}s`;
        
        // Determine severity styling
        const severityClass = this.getSeverityClass(prediction.severity_level);
        const confidenceClass = `confidence-${prediction.confidence}`;
        
        card.innerHTML = `
            <div class="result-header">
                <div class="disease-info">
                    <h4>${prediction.disease}</h4>
                    <p class="disease-description">${this.getSimpleDescription(prediction.disease)}</p>
                </div>
                <div class="probability-info">
                    <div class="probability-value">${prediction.probability}%</div>
                    <div class="confidence-badge ${confidenceClass}">
                        ${prediction.confidence} confidence
                    </div>
                    <div class="severity-badge ${severityClass}">
                        ${prediction.severity_level || 'moderate'} severity
                    </div>
                </div>
            </div>
            
            <div class="probability-bar">
                <div class="probability-fill"></div>
            </div>
            
            <div class="result-details">
                ${this.createSymptomsSection(prediction)}
                ${this.createAdviceSection(prediction)}
                ${this.createNextStepsSection(prediction)}
            </div>
            
            ${prediction.probability > 80 ? this.createHighRiskWarning() : ''}
        `;
        
        return card;
    }
    
    displaySummary(summaryText) {
        const resultsContainer = document.getElementById('diagnosisResults');
        if (!resultsContainer) return;
        
        const summaryCard = document.createElement('div');
        summaryCard.className = 'result-card slide-up';
        summaryCard.style.animationDelay = '0.8s';
        summaryCard.style.marginTop = '20px';
        summaryCard.style.borderLeft = '4px solid #10b981';
        summaryCard.style.backgroundColor = '#f0fdf4';
        
        summaryCard.innerHTML = `
            <div class="result-header" style="padding-bottom: 15px;">
                <h4 style="color: #065f46; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-robot"></i> AI Diagnosis Summary
                </h4>
            </div>
            <div class="result-details" style="color: #064e3b; line-height: 1.6; font-size: 0.95rem;">
                ${summaryText.replace(/\n/g, '<br>')}
            </div>
        `;
        
        resultsContainer.appendChild(summaryCard);
    }
    
    getSeverityClass(severity) {
        const severityMap = {
            'mild': 'severity-mild',
            'moderate': 'severity-moderate',
            'serious': 'severity-serious',
            'critical': 'severity-critical'
        };
        return severityMap[severity] || 'severity-moderate';
    }
    
    getSimpleDescription(diseaseName) {
        // Simple disease descriptions (you could expand this)
        const descriptions = {
            'diabetes': 'A metabolic disorder with high blood sugar levels',
            'hypertension': 'High blood pressure condition',
            'asthma': 'Respiratory condition affecting airways',
            'anxiety': 'Mental health condition with excessive worry',
            'migraine': 'Severe headache disorder',
            'pneumonia': 'Lung infection causing breathing difficulties'
        };
        
        const lowerName = diseaseName.toLowerCase();
        for (const [key, description] of Object.entries(descriptions)) {
            if (lowerName.includes(key)) {
                return description;
            }
        }
        
        return 'Medical condition requiring professional evaluation';
    }
    
    createSymptomsSection(prediction) {
        if (!prediction.primary_symptoms || prediction.primary_symptoms.length === 0) {
            return '';
        }
        
        return `
            <div class="matched-symptoms">
                <h5 class="section-title">
                    <i class="fas fa-check-circle"></i>
                    Primary Symptoms for ${prediction.disease}
                </h5>
                <div class="symptom-matches">
                    ${prediction.primary_symptoms.map(symptom => 
                        `<span class="symptom-match">${symptom.replace(/_/g, ' ')}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }
    
    createAdviceSection(prediction) {
        if (!prediction.immediate_advice || prediction.immediate_advice.length === 0) {
            return this.getDefaultAdvice();
        }
        
        return `
            <div class="recommendations">
                <h5 class="section-title">
                    <i class="fas fa-lightbulb"></i>
                    Immediate Advice
                </h5>
                <ul>
                    ${prediction.immediate_advice.map(advice => 
                        `<li>${advice}</li>`
                    ).join('')}
                </ul>
            </div>
            
            ${prediction.quick_solutions ? `
                <div class="quick-solutions">
                    <h5 class="section-title">
                        <i class="fas fa-bolt"></i>
                        Quick Solutions
                    </h5>
                    <ul>
                        ${prediction.quick_solutions.map(solution => 
                            `<li>${solution}</li>`
                        ).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }
    
    createNextStepsSection(prediction) {
        return `
            <div class="next-steps">
                <h5 class="section-title">
                    <i class="fas fa-user-md"></i>
                    When to Seek Medical Help
                </h5>
                <p class="help-guidance">${prediction.when_to_seek_help || 'Consult a healthcare provider if symptoms persist or worsen'}</p>
                ${prediction.specialist_recommendation ? `
                    <p class="specialist-rec">
                        <strong>Recommended Specialist:</strong> ${prediction.specialist_recommendation}
                    </p>
                ` : ''}
            </div>
        `;
    }
    
    getDefaultAdvice() {
        return `
            <div class="recommendations">
                <h5 class="section-title">
                    <i class="fas fa-lightbulb"></i>
                    General Recommendations
                </h5>
                <ul>
                    <li>Rest and stay hydrated</li>
                    <li>Monitor your symptoms</li>
                    <li>Avoid strenuous activities</li>
                    <li>Consult a healthcare provider for proper diagnosis</li>
                </ul>
            </div>
        `;
    }
    
    createHighRiskWarning() {
        return `
            <div class="high-risk-warning">
                <div class="warning-icon">⚠️</div>
                <div class="warning-content">
                    <h6>High Probability Alert</h6>
                    <p><strong>This condition shows high probability (>80%). We strongly recommend consulting a healthcare provider as soon as possible for proper medical evaluation.</strong></p>
                </div>
            </div>
        `;
    }
    
    checkForHighRiskWarnings(predictions) {
        const highRiskPredictions = predictions.filter(p => p.probability > 80);
        
        if (highRiskPredictions.length > 0) {
            console.warn('⚠️ High risk predictions detected:', highRiskPredictions);
            
            const warningMessage = `High probability detected for: ${
                highRiskPredictions.map(p => `${p.disease} (${p.probability}%)`).join(', ')
            }. Please consult a healthcare provider soon.`;
            
            this.showAlert(warningMessage, 'warning', 8000); // Show for 8 seconds
        }
    }
    
    saveDiagnosisToHistory(diagnosisData) {
        this.diagnosisHistory.unshift(diagnosisData);
        
        // Keep only last 10 diagnoses
        if (this.diagnosisHistory.length > 10) {
            this.diagnosisHistory = this.diagnosisHistory.slice(0, 10);
        }
        
        // Save to localStorage
        try {
            localStorage.setItem('diagnosisHistory', JSON.stringify(this.diagnosisHistory));
            console.log('💾 Diagnosis saved to history');
        } catch (error) {
            console.error('Failed to save to history:', error);
        }
        
        // Update display
        this.displayHistory();
    }
    
    loadHistory() {
        try {
            const history = localStorage.getItem('diagnosisHistory');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Failed to load history:', error);
            return [];
        }
    }
    
    displayHistory() {
        const historyContainer = document.getElementById('historyList');
        const historySection = document.getElementById('historySection');
        
        if (!historyContainer || !historySection) return;
        
        if (this.diagnosisHistory.length === 0) {
            historySection.style.display = 'none';
            return;
        }
        
        historySection.style.display = 'block';
        historyContainer.innerHTML = '';
        
        this.diagnosisHistory.slice(0, 5).forEach((history, index) => {
            const historyItem = this.createHistoryItem(history, index);
            historyContainer.appendChild(historyItem);
        });
    }
    
    createHistoryItem(history, index) {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        const date = new Date(history.timestamp).toLocaleString();
        const topResult = history.results?.predictions?.[0];
        const symptomsPreview = history.symptoms.length > 80 ? 
            history.symptoms.substring(0, 80) + '...' : 
            history.symptoms;
        
        item.innerHTML = `
            <div class="history-header">
                <span class="history-date">${date}</span>
                ${topResult ? `
                    <span class="confidence-badge confidence-${topResult.confidence}">
                        ${topResult.confidence} confidence
                    </span>
                ` : ''}
            </div>
            <div class="history-symptoms">${symptomsPreview}</div>
            <div class="history-result">
                ${topResult ? 
                    `Top result: ${topResult.disease} (${topResult.probability}%)` : 
                    'No specific diagnosis found'
                }
            </div>
        `;
        
        return item;
    }
    
    showSection(sectionName) {
        console.log(`📱 Switching to ${sectionName} section`);
        
        // Hide all main sections
        const sections = ['inputSection', 'analysisSection', 'resultsSection'];
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.add('hidden');
            }
        });
        
        // Show target section with animation
        const targetSection = document.getElementById(sectionName + 'Section');
        if (targetSection) {
            targetSection.classList.remove('hidden');
            targetSection.classList.add('fade-in');
        }
        
        // Scroll to top smoothly
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        this.currentStep = sectionName;
    }
    
    resetToInput() {
        console.log('🔄 Resetting to input section');
        this.showSection('input');
        this.isAnalyzing = false;
    }
    
    downloadReport() {
        console.log('📄 Generating diagnosis report...');
        
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;
        
        // Clone the results section to manipulate
        const clonedResults = resultsSection.cloneNode(true);
        
        // Remove the disclaimer alert from the cloned content
        const disclaimer = clonedResults.querySelector('.disclaimer-alert');
        if (disclaimer) {
            disclaimer.remove();
        }
        
        // Remove action buttons from cloned content
        const actionButtons = clonedResults.querySelector('.results-actions');
        if (actionButtons) {
            actionButtons.remove();
        }
        
        // Create printable window
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
                        .keyword-tag, .profile-tag {
                            display: inline-block;
                            padding: 4px 8px;
                            margin: 4px;
                            border-radius: 4px;
                            font-size: 12px;
                        }
                        .keyword-tag {
                            background: rgba(37, 99, 235, 0.1);
                            color: #2563eb;
                            border: 1px solid rgba(37, 99, 235, 0.2);
                        }
                        .profile-tag {
                            background: rgba(124, 58, 237, 0.1);
                            color: #7c3aed;
                            border: 1px solid rgba(124, 58, 237, 0.2);
                        }
                        @media print { 
                            body { margin: 0; }
                            .no-print { display: none; }
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>🧠 AI Medical Diagnosis Report</h1>
                        <p><strong>Generated:</strong> ${currentDate}</p>
                    </div>
                    
                    ${clonedResults.innerHTML.replace(/class="hidden"/g, '').replace(/hidden/g, '')}
                    
                    <div style="margin-top: 40px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #d1d5db; padding-top: 20px;">
                        <p><strong>This report was generated by:</strong></p>
                        <p>AI Medical Diagnosis System v1.0</p>
                        <p>Trained on 254 diseases with 86% accuracy</p>
                        <p><em>For questions or concerns, consult with your healthcare provider</em></p>
                    </div>
                </body>
            </html>
        `);
        
        printWindow.document.close();
        
        // Wait a moment then trigger print
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 1000);
    }
    
    showAlert(message, type = 'info', duration = 5000) {
        console.log(`🔔 Alert [${type}]: ${message}`);
        
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        
        // Icon mapping
        const icons = {
            'info': '🔵',
            'success': '✅', 
            'warning': '⚠️',
            'error': '❌'
        };
        
        alert.innerHTML = `
            <div class="alert-content">
                <span class="alert-icon">${icons[type] || icons.info}</span>
                <span class="alert-message">${message}</span>
                <button class="alert-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Color mapping
        const colors = {
            'info': { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
            'success': { bg: '#d1fae5', border: '#10b981', text: '#065f46' },
            'warning': { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
            'error': { bg: '#fee2e2', border: '#ef4444', text: '#dc2626' }
        };
        
        const color = colors[type] || colors.info;
        
        // Style the alert
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${color.bg};
            border: 2px solid ${color.border};
            color: ${color.text};
            border-radius: 12px;
            padding: 16px 20px;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease-out;
            font-size: 14px;
            font-weight: 500;
        `;
        
        // Add to DOM
        document.body.appendChild(alert);
        
        // Auto remove after duration
        setTimeout(() => {
            if (document.body.contains(alert)) {
                alert.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => alert.remove(), 300);
            }
        }, duration);
        
        // Add animation styles if they don't exist
        if (!document.querySelector('#alert-animations')) {
            const style = document.createElement('style');
            style.id = 'alert-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
                .alert-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .alert-close {
                    background: none;
                    border: none;
                    font-size: 20px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-left: auto;
                    opacity: 0.7;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 50%;
                }
                .alert-close:hover {
                    opacity: 1;
                    background: rgba(0,0,0,0.1);
                }
                .no-results {
                    text-align: center;
                    padding: 60px 40px;
                    color: #6b7280;
                    background: #f9fafb;
                    border-radius: 16px;
                    margin: 20px 0;
                }
                .no-results-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                .no-results h3 {
                    font-size: 24px;
                    margin-bottom: 12px;
                    color: #374151;
                }
                .high-risk-warning {
                    background: linear-gradient(135deg, #fee2e2, #fecaca);
                    border: 2px solid #ef4444;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 20px 0;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }
                .warning-icon {
                    font-size: 32px;
                    flex-shrink: 0;
                }
                .warning-content h6 {
                    color: #dc2626;
                    font-size: 16px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }
                .warning-content p {
                    color: #991b1b;
                    margin: 0;
                    font-size: 14px;
                }
                .severity-mild { background: #d1fae5; color: #065f46; }
                .severity-moderate { background: #fef3c7; color: #92400e; }
                .severity-serious { background: #fed7aa; color: #9a3412; }
                .severity-critical { background: #fee2e2; color: #dc2626; }
            `;
            document.head.appendChild(style);
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Utility method for debugging
    debugLog(message, data = null) {
        if (data) {
            console.log(`🐛 DEBUG: ${message}`, data);
        } else {
            console.log(`🐛 DEBUG: ${message}`);
        }
    }
}

// Initialize the app when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌟 DOM Content Loaded - Initializing Medical Diagnosis App');
        window.medicalApp = new MedicalDiagnosisApp();
        
        console.log('🎉 Medical Diagnosis App loaded successfully!');
        console.log('📱 Ready for user interaction');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('👀 Page became visible');
        // Could check API connection here if needed
    }
});

// Handle beforeunload to save any unsaved data
window.addEventListener('beforeunload', (e) => {
    // Save any important state before page unloads
    console.log('💾 Page unloading - saving state');
});

// Export for potential external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedicalDiagnosisApp;
}