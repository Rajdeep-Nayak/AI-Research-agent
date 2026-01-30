from dotenv import load_dotenv
load_dotenv() # Load API key

from app.agents.planner import planner

# Test prompt
response = planner.invoke({"input": "Research the impact of Quantum Computing on Cybersecurity."})

print("Generated Plan:")
for i, step in enumerate(response.steps):
    print(f"{i+1}. {step}")