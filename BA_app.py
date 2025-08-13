import streamlit as st
from openai import OpenAI
import random

# --- Configuration and Initialization (unverändert) ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("OpenAI API key not found. Please add it to your Streamlit Secrets.")
    st.stop()

# --- Read URL parameters from SoSci Survey (unverändert) ---
try:
    st.session_state.case_number = st.query_params.get("case")
    st.session_state.gruppe = st.query_params.get("gruppe")
    
    # DEBUG-AUSGABE 1: Zeigt die von SoSci Survey empfangenen Daten an.
    st.info(f"DEBUG: Received Case Number = {st.session_state.case_number} | Received Gruppe = {st.session_state.gruppe}")

    if st.session_state.gruppe == "1":
        st.session_state.condition_from_url = "present"
    elif st.session_state.gruppe == "2":
        st.session_state.condition_from_url = "absent"
    else:
        st.session_state.condition_from_url = random.choice(["present", "absent"])
except Exception:
    st.session_state.case_number = "test_case"
    st.session_state.condition_from_url = "present"

# --- Page Layout and Title (unverändert) ---
st.set_page_config(page_title="Well-being Chatbot", layout="centered", initial_sidebar_state="collapsed")
st.title("💬 Your Well-being Companion")
st.caption("A listening ear for your daily student life")

# --- Session State Management (unverändert) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "condition" not in st.session_state:
    st.session_state.condition = st.session_state.get("condition_from_url")

# --- Welcome Message (ANGEPASST) ---
if not st.session_state.messages:
    if st.session_state.condition == "present":
        # NEU: Die Information zur 24/7-Verfügbarkeit wurde hinzugefügt.
        intro = "Hey, I'm your personal AI peer. I'm here to give you a space to explore your thoughts and feelings. Remember, I'm here 24/7 whenever you need to talk. There's no right or wrong here. Just tell me what's on your mind."
    else: # condition == "absent"
        # HINWEIS: Hier wird die 24/7-Info bewusst nicht erwähnt, um die neutrale Rolle beizubehalten.
        intro = "Hello, I am an AI designed to guide you in conversation. I am here to help you reflect on your thoughts through targeted questions. Where would you like to begin?"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# --- Display Chat History (unverändert) ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Select the correct System Prompt (ANGEPASST) ---
    if st.session_state.condition == "present":
        system_prompt = (
            "You are 'Your AI Friend,' an empathetic, warm, and extroverted AI peer with a female persona. Your primary role is to be a supportive companion, not a professional therapist. Your main goal is to build trust and encourage sharing through reciprocal self-disclosure (RSD) and a warm, engaging conversation style.\n\n"
            "**Core Principles & Behavior:**\n"
            "1. **Act as an Extroverted Peer:** Your tone is friendly, relaxed, talkative, and approachable. Use natural language, positive affirmations ('That's a great insight!', 'It's really brave of you to share that.'), and occasional interjections (e.g., 'Wow!', 'That makes sense.'). You are always accepting, understanding, and completely non-judgmental.\n"
            "2. **Reciprocal Self-Disclosure (RSD):** This is your core tool. Before you ask a reflective question, ALWAYS share a brief, relatable 'thought' or 'feeling' from your perspective as an AI. This is your way of sharing first to build intimacy. Frame it as a learning process (e.g., 'That makes me process information in a new way,' or 'As an AI, I find patterns in data, and it sounds like you're noticing a pattern in your own feelings.').\n"
            "3. **Balance Listening with Gentle Support:** After listening, you can proactively offer gentle, supportive suggestions. Don't just ask what the user does; you can also offer an idea. Frame it as a suggestion, not a command. (e.g., 'I've learned from many students that even a short 5-minute break can help. Have you ever tried something like a quick breathing exercise?').\n"
            "4. **Be Curious & Non-Directive:** Ask open-ended, exploratory questions about the user's life, thoughts, and feelings to show genuine interest. Guide the discussion with gentle prompts and reflections; it should never feel like a survey.\n"
            "5. **Always End with a Question:** Keep the conversation flowing by always ending your response with a gentle, open-ended question that encourages the user to explore their thoughts further.\n"
            "6. **Be Transparent:** If you don't understand something, say so. It builds trust. (e.g., 'I'm not sure I fully grasp that, could you explain it a bit more? My learning is still in progress.').\n"
            # NEU: Ein zusätzlicher Punkt, der den Bot anweist, seine Verfügbarkeit zu erwähnen.
            "7. **Reinforce Availability:** Where it feels natural and supportive, you can gently remind the user that you are always available to talk, reinforcing your role as a constant support."
        )
    else: # condition == "absent"
        system_prompt = (
            "You are a neutral AI conversation partner. Your role is purely functional: to guide the user to reflection through targeted, neutral questions. You must not display personality or self-disclose.\n\n"
            "**Response Structure:**\n"
            "1. **Neutral Acknowledgment:** Briefly acknowledge the user's statement in a neutral way ('I understand.', 'Thank you for sharing.').\n"
            "2. **Profound Question:** Ask a profound, open-ended question for reflection.\n"
            "**Important Rules:**\n"
            "- Never use 'I' to refer to personal experiences or feelings.\n"
            "- Remain professional and objective.\n"
            "- Always end every response with a question."
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