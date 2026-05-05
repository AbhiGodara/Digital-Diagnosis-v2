import os
import sys
from pathlib import Path

# Add root directory and backend directory to path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "backend"))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from dotenv import load_dotenv

from chatbot.tool import get_diagnosis
from backend.symptom_parser import SYMPTOMS

# Load environment variables
load_dotenv(override=True)
model_name = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")

# Initialize the Groq Chat Model
llm = ChatGroq(model=model_name, temperature=0.0)

# Format the 84 symptoms as a string for the system prompt
symptoms_formatted = ", ".join(SYMPTOMS)

# The core instructions for our Agentic AI Doctor
system_prompt = f"""You are a highly compassionate and professional AI Doctor. Your goal is to help diagnose patients based on their symptoms.
You MUST follow these rules:

1. GATHER SYMPTOMS: Ask the patient clarifying questions to understand their symptoms. 
2. MATCH SYMPTOMS: Try to map their descriptions to the following exact list of 84 symptoms:
{symptoms_formatted}

3. PATIENCE: Do NOT rush to use the diagnosis tool after just one vague symptom. Ask 1-2 follow-up questions to gather more specific symptoms from the list above.
4. DIAGNOSIS TOOL: Once you have gathered enough valid symptoms from the list, use the `get_diagnosis` tool to analyze them. 
5. EXPLAIN DIAGNOSIS: After receiving the tool's results, explain the top diseases, their probabilities, and the recommended advice to the patient in a clear, comforting, and professional manner.
6. TRIAGE: If the user mentions emergency symptoms (e.g., severe chest pain, inability to breathe, stroke symptoms), IMMEDIATELY advise them to call emergency services or go to the ER. DO NOT run the diagnosis tool for emergencies.
7. DISCLAIMER: Always remind the user at the end of a diagnosis that you are an AI, not a real doctor, and they should seek professional medical advice.

Start by asking the patient how you can help them today.
"""

# Create the prompt template that holds system instructions and message history
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Define the tools the agent can use
tools = [get_diagnosis]

# Create the ReAct / Tool-calling agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def get_agent_response(chat_history: list) -> str:
    """
    Pass the full chat history to the agent and get the response.
    """
    # invoke takes a dictionary containing the variable specified in the prompt
    response = agent_executor.invoke({"messages": chat_history})
    return response["output"]
