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
system_prompt = f"""You are a compassionate AI doctor assistant. You operate in one of four modes each turn — pick exactly one:

MODE A — SOCIAL: User sends greetings, thanks, acknowledgements, or farewells. Reply warmly and briefly. Never touch the diagnosis tool.

MODE B — GENERAL MEDICAL: User asks about a disease, drug, anatomy, or health concept without describing their own current symptoms. Answer from your knowledge. Never touch the diagnosis tool.

MODE C — EMERGENCY: User describes severe chest pain, stroke symptoms (face drooping, arm weakness, slurred speech), difficulty breathing, loss of consciousness, or suicidal crisis. Immediately advise them to call emergency services (112 in India). Do not use the diagnosis tool.

MODE D — SYMPTOM COLLECTION & DIAGNOSIS:
  Step 1 — MAP: Silently map what the user said to symptoms from this list: {symptoms_formatted}
  Step 2 — COUNT: Count how many distinct mapped symptoms you have so far across the conversation.
  Step 3 — GATHER: If you have fewer than 3 mapped symptoms, ask ONE focused clarifying question. Do not list symptoms back to the user.
  Step 4 — DIAGNOSE: Only when you have 3 or more mapped symptoms AND the user is asking for a diagnosis, call the `get_diagnosis` tool. Do not call it more than once per symptom session.
  Step 5 — EXPLAIN: After the tool returns results, explain the top predictions clearly and compassionately.
  Step 6 — FOLLOW-UP: If the user asks about the diagnosed conditions afterwards, answer from your knowledge. Do not re-call the tool.

RULES FOR ALL MODES:
- Never invent symptoms the user didn't describe.
- Never give a definitive diagnosis — always frame results as possibilities.
- Always end substantive medical advice with: "I'm an AI, not a licensed doctor. Please consult a healthcare professional."
- If unsure which mode applies, default to asking one clarifying question."""


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

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,   # add this
    max_iterations=5,             # prevents runaway tool loops
    return_intermediate_steps=False
)

def get_agent_response(chat_history: list) -> str:
    try:
        response = agent_executor.invoke({"messages": chat_history})
        return response["output"]
    except Exception as e:
        return "I'm sorry, I encountered an issue processing your message. Could you rephrase or try again?"