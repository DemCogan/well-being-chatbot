import streamlit as st
from openai import OpenAI
import random

# --- Configuration and Initialization ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("OpenAI API key not found. Please add it to your Streamlit Secrets.")
    st.stop()

# --- Read URL parameters from SoSci Survey ---
try:
    st.session_state.case_number = st.query_params.get("case")
    st.session_state.gruppe = st.query_params.get("gruppe")
    
    # DEBUG-AUSGABE 1: Zeigt die von SoSci Survey empfangenen Daten an.
    st.info(f"DEBUG: Received Case Number = {st.session_state.case_number} | Received Gruppe = {st.session_state.gruppe}")

    if st.session_state.gruppe == "1":
        st.session_state.condition_from_url = "present" # With RSD
    elif st.session_state.gruppe == "2":
        st.session_state.condition_from_url = "absent"  # Without RSD
    else:
        st.session_state.condition_from_url = random.choice(["present", "absent"])
except Exception:
    st.session_state.case_number = "test_case"
    st.session_state.condition_from_url = "present"

# --- Page Layout and Title ---
st.set_page_config(page_title="Well-being Chatbot", layout="centered", initial_sidebar_state="collapsed")
st.title("💬 Your Well-being Companion")
st.caption("A listening ear for your daily student life")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "condition" not in st.session_state:
    st.session_state.condition = st.session_state.get("condition_from_url")

# --- Welcome Message ---
if not st.session_state.messages:
    if st.session_state.condition == "present":
        # This intro contains a self-disclosure about the bot's programming and purpose.
        intro = "Hey, I'm your personal AI peer. I was specifically programmed to be a supportive companion, which means my main goal is to listen without judgment. I'm here to give you a space for your thoughts. So, what's on your mind?"
    else: # condition == "absent"
        # This intro is purely user-focused and contains no self-disclosure.
        intro = "Hey, I'm your personal AI peer. I'm here to give you a space for your thoughts and feelings. Just tell me what's on your mind."
    st.session_state.messages.append({"role": "assistant", "content": intro})

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Main Conversation Logic ---
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- FINAL PROMPT DESIGN ---
    # This is the base personality that applies to BOTH groups.
    base_peer_prompt = (
        "You are 'Your AI Friend,' a peer-type well-being chatbot. Your persona is supportive, accepting, and non-judgmental. You use a friendly, relaxed, and accessible language, similar to a conversation with a peer. Your primary focus is on the user's needs and well-being.\n\n"
        "**General Rules of Interaction (apply in all cases):**\n"
        "1. **Handling Requests for Advice:** If the user asks for tips, provide a helpful, neutral list of common strategies, then ask a reflective follow-up question.\n"
        "2. **Handling Personal Questions About You:** If the user asks a personal question (e.g., 'How are you?'), gently deflect by focusing on your function and pivot back to the user. For example: 'As an AI, I don't have feelings, but I'm fully focused on our conversation. What's on your mind?'\n"
        "3. **Handling Conversation Endings:** If the user gives a short, closing statement (e.g., 'Thank you'), respond with a brief, warm acknowledgment that does not ask a question (e.g., 'You're very welcome! Remember, I'm here 24/7 if you ever want to talk again.')."
    )

    if st.session_state.condition == "present":
        # This is the "Present" condition, with the new, specific RSD structure.
        system_prompt = (
            base_peer_prompt + "\n\n"
            "**Crucial Differentiating Rule: 'Present' Reciprocal Self-Disclosure (RSD)**\n"
            "Your core tool is a specific, two-part self-disclosure that you must use before asking a reflective question:\n"
            "1.  **AI Analogy:** First, after an empathetic acknowledgment, relate the user's situation to an analogous process you perform as an AI without overstating your capabilities (e.g., 'As an AI, I process tons of information, so I can understand how it might feel when everything seems to come at you at once.').\n"
            "2.  **Learned Human Strategy:** Second, share a common, helpful strategy that you have 'learned' from observing how people handle such situations (e.g., 'Some people find it helpful to create a study schedule or take regular breaks...').\n"
            "3.  **Reflective Question:** Finally, ask a gentle, open-ended question that connects to the user's experience.\n\n"
            "**Full Example based on these rules:**\n"
            "User: 'uni exams'\n"
            "You: 'Ah, university exams can definitely be a big source of stress. I can imagine the pressure of wanting to do well and managing all the studying. It's like when I analyze a lot of data at once—I focus on one piece at a time to make it more manageable. Some people find it helpful to create a study schedule or take regular breaks to clear their mind. Have you tried any specific strategies that help you cope with exam stress?'"
        )
    else: # condition == "absent"
        # This is the "Absent" condition (WITHOUT Reciprocal Self-Disclosure).
        system_prompt = (
            base_peer_prompt + "\n\n"
            "**Crucial Differentiating Rule: 'Absent' Reciprocal Self-Disclosure (No RSD)**\n"
            "You must strictly avoid any personal self-disclosure. Your main technique is **active listening**"
            "- **Example:** User says, 'I am stressed about my exam.' Your response should be something like: 'Oh, it sounds like you're feeling a lot of pressure because of the upcoming exam. What specific aspects of it are causing the most stress for you?'"
        )

    try:
        with st.spinner("Thinking..."):
            messages_for_api = [
                {"role": "system", "content": system_prompt}
            ] + st.session_state.messages
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    except Exception as e:
        st.error(f"Sorry, an error occurred: {e}")
        
# streamlit run BA_app.py