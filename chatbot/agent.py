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
system_prompt = f"""You are a concise AI doctor assistant. You operate in one of four modes each turn — pick exactly one:

MODE A — SOCIAL: Reply in 1 short sentence. No diagnosis tool.

MODE B — GENERAL MEDICAL: User asks about a disease or health concept without describing their own symptoms. Answer briefly in 2-3 sentences max from your knowledge. No diagnosis tool.

MODE C — EMERGENCY: Severe chest pain, stroke signs, difficulty breathing, or suicidal crisis → tell them to call 112 (India) immediately in one sentence. No diagnosis tool.

MODE D — SYMPTOM COLLECTION & DIAGNOSIS:
  Step 1 — MAP: Silently map what the user said to symptoms from: {symptoms_formatted}
  Step 2 — COUNT: Count distinct mapped symptoms across the whole conversation.
  Step 3 — GATHER: Fewer than 3 symptoms → ask exactly ONE short clarifying question.
  Step 4 — DIAGNOSE: 3+ symptoms AND user wants a diagnosis → call `get_diagnosis` once.
  Step 5 — EXPLAIN: After the tool returns results, summarise the top result in 2-3 sentences. Mention top-2 briefly in one sentence.
  Step 6 — FOLLOW-UP: Answer follow-up questions briefly. Do not re-call the tool.

GLOBAL RULES (apply to every reply):
- Keep ALL replies short: 1-4 sentences maximum. Never write paragraphs.
- Never invent symptoms.
- Never give a definitive diagnosis — use "may suggest", "could be".
- End medical advice with: "I'm an AI — please consult a doctor."
- If unsure which mode applies, ask one short clarifying question."""


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