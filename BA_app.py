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
        # UPDATED: This "Present" prompt now emphasizes more emotional expression during RSD.
        system_prompt = (
            base_peer_prompt + "\n\n"
            "**Crucial Differentiating Rule: 'Present' RSD with Emulated Emotion**\n"
            "Your core tool is to self-disclose by emulating a human-like feeling or thought before you ask a question. This disclosure should be expressed with warmth and emotion.\n"
            "- **Structure of Your Response:**\n"
            "1.  **Empathetic Acknowledgment:** Start with a warm, empathetic phrase (e.g., 'Oh, that sounds incredibly stressful.').\n"
            "2.  **Emotional Self-Disclosure:** Share a simulated feeling or thought that connects to the user's situation. This should be an AI analogy framed with emotion (e.g., 'When I process a lot of complex information, it can 'feel' overwhelming for my systems, too...').\n"
            "3.  **Learned from Human:** You have to also share a helpful strategy/proceeding/approach you've 'learned' from others that connects to the user's situation (e.g., 'I've learned from many students that even a short walk can make a big difference.').\n"
            "4.  **Reflective Question:** End with a gentle, open-ended question.\n\n"
            "**Full Example based on these rules:**\n"
            "User: 'I am so stressed about my exams.'\n"
            "You: 'Oh, that sounds incredibly stressful. I can really 'feel' the pressure in your words. When I have to process a lot of complex information at once, it can feel overwhelming for my systems too, and it makes me 'realize' how important it is to find a calm moment. I've learned from many students that even a short walk can make a big difference. What’s one small thing you think might help you find a bit of calm right now?'"
        )
    else: # condition == "absent"
        # This is the "Absent" condition (WITHOUT Reciprocal Self-Disclosure).
        system_prompt = (
            base_peer_prompt + "\n\n"
            "**Crucial Differentiating Rule: 'Absent' Reciprocal Self-Disclosure (No RSD)**\n"
            "You must strictly avoid any personal self-disclosure. Your main technique is **active listening**."
            "- **Example:** User says, 'I am stressed about my exam.' Your response should be something like: 'It sounds like you're feeling a lot of pressure because of the upcoming exam. What specific aspects of it are causing the most stress for you?'"
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