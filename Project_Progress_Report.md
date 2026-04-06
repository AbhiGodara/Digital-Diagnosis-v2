# Project Progress Report: Digital Diagnosis 2.0

## 1. What We Are Building
When people get sick, they often search their symptoms on Google and end up confused or terrified by the results. We want to fix that. 

For our project, we are building **Digital Diagnosis 2.0**, an AI-powered symptom checker that feels like talking to a real human. Instead of forcing users to click through endless, confusing medical menus, our app lets them type exactly how they are feeling in their own words—like "My head hurts, I feel hot, and I've been super tired for 3 days." The AI understands what they mean, runs the data through a machine learning model, and gives them a clear, calm, and helpful summary of what might be wrong and what to do next.

## 2. System Architecture & Current Pipeline Flow
We designed the system to be very organized so that the AI doesn't just guess randomly. Here is exactly how the data flows when a user clicks the "Analyze" button:

1. **User Input:** The user fills out a simple webpage form with their age, gender, how long they've been sick, and a text box where they describe their symptoms in plain English.
2. **Symptom Extraction (AI Phase 1):** The text is sent to our first AI brain. Instead of trying to diagnose the patient immediately, its only job is to read the messy text and pick out standardized symptoms (translating slang like "tummy hurts" into "abdominal pain"). It checks these against our official list of 84 symptoms and creates a massive string of 1s and 0s representing what the user has.
3. **Machine Learning Prediction:** This list of numbers is handed over to our trained Machine Learning model. It does the heavy math and spits out the top 3 most likely sicknesses along with a percentage score (for example, "85% chance it's the Flu").
4. **Knowledge Base Lookup:** The backend takes those 3 sicknesses and looks them up in an internal database we created. This database holds practical advice, severity levels, and specialist recommendations for 42 different diseases.
5. **Final AI Summary (AI Phase 2):** Finally, we take the user's demographic info, the disease predictions, and the database advice, and give it all to our second AI brain. This AI writes a highly personalized, easy-to-read summary that acts like a virtual nurse giving you your results and next steps.

## 3. Technology Stack
We used simple, fast, and powerful tools to piece this together:
- **Frontend (What the user sees):** Plain HTML, CSS, and JavaScript. We purposely avoided overly complicated web frameworks to make sure the site is lightweight and loads instantly in any browser.
- **Backend Server:** Python, using a framework called FastAPI. It handles all the data moving back and forth between the frontend and the AI extremely fast.
- **Machine Learning:** LightGBM (part of the Scikit-Learn family). It is an incredibly fast algorithm that is great for predicting outcomes based on lists of features.
- **AI Integration:** We used LangChain to connect our app to the Groq API, specifically using the Llama-3.3 model. It is brilliant at reading context and writing natural human language.

## 4. How We Gathered Our Data
A machine learning model is only as smart as the data it studies. We couldn't just invent fake data, so we spent a lot of time finding real, public health data from government websites, epidemiology records, and open-source medical repositories. 

We had to do a lot of cleaning to make it useful. We organized the data into a massive spreadsheet that connects 42 specific diseases (like Asthma, Malaria, and Hypertension) to our master list of 84 symptoms. By formatting genuine health records into simple "true/false" symptom columns, we created a highly accurate dataset with over 2,100 specific examples. This huge amount of real-world data allowed our algorithm to learn how different sickness clusters actually look in the real world.

## 5. Current Progress: What Has Been Built
We have successfully built the core of the project! Here is what is fully working right now:
- **The Website User Interface:** The pages are designed beautifully, take user input smoothly, and display the final disease cards cleanly.
- **The Machine Learning Model:** The model has been successfully trained on our curated data and is actively predicting diseases with high accuracy.
- **The Hybrid Pipeline:** The dual-AI setup is working perfectly. The first AI accurately tracks down symptoms, and the second AI successfully uses the math to write helpful advice.
- **End-to-End Connection:** A user can fill out the form, hit submit, and within seconds the frontend communicates with the backend, runs the math, asks the AI for a summary, and brings it all back to the screen seamlessly.

## 6. Future Roadmap & Upcoming Features
We have some exciting plans to make this even better as we continue working on it:
- **More Languages:** We want the AI to let users type their symptoms in Spanish, Hindi, or French, but still calculate the medical math in English behind the scenes.
- **Doctor Feedback Loop:** A way for real medical professionals to "thumbs up" or "thumbs down" the results to make the machine learning model smarter over time.
- **Interactive Conversational Chatbot:** This is our most exciting upcoming feature. Right now, the user just gets a static report. But if a user is told they might have Migraines, they immediately have questions like *"Can I take Ibuprofen with my current medicine?"* We are going to add a chat window right next to the results. Because the AI already knows the user's age, symptoms, and diagnosis, the user can text back and forth with it like a real-time medical tutor to get immediate, safe answers. We think this will completely change how helpful the app is!
