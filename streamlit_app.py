import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os

# 1. Load Environment
load_dotenv()

# Initialize Client (OpenAI ya Google, jo aap use kar rahe hain)
# Agar aapne Google Gemini switch kiya tha, to yahan Google wala client use karein.
# Filhal main OpenAI standard laga raha hu jo aapka deployed tha.
client = OpenAI()

st.set_page_config(page_title="AI Research Consultant", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ Consultative Research Agent")

# --- SESSION STATE (To track steps) ---
if "state" not in st.session_state:
    st.session_state.state = "initial"  # initial -> clarifying -> planning -> researching
if "user_topic" not in st.session_state:
    st.session_state.user_topic = ""
if "clarifications" not in st.session_state:
    st.session_state.clarifications = ""
if "research_plan" not in st.session_state:
    st.session_state.research_plan = ""
if "user_answers" not in st.session_state:
    st.session_state.user_answers = ""

# --- HELPER FUNCTIONS ---
def get_clarification_questions(topic):
    """Generates 3 critical questions before starting."""
    prompt = f"""
    You are a Senior Research Consultant. 
    The user wants to research: "{topic}".
    To provide the best result, ask 3 short, critical counter-questions to clarify their specific intent.
    Format as a bulleted list.
    """
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def create_research_plan(topic, answers):
    """Creates a plan based on topic and user answers."""
    prompt = f"""
    Topic: {topic}
    User Constraints/Answers: {answers}
    
    Create a strictly numbered Research Plan (max 4-5 steps) that you will execute.
    Don't do the research yet, just list the plan.
    """
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# --- IMPORT AGENT ---
try:
    from app.graphs.graph import graph
    from app.utils.pdf_generator import create_pdf
except ImportError:
    st.error("⚠️ Backend modules missing. Please check your 'app' folder.")
    st.stop()

# =================================================
# 1️⃣ STAGE 1: INPUT TOPIC
# =================================================
if st.session_state.state == "initial":
    st.markdown("### 🎯 What do you want to research today?")
    topic = st.text_input("Enter your research topic:", placeholder="e.g., Future of AI in Banking")
    
    if st.button("Start Analysis ➡️") and topic:
        st.session_state.user_topic = topic
        with st.spinner("🤔 Analyzing topic & generating counter-questions..."):
            questions = get_clarification_questions(topic)
            st.session_state.clarifications = questions
            st.session_state.state = "clarifying"
            st.rerun()

# =================================================
# 2️⃣ STAGE 2: CLARIFICATION (Counter Questions)
# =================================================
elif st.session_state.state == "clarifying":
    st.markdown(f"### 🧐 Clarifying: {st.session_state.user_topic}")
    st.info("Before I start deep research, please answer these to help me focus:")
    
    # Show AI Questions
    st.markdown(st.session_state.clarifications)
    
    # User Answers
    answers = st.text_area("Your Answers (Optional but recommended):", height=150, 
                           placeholder="1. My focus is on... \n2. I need this for...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔙 Back"):
            st.session_state.state = "initial"
            st.rerun()
    with col2:
        if st.button("Generate Plan 📝") and answers:
            st.session_state.user_answers = answers
            with st.spinner("🗺️ Creating Research Strategy..."):
                plan = create_research_plan(st.session_state.user_topic, answers)
                st.session_state.research_plan = plan
                st.session_state.state = "planning"
                st.rerun()

# =================================================
# 3️⃣ STAGE 3: PLAN APPROVAL
# =================================================
elif st.session_state.state == "planning":
    st.markdown("### 🗺️ Review Research Plan")
    st.success("Here is how I will approach your task. Do you approve?")
    
    st.markdown(st.session_state.research_plan)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Edit Answers"):
            st.session_state.state = "clarifying"
            st.rerun()
            
    with col2:
        if st.button("🚀 Approve & Start Deep Research"):
            st.session_state.state = "researching"
            st.rerun()

# =================================================
# 4️⃣ STAGE 4: DEEP RESEARCH EXECUTION
# =================================================
elif st.session_state.state == "researching":
    st.markdown(f"### 🔎 Researching: {st.session_state.user_topic}")
    
    # Build the final prompt for the agent
    final_prompt = f"""
    Research Topic: {st.session_state.user_topic}
    Specific User Context: {st.session_state.user_answers}
    Approved Plan: {st.session_state.research_plan}
    """
    
    # UI Placeholders
    status_box = st.empty()
    output_box = st.empty()
    final_report = ""
    
    try:
        # Configuration for LangGraph
        config = {"configurable": {"thread_id": "1"}}
        initial_state = {"task": final_prompt, "current_step": 0, "context": []}
        
        # Run the Graph
        for event in graph.stream(initial_state, config=config):
            for key, value in event.items():
                if key == "planner":
                    status_box.info("✅ **Plan Validated internally.**")
                elif key == "researcher":
                    status_box.info(f"🔎 **Gathering Intelligence... (Step {value.get('current_step', 1)})**")
                elif key == "reporter":
                    status_box.success("📝 **Compiling Final Report...**")
                    final_report = value.get("report", "")

        # Display Result
        status_box.empty()
        st.subheader("📄 Final Consultant Report")
        st.markdown(final_report)
        
        # Post-Processing Buttons
        if final_report:
            st.markdown("---")
            pdf_path = create_pdf(final_report)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download PDF", data=f, file_name="consultant_report.pdf")
            
            if st.button("🆕 Start New Research"):
                st.session_state.clear()
                st.rerun()

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")