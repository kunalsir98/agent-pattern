import streamlit as st
from dotenv import load_dotenv
import os
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# App Configuration
st.set_page_config(
    page_title="AI Content Studio",
    page_icon="✍️",
    layout="centered"
)

# Session State Initialization
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
if 'critique' not in st.session_state:
    st.session_state.critique = ""
if 'revised_content' not in st.session_state:
    st.session_state.revised_content = ""

# UI Elements
st.title("✨ AI-Powered Content Studio")
st.subheader("Generate → Critique → Refine")

with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox(
        "Select Model",
        ("llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"),
        index=0
    )
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.3)
    max_tokens = st.slider("Max Tokens", 512, 4096, 1024)

# Content Generation Section
with st.expander("🎯 Generate Marketing Content", expanded=True):
    with st.form("content_form"):
        topic = st.text_input("Topic/Product", "eco-friendly yoga mats")
        feature1 = st.text_input("Key Feature 1", "non-slip recycled materials")
        feature2 = st.text_input("Key Feature 2", "plant-based packaging")
        audience = st.text_input("Target Audience", "eco-conscious millennials")
        
        if st.form_submit_button("Generate Content"):
            with st.spinner("Creating compelling content..."):
                # Build prompt with user inputs
                user_prompt = (
                    f"Create captivating marketing content about {topic}. "
                    f"Key features: {feature1}, {feature2}. "
                    f"Target audience: {audience}."
                )
                
                generate_chat_history = [
                    {
                        'role': 'system',
                        'content': (
                            "You are a visionary Content Creator specializing in compelling marketing narratives. "
                            "Generate emotionally resonant content that:\n"
                            "1. Captures attention within 3 seconds\n"
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
                
                response = client.chat.completions.create(
                    messages=generate_chat_history,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                st.session_state.generated_content = response.choices[0].message.content

    if st.session_state.generated_content:
        st.subheader("Generated Content")
        st.markdown(st.session_state.generated_content)
        
        # Critique Section
        with st.expander("🔍 Get Expert Critique"):
            if st.button("Analyze Content Quality"):
                with st.spinner("Getting expert analysis..."):
                    reflection_history = [
                        {
                            'role': 'system',
                            'content': (
                                "You are Darren Rowse, veteran content strategist with 15+ years experience. "
                                "Provide razor-sharp critiques that:\n"
                                "1. Evaluate content effectiveness against marketing objectives\n"
                                "2. Assess emotional resonance and audience alignment\n"
                                "3. Identify structural weaknesses and optimization opportunities\n\n"
                                "Critique format:\n"
                                "- 🎯 Objective Alignment (1-5)\n"
                                "- 💔 Engagement Gaps\n"
                                "- ✨ Top Strengths\n"
                                "- 🔥 Improvement Priorities\n"
                                "- 🛠️ Quick Wins\n"
                                "- 📈 Strategic Recommendations"
                            )
                        },
                        {
                            'role': 'user',
                            'content': (
                                f"Perform expert content audit on this marketing content:\n\n"
                                f"```\n{st.session_state.generated_content}\n```\n\n"
                                "Key evaluation criteria:\n"
                                "• Conversion potential\n"
                                "• Brand voice consistency\n"
                                "• Platform-specific optimization"
                            )
                        }
                    ]
                    
                    critique_response = client.chat.completions.create(
                        messages=reflection_history,
                        model=model_name,
                        temperature=0.1,
                        max_tokens=max_tokens
                    )
                    
                    st.session_state.critique = critique_response.choices[0].message.content
        
        if st.session_state.critique:
            st.subheader("Expert Analysis")
            st.markdown(st.session_state.critique)
            
            # Revision Section
            with st.expander("🔄 Revise Content"):
                if st.button("Generate Improved Version"):
                    with st.spinner("Refining content..."):
                        revision_history = [
                            {
                                'role': 'system',
                                'content': "You are an expert content editor. Improve the following content based on the provided critique."
                            },
                            {
                                'role': 'user',
                                'content': f"Original Content:\n{st.session_state.generated_content}\n\nCritique:\n{st.session_state.critique}"
                            }
                        ]
                        
                        revision_response = client.chat.completions.create(
                            messages=revision_history,
                            model=model_name,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        st.session_state.revised_content = revision_response.choices[0].message.content
        
        if st.session_state.revised_content:
            st.subheader("Refined Content")
            st.markdown(st.session_state.revised_content)
            st.download_button(
                label="Download Revised Content",
                data=st.session_state.revised_content,
                file_name="refined_content.md",
                mime="text/markdown"
            )

# Instructions
st.sidebar.markdown("""
**How to Use:**
1. Enter content parameters
2. Generate initial content
3. Get expert critique
4. Refine based on feedback
5. Download final version

**Pro Tips:**
- Increase creativity for more experimental content
- Use lower temperature for factual accuracy
- For long-form content, increase max tokens
""")