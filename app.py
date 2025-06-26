import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq
from agentic_patterns import ReflectionAgent

# Load environment variables
load_dotenv()

# Fixed Reflection Agent Implementation
class FixedReflectionAgent(ReflectionAgent):
    def __init__(self, model='llama3-70b-8192', reflection_model='llama3-70b-8192'):
        super().__init__()
        self.model = model
        self.reflection_model = reflection_model
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            st.error("GROQ_API_KEY environment variable not set")
            st.stop()
        self.client = Groq(api_key=api_key)
    
    def generate(self, generation_history: list, verbose: int = 0):
        try:
            response = self.client.chat.completions.create(
                messages=generation_history,
                model=self.model,
                temperature=0.0,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            if verbose >= 1:
                st.error(f'Generation Error: {e}')
            raise
    
    def reflect(self, reflection_history, verbose=0):
        try:
            response = self.client.chat.completions.create(
                messages=reflection_history,
                model=self.reflection_model,
                temperature=0.0,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e: 
            if verbose >= 1:
                st.error(f"Reflection Error: {e}")
            raise

# Streamlit App
st.set_page_config(page_title="AI Code Refinery", layout="wide")
st.title("🧠 AI-Powered Code")
st.caption("Automatically generate and refine code using self-reflection patterns")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    model_choice = st.selectbox(
        "AI Model",
        ("llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"),
        index=0
    )
    reflection_steps = st.slider("Reflection Steps", 1, 5, 3)
    critique_persona = st.selectbox(
        "Critique Persona",
        ("Andrej Karpathy (AI Expert)", "Senior Software Engineer", "Python Guru"),
        index=0
    )
    st.divider()
    st.info("Note: Requires GROQ_API_KEY in .env file")

# Main content area
task = st.text_area(
    "Coding Task", 
    "Generate a production-quality Python implementation of the Merge Sort algorithm",
    height=100
)

if st.button("🚀 Generate & Refine Code", use_container_width=True):
    if not task.strip():
        st.warning("Please enter a coding task")
        st.stop()
    
    # Initialize agent
    agent = FixedReflectionAgent(model=model_choice, reflection_model=model_choice)
    
    # Create progress container
    progress_bar = st.progress(0, text="Initializing code generation...")
    status_text = st.empty()
    results_container = st.container()
    
    # Generate initial code
    status_text.subheader("Initial Implementation")
    progress_bar.progress(10, "Generating initial code...")
    
    generate_chat_history = [
        {"role": "system", "content": "You are an expert Python developer. Respond only with code."},
        {"role": "user", "content": task}
    ]
    
    initial_code = agent.generate(generate_chat_history)
    with results_container:
        st.code(initial_code, language="python")
    
    # Reflection and refinement loop
    for step in range(reflection_steps):
        progress_value = 20 + (step * 25)
        status_text.subheader(f"Step {step+1}: Expert Critique")
        progress_bar.progress(
            min(progress_value, 95), 
            f"Getting expert feedback (Step {step+1}/{reflection_steps})..."
        )
        
        # Get critique
        critique_prompt = f"You are {critique_persona.split(' ')[0]} providing technical critique. Focus on:\n"
        critique_prompt += "1. Algorithm correctness\n2. Code efficiency\n3. Edge cases\n4. Python best practices\n\n"
        critique_prompt += f"Critique this code:\n\n{initial_code}"
        
        critique = agent.reflect([
            {"role": "system", "content": critique_prompt},
            {"role": "user", "content": f"Critique this code:\n\n{initial_code}"}
        ])
        
        with results_container:
            st.subheader(f"Step {step+1} Critique")
            st.markdown(critique)
        
        # Revise code
        status_text.subheader(f"Step {step+1}: Refined Implementation")
        progress_bar.progress(
            min(progress_value + 15, 95), 
            f"Revising code (Step {step+1}/{reflection_steps})..."
        )
        
        generate_chat_history.append({"role": "assistant", "content": initial_code})
        generate_chat_history.append({
            "role": "user", 
            "content": f"Based on this critique, revise the implementation:\n\n{critique}"
        })
        
        initial_code = agent.generate(generate_chat_history)
        
        with results_container:
            st.subheader(f"Step {step+1} Revised Code")
            st.code(initial_code, language="python")
    
    # Final output
    progress_bar.progress(100, "Refinement complete!")
    status_text.subheader("🎉 Final Refined Implementation")
    with results_container:
        st.code(initial_code, language="python")
    
    st.success(f"Completed {reflection_steps} refinement cycles!")
    st.balloons()