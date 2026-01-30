import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import time  # <--- WAPAS ADD KIYA (Streaming ke liye)

# 1. Load Environment
load_dotenv()
client = OpenAI()

st.set_page_config(page_title="AI Research Consultant", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ Consultative Research Agent")

# --- SESSION STATE ---
if "state" not in st.session_state:
    st.session_state.state = "initial"
if "user_topic" not in st.session_state:
    st.session_state.user_topic = ""
if "clarifications" not in st.session_state:
    st.session_state.clarifications = ""
if "research_plan" not in st.session_state:
    st.session_state.research_plan = ""
if "user_answers" not in st.session_state:
    st.session_state.user_answers = ""

# --- HELPER FUNCTIONS ---

# 1. Streaming Function (WAPAS AAGAYA!) 🌊
def stream_text(text):
    """Simulates typing effect for the report."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

def get_clarification_questions(topic):
    prompt = f"""
    You are a Senior Research Consultant. 
    The user wants to research: "{topic}".
    Ask 3 critical questions to clarify their intent.
    Format as a bulleted list.
    """
    completion = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def create_research_plan(topic, answers):
    prompt = f"""
    Topic: {topic}
    User Constraints: {answers}
    Create a strictly numbered Research Plan (max 5 steps).
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
    st.error("⚠️ Backend modules missing.")
    st.stop()

# =================================================
# STAGE 1: INPUT
# =================================================
if st.session_state.state == "initial":
    st.markdown("### 🎯 What do you want to research?")
    topic = st.text_input("Enter topic:", placeholder="e.g., AI in Banking")
    
    if st.button("Start Analysis ➡️") and topic:
        st.session_state.user_topic = topic
        with st.spinner("🤔 Generating counter-questions..."):
            questions = get_clarification_questions(topic)
            st.session_state.clarifications = questions
            st.session_state.state = "clarifying"
            st.rerun()

# =================================================
# STAGE 2: CLARIFICATION
# =================================================
elif st.session_state.state == "clarifying":
    st.markdown(f"### 🧐 Clarifying: {st.session_state.user_topic}")
    st.info("Please answer these to help me focus:")
    st.markdown(st.session_state.clarifications)
    
    answers = st.text_area("Your Answers:", height=150)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔙 Back"):
            st.session_state.state = "initial"
            st.rerun()
    with col2:
        if st.button("Generate Plan 📝") and answers:
            st.session_state.user_answers = answers
            with st.spinner("🗺️ Creating Strategy..."):
                plan = create_research_plan(st.session_state.user_topic, answers)
                st.session_state.research_plan = plan
                st.session_state.state = "planning"
                st.rerun()

# =================================================
# STAGE 3: PLAN APPROVAL
# =================================================
elif st.session_state.state == "planning":
    st.markdown("### 🗺️ Review Research Plan")
    st.success("Do you approve this plan?")
    st.markdown(st.session_state.research_plan)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Edit Answers"):
            st.session_state.state = "clarifying"
            st.rerun()
    with col2:
        if st.button("🚀 Approve & Start"):
            st.session_state.state = "researching"
            st.rerun()

# =================================================
# STAGE 4: EXECUTION (STREAMING ADDED HERE) 🌊
# =================================================
elif st.session_state.state == "researching":
    st.markdown(f"### 🔎 Researching: {st.session_state.user_topic}")
    
    final_prompt = f"""
    Topic: {st.session_state.user_topic}
    Context: {st.session_state.user_answers}
    Plan: {st.session_state.research_plan}
    """
    
    status_box = st.empty()
    output_box = st.empty()
    final_report = ""
    
    try:
        config = {"configurable": {"thread_id": "1"}}
        initial_state = {"task": final_prompt, "current_step": 0, "context": []}
        
        for event in graph.stream(initial_state, config=config):
            for key, value in event.items():
                if key == "planner":
                    status_box.info("✅ **Plan Validated.**")
                elif key == "researcher":
                    status_box.info(f"🔎 **Gathering Intelligence... (Step {value.get('current_step', 1)})**")
                elif key == "reporter":
                    status_box.success("📝 **Writing Report...**")
                    final_report = value.get("report", "")

        status_box.empty()
        
        # --- ✨ MAGIC: STREAMING EFFECT ---
        st.subheader("📄 Final Consultant Report")
        if final_report:
            # Ye line text ko type hote hue dikhayegi
            st.write_stream(stream_text(final_report))
        
        # Post-Processing
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