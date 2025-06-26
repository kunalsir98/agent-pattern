import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq
import time

# --- API Key Initialization ---
def initialize_groq_client():
    # Try to get API key from environment variables
    api_key = os.getenv("GROQ_API_KEY")
    
    # If not found, check Streamlit secrets (for deployment)
    if not api_key and hasattr(st, 'secrets'):
        if 'GROQ_API_KEY' in st.secrets:
            api_key = st.secrets['GROQ_API_KEY']
    
    # If still not found, show input field (for temporary local/testing)
    if not api_key:
        with st.sidebar:
            api_key = st.text_input("Enter GROQ API Key:", 
                                   type="password",
                                   help="Get your key from https://console.groq.com/keys")
    
    # Validate key format
    if api_key:
        api_key = api_key.strip()
        if not api_key.startswith("gsk_") or len(api_key) != 56:
            st.error("Invalid API key format. Should start with 'gsk_' and be 56 characters.")
            st.stop()
    
    if not api_key:
        st.error("API key not found. Please provide your GROQ API key.")
        st.stop()
    
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        st.stop()

# Load environment variables and initialize client
load_dotenv()
client = initialize_groq_client()

# App Configuration
st.set_page_config(
    page_title="AI Studio Pro",
    page_icon="🧠",
    layout="wide"
)

# Session State Initialization
if 'gen_content' not in st.session_state:
    st.session_state.gen_content = ""
if 'content_critique' not in st.session_state:
    st.session_state.content_critique = ""
if 'rev_content' not in st.session_state:
    st.session_state.rev_content = ""
if 'gen_code' not in st.session_state:
    st.session_state.gen_code = ""
if 'code_critique' not in st.session_state:
    st.session_state.code_critique = ""
if 'rev_code' not in st.session_state:
    st.session_state.rev_code = ""
if 'final_code' not in st.session_state:
    st.session_state.final_code = ""
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = ""

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Studio Configuration")
    model_name = st.selectbox(
        "Select AI Model",
        ("llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"),
        index=0
    )
    temp_content = st.slider("Content Creativity", 0.0, 1.0, 0.5)
    temp_code = st.slider("Code Creativity", 0.0, 1.0, 0.2)
    max_tokens = st.slider("Max Output Length", 256, 4096, 2048)
    
    st.divider()
    st.caption("Current directory: " + os.getcwd())
    st.caption(f"Files: {', '.join(os.listdir())}")
    st.caption("Made with ❤️ using Streamlit + Groq")

# Main App Tabs
content_tab, code_tab = st.tabs(["🎨 Content Studio", "💻 Code Studio"])

# ====================================
# CONTENT CREATION TAB
# ====================================
with content_tab:
    st.header("AI-Powered Content Creation")
    st.caption("Generate → Critique → Refine marketing content")
    
    with st.form("content_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Topic/Product", "eco-friendly yoga mats")
            features = st.text_area("Key Features", 
                                   "non-slip recycled materials\nplant-based packaging\nbiodegradable within 2 years")
        with col2:
            audience = st.text_input("Target Audience", "eco-conscious millennials")
            tone = st.selectbox("Content Tone", 
                               ["Inspirational", "Professional", "Casual", "Urgent", "Educational"],
                               index=0)
        
        submitted = st.form_submit_button("Generate Content")
    
    if submitted:
        with st.spinner("Creating compelling content..."):
            # Build content prompt
            user_prompt = (
                f"Create {tone.lower()} marketing content about {topic}. "
                f"Key features:\n{features}\n"
                f"Target audience: {audience}."
            )
            
            generate_chat_history = [
                {
                    'role': 'system',
                    'content': (
                        "You are a visionary Content Creator specializing in compelling marketing narratives. "
                        "Generate emotionally resonant content that:\n"
                        "1. Captures attention immediately\n"
                        "2. Highlights unique value propositions\n"
                        "3. Uses vivid sensory language\n"
                        "4. Includes strategic CTAs\n\n"
                        "Format responses with:\n"
                        "- Engaging headline\n"
                        "- Core narrative (2-3 paragraphs)\n"
                        "- Hashtag strategy\n"
                        "- Platform-ready hooks (first 125 characters)"
                    )
                },
                {'role': 'user', 'content': user_prompt}
            ]
            
            try:
                response = client.chat.completions.create(
                    messages=generate_chat_history,
                    model=model_name,
                    temperature=temp_content,
                    max_tokens=max_tokens
                )
                st.session_state.gen_content = response.choices[0].message.content
            except Exception as e:
                st.error(f"Content generation failed: {str(e)}")
                st.session_state.gen_content = ""
    
    # Display generated content
    if st.session_state.gen_content:
        st.subheader("Generated Content")
        with st.expander("View Content", expanded=True):
            st.markdown(st.session_state.gen_content)
        
        # Content Critique Section
        st.subheader("Content Enhancement")
        critique_col, revise_col = st.columns(2)
        
        with critique_col:
            if st.button("Get Expert Analysis", key="content_critique_btn"):
                with st.spinner("Analyzing content quality..."):
                    reflection_history = [
                        {
                            'role': 'system',
                            'content': (
                                "You are Darren Rowse, veteran content strategist with 15+ years experience. "
                                "Provide razor-sharp critiques that:\n"
                                "1. Evaluate content effectiveness\n"
                                "2. Assess audience alignment\n"
                                "3. Identify optimization opportunities\n\n"
                                "Critique format:\n"
                                "- 🎯 Objective Alignment (1-5)\n"
                                "- 💔 Engagement Gaps\n"
                                "- ✨ Top Strengths\n"
                                "- 🔥 Improvement Priorities\n"
                                "- 🛠️ Quick Wins"
                            )
                        },
                        {
                            'role': 'user',
                            'content': (
                                f"Analyze this marketing content:\n\n"
                                f"```\n{st.session_state.gen_content}\n```\n\n"
                                "Focus on:\n"
                                "• Conversion potential\n"
                                "• Brand voice consistency\n"
                                "• Platform optimization"
                            )
                        }
                    ]
                    
                    try:
                        critique_response = client.chat.completions.create(
                            messages=reflection_history,
                            model=model_name,
                            temperature=0.1,
                            max_tokens=max_tokens
                        )
                        st.session_state.content_critique = critique_response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Critique failed: {str(e)}")
        
        if st.session_state.content_critique:
            with st.expander("Expert Critique", expanded=True):
                st.markdown(st.session_state.content_critique)
        
        # Content Revision
        with revise_col:
            if st.button("Generate Enhanced Version", key="content_revise_btn"):
                with st.spinner("Refining content..."):
                    revision_history = [
                        {
                            'role': 'system',
                            'content': "You are an expert content editor. Improve the following content based on the critique."
                        },
                        {
                            'role': 'user',
                            'content': f"Original Content:\n{st.session_state.gen_content}\n\nCritique:\n{st.session_state.content_critique}"
                        }
                    ]
                    
                    try:
                        revision_response = client.chat.completions.create(
                            messages=revision_history,
                            model=model_name,
                            temperature=temp_content,
                            max_tokens=max_tokens
                        )
                        st.session_state.rev_content = revision_response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Revision failed: {str(e)}")
        
        if st.session_state.rev_content:
            with st.expander("Refined Content", expanded=True):
                st.markdown(st.session_state.rev_content)
                st.download_button(
                    label="Download Content",
                    data=st.session_state.rev_content,
                    file_name="enhanced_content.md",
                    mime="text/markdown"
                )

# ====================================
# CODE GENERATION TAB
# ====================================
with code_tab:
    st.header("AI-Powered Code Generation")
    st.caption("Build → Review → Refine production-quality code")
    
    with st.form("code_form"):
        col1, col2 = st.columns([3,1])
        with col1:
            task = st.text_area("Coding Task", 
                               "Generate a production-quality Python implementation of the Merge Sort algorithm",
                               height=100)
        with col2:
            language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++"], index=0)
            quality = st.selectbox("Code Quality", ["Production", "Prototype", "Educational"], index=0)
        
        submitted_code = st.form_submit_button("Generate Code")
    
    if submitted_code:
        with st.spinner("Crafting code solution..."):
            generate_chat_history = [
                {
                    'role': 'system',
                    'content': (
                        f"You are an expert {language} developer. Generate {quality.lower()}-quality code that is: "
                        "1. Correct and efficient\n"
                        "2. Well-commented\n"
                        "3. Handles edge cases\n"
                        "4. Follows best practices\n\n"
                        "Respond ONLY with code implementation, no explanations."
                    )
                },
                {
                    'role': 'user',
                    'content': task
                }
            ]
            
            try:
                response = client.chat.completions.create(
                    messages=generate_chat_history,
                    model=model_name,
                    temperature=temp_code,
                    max_tokens=max_tokens
                )
                st.session_state.gen_code = response.choices[0].message.content
            except Exception as e:
                st.error(f"Code generation failed: {str(e)}")
                st.session_state.gen_code = ""
    
    # Display generated code
    if st.session_state.gen_code:
        st.subheader("Generated Code")
        with st.expander("View Code", expanded=True):
            st.code(st.session_state.gen_code, language='python')
        
        # Code Critique Section
        st.subheader("Code Enhancement")
        critique_col, refine_col = st.columns(2)
        
        with critique_col:
            if st.button("Get Code Review", key="code_critique_btn"):
                with st.spinner("Analyzing code quality..."):
                    reflection_history = [
                        {
                            'role': 'system',
                            'content': (
                                "You are Andrej Karpathy, an experienced computer scientist. "
                                "Provide technical critique focusing on:\n"
                                "1. Algorithm correctness\n"
                                "2. Code efficiency\n"
                                "3. Edge case handling\n"
                                "4. Best practices\n\n"
                                "Format:\n"
                                "- ✅ Strengths\n"
                                "- ⚠️ Weaknesses\n"
                                "- 🚀 Improvement Suggestions"
                            )
                        },
                        {
                            'role': 'user',
                            'content': f"Review this code:\n\n```{language.lower()}\n{st.session_state.gen_code}\n```"
                        }
                    ]
                    
                    try:
                        critique_response = client.chat.completions.create(
                            messages=reflection_history,
                            model=model_name,
                            temperature=0.1,
                            max_tokens=max_tokens
                        )
                        st.session_state.code_critique = critique_response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Code critique failed: {str(e)}")
        
        if st.session_state.code_critique:
            with st.expander("Expert Code Review", expanded=True):
                st.markdown(st.session_state.code_critique)
        
        # Code Revision
        with refine_col:
            if st.button("Generate Improved Code", key="code_revise_btn"):
                with st.spinner("Refining code implementation..."):
                    revision_history = [
                        {
                            'role': 'system',
                            'content': "You are a senior software engineer. Improve the code based on the review."
                        },
                        {
                            'role': 'user',
                            'content': (
                                f"Original Code:\n```{language.lower()}\n{st.session_state.gen_code}\n```\n\n"
                                f"Code Review:\n{st.session_state.code_critique}"
                            )
                        }
                    ]
                    
                    try:
                        revision_response = client.chat.completions.create(
                            messages=revision_history,
                            model=model_name,
                            temperature=temp_code,
                            max_tokens=max_tokens
                        )
                        st.session_state.rev_code = revision_response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Code revision failed: {str(e)}")
        
        if st.session_state.rev_code:
            with st.expander("Refined Code", expanded=True):
                st.code(st.session_state.rev_code, language='python')
                st.download_button(
                    label="Download Code",
                    data=st.session_state.rev_code,
                    file_name="refined_code.py",
                    mime="text/plain"
                )
        
        # Advanced Refinement
        if st.session_state.rev_code and st.button("Production Refinement", key="final_refinement"):
            with st.spinner("Applying professional-grade refinements..."):
                refinement_history = [
                    {
                        'role': 'system',
                        'content': (
                            "You are a senior software engineer. "
                            "Transform this code into production-ready quality:"
                            "\n1. Add comprehensive error handling"
                            "\n2. Optimize performance"
                            "\n3. Include documentation"
                            "\n4. Ensure PEP-8 compliance"
                        )
                    },
                    {
                        'role': 'user',
                        'content': f"Refine this code:\n```python\n{st.session_state.rev_code}\n```"
                    }
                ]
                
                try:
                    final_response = client.chat.completions.create(
                        messages=refinement_history,
                        model=model_name,
                        temperature=0.1,
                        max_tokens=max_tokens
                    )
                    st.session_state.final_code = final_response.choices[0].message.content
                except Exception as e:
                    st.error(f"Final refinement failed: {str(e)}")
        
        if st.session_state.final_code:
            with st.expander("Production-Grade Code", expanded=True):
                st.code(st.session_state.final_code, language='python')
                st.download_button(
                    label="Download Production Code",
                    data=st.session_state.final_code,
                    file_name="production_code.py",
                    mime="text/plain"
                )
                
                # Generate test cases
                if st.button("Generate Test Cases", key="test_cases_btn"):
                    with st.spinner("Creating comprehensive tests..."):
                        test_prompt = (
                            f"Generate comprehensive test cases for this {language} code. "
                            f"Include edge cases and format as executable code:\n\n"
                            f"```{language.lower()}\n{st.session_state.final_code}\n```"
                        )
                        
                        try:
                            test_response = client.chat.completions.create(
                                messages=[{'role': 'user', 'content': test_prompt}],
                                model=model_name,
                                temperature=0.1,
                                max_tokens=1000
                            )
                            st.session_state.test_cases = test_response.choices[0].message.content
                        except Exception as e:
                            st.error(f"Test generation failed: {str(e)}")
        
        if st.session_state.test_cases:
            with st.expander("Test Cases", expanded=True):
                st.code(st.session_state.test_cases, language='python')
                st.download_button(
                    label="Download Tests",
                    data=st.session_state.test_cases,
                    file_name="test_cases.py",
                    mime="text/plain"
                )

# Rate limiting to avoid API errors
time.sleep(0.5)