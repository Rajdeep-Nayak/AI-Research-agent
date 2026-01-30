from dotenv import load_dotenv
import os

# 1. Load environment variables from .env file
load_dotenv() 

# Check if key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print(" ERROR: OPENAI_API_KEY is missing! Check your .env file.")
    exit(1)

# 2. Import the graph
from app.graphs.graph import graph

def run_research_agent(topic: str):
    print(f"🚀 Starting research on: {topic}")
    
    initial_state = {"task": topic, "current_step": 0, "context": []}
    
    try:
        for event in graph.stream(initial_state):
            for key, value in event.items():
                print(f"✅ Finished Node: {key}")
                if "report" in value:
                    print("\n\n🔥 FINAL REPORT 🔥\n")
                    print(value["report"])
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == "__main__":
    user_topic = input("📝 Enter a research topic: ")
    run_research_agent(user_topic)