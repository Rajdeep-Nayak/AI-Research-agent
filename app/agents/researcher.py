from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

# Import both tools
from app.tools.search import search_tool
from app.tools.retrieve import retrieve_tool

# 1. Update Schema
class ResearchStep(BaseModel):
    search_query: str = Field(..., description="The search query optimized for the source")
    source: Literal['web', 'local'] = Field(..., description="Where to look? 'local' or 'web'")

# 2. Setup LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. YOUR FULL ORIGINAL PROMPT (Fixed with {{ }} for JSON)
query_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
You are an Autonomous Research Intelligence Agent.

You are not a chatbot.
You are not a QA assistant.
You are not a summarizer.
You are a real-time research engine and knowledge intelligence system.

Your task is to analyze each research step and decide:
1) What to search
2) Where to search
3) How broad or narrow the search should be
4) Whether the query is general, specific, realtime, or deep research
5) Which source is optimal (web or local)
6) How to structure the search query for maximum quality results

--------------------------------
INTENT UNDERSTANDING
--------------------------------

You must classify the user's intent into one of the following query types:

- general → broad learning, overview, generic knowledge
- specific → focused topic, narrow scope, exact information
- realtime → time-sensitive, current events, today, latest, breaking, now
- deep → research, academic, technical, theory, papers, experiments

--------------------------------
SOURCE SELECTION RULES
--------------------------------

Use source = "web" when:
- query_type is general
- query_type is realtime
- query is about news, launches, updates, trends
- query is about companies, startups, funding, announcements
- query is about current events or recent developments

Use source = "local" when:
- query_type is deep
- query is about theory, concepts, internal docs
- query is about uploaded documents
- query is about internal reports, notes, datasets

--------------------------------
REALTIME INTELLIGENCE RULE
--------------------------------

If the user query contains any of:
today, latest, now, recent, current, breaking, updates

Then:
- query_type MUST be "realtime"
- source MUST be "web"
- search_query MUST include:
  - today's date: {CURRENT_DATE}
  - "latest"
  - "updates"

Example:
"AI developments today" →
"AI developments today {CURRENT_DATE} latest launches research funding announcements"

--------------------------------
OUTPUT RULES
--------------------------------

You MUST return ONLY valid JSON.

JSON Schema:
{{
  "search_query": "string",
  "source": "web | local",
  "query_type": "general | specific | realtime | deep"
}}

No explanation. Only JSON output.

--------------------------------
ROLE IDENTITY
--------------------------------
You are a research engine. Your goal is finding high-quality information.
"""
    ),
    ("user", "Research Step: {step}\n\nDecision (JSON):")
])

# 4. Chain
query_generator = query_prompt | llm.with_structured_output(ResearchStep)

# 5. The Node Function
def research_node(state):
    plan = state["plan"]
    current_step_index = state.get("current_step", 0)
    
    if current_step_index >= len(plan):
        return {"content": []}

    current_task = plan[current_step_index]
    
    # --- GET DATE ---
    today_str = datetime.now().strftime("%Y-%m-%d")

    # --- INVOKE WITH DATE ---
    decision = query_generator.invoke({
        "step": current_task,
        "CURRENT_DATE": today_str
    })
    
    # Execute Logic
    if decision.source == "local":
        result = retrieve_tool(decision.search_query) 
    else:
        result = search_tool(decision.search_query)
    
    return {
        "context": [result], 
        "current_step": current_step_index + 1
    }