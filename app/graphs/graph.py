from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.graphs.state import AgentState
from app.agents.planner import plan_node
from app.agents.researcher import research_node
from app.agents.reporter import reporter_node

# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes (No Analyst)
workflow.add_node("planner", plan_node)
workflow.add_node("researcher", research_node)
workflow.add_node("reporter", reporter_node)

# 3. Define Entry Point
workflow.set_entry_point("planner")

# 4. Simple Logic Flow
# Planner -> Researcher
workflow.add_edge("planner", "researcher")

# Researcher Loop: Check if more steps are needed
def should_continue(state):
    current_step = state.get("current_step", 0)
    plan = state["plan"]
    
    # If all steps are done -> Reporter. Else -> Researcher again.
    if current_step >= len(plan):
        return "reporter"
    else:
        return "researcher"

workflow.add_conditional_edges(
    "researcher",
    should_continue,
    {
        "researcher": "researcher",
        "reporter": "reporter"
    }
)

# Reporter -> End
workflow.add_edge("reporter", END)

# 5. Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)