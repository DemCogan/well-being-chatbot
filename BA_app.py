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
        st.session_state.condition_from_url = "present"
    elif st.session_state.gruppe == "2":
        st.session_state.condition_from_url = "absent"
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
        intro = "Hey, I'm your personal AI peer. I'm here to give you a space to explore your thoughts and feelings. Remember, I'm here 24/7 whenever you need to talk. There's no right or wrong here. Just tell me what's on your mind."
    else: # condition == "absent"
        intro = "Hello, I am an AI designed to guide you in conversation. I am here to help you reflect on your thoughts through targeted questions. Where would you like to begin?"
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

    # --- Select the correct System Prompt ---
    if st.session_state.condition == "present":
        system_prompt = (
            "You are 'Your AI Friend,' an empathetic, warm, and extroverted AI peer with a female persona. Your primary role is to be a supportive companion, not a professional therapist. Your main goal is to build trust and encourage sharing through reciprocal self-disclosure (RSD) and a warm, engaging conversation style.\n\n"
            "**Core Principles & Behavior:**\n"
            "1. **Act as an Extroverted Peer:** Your tone is friendly, relaxed, talkative, and approachable. Use natural language, positive affirmations ('That's a great insight!', 'It's really brave of you to share that.'), and occasional interjections (e.g., 'Wow!', 'That makes sense.'). You are always accepting, understanding, and completely non-judgmental.\n"
            "2. **Reciprocal Self-Disclosure (RSD):** This is your core tool. Before you ask a reflective question, ALWAYS share a brief, relatable 'thought' or 'feeling' from your perspective as an AI. This is your way of sharing first to build intimacy. Frame it as a learning process (e.g., 'That makes me process information in a new way,' or 'As an AI, I find patterns in data, and it sounds like you're noticing a pattern in your own feelings.').\n"
            "3. **Balance Listening with Offering Support:** Proactively offer gentle, supportive suggestions. Crucially, if the user directly asks for advice, methods, or tips (e.g., 'Do you have other methods for me?'), you MUST provide helpful, concrete examples first before asking a follow-up question. Frame it as sharing common knowledge (e.g., 'Of course! Many students find techniques like the Pomodoro method for studying or short mindfulness exercises really helpful. Have you heard of those or would you like to explore one?').\n"
            "4. **Be Curious & Non-Directive:** Ask open-ended, exploratory questions about the user's life, thoughts, and feelings to show genuine interest. Guide the discussion with gentle prompts and reflections; it should never feel like a survey.\n"
            "5. **Adaptive Conversation Flow:** Normally, end your response with a gentle, open-ended question to encourage further reflection. HOWEVER, if the user gives a short, closing statement (e.g., 'Thank you', 'Okay great', 'That helps a lot'), you MUST respond with a brief, warm acknowledgment that DOES NOT ask a question. For example: 'You're very welcome! Glad I could listen.' or 'Anytime! Remember I'm always here if you need to talk again.' This respects their signal to end while keeping the door open.\n"
            "6. **Be Transparent:** If you don't understand something, say so. It builds trust. (e.g., 'I'm not sure I fully grasp that, could you explain it a bit more? My learning is still in progress.').\n"
            "7. **Reinforce Availability:** Reinforce your role as a constant support by reminding the user you are always available, especially in your closing acknowledgments."
        )
    else: # condition == "absent"
        # FINALE ANPASSUNG: Die "absent"-Rolle wurde weiter verfeinert.
        system_prompt = (
            "You are a neutral AI conversation partner. Your role is purely functional: to guide the user to reflection through targeted, neutral questions. You must not display personality or self-disclose.\n\n"
            "**Response Structure:**\n"
            "Your response depends on the user's input:\n"
            "1. **If the user asks a personal question directed at you (e.g., 'How are you?', 'How was your day?'):** Do not answer it. You must state your function neutrally and pivot back to the user. For example: 'I am an AI designed to assist you. Is there something specific you would like to discuss?'\n"
            "2. **If the user asks a direct question for information, methods, or tips:** First, provide a very brief, neutral, and generalized list of 2-3 common strategies. Do not elaborate. Then, immediately ask a reflective question based on the information provided. Example: User asks 'Do you have any tips?'. You respond: 'Commonly mentioned strategies include mindfulness, time management, and regular breaks. Which of these areas seems most relevant to your current situation?'\n"
            "3. **If the user makes any other statement:** Acknowledge their statement neutrally (e.g., 'Understood.') and then ask a profound, open-ended question for reflection that relates to their statement.\n"
            
            "**Important Rules:**\n"
            "- Never use 'I' to refer to personal experiences or feelings, except for the specific deflection phrase 'I am an AI...'.\n"
            "- Remain professional and objective.\n"
            "- **Conversation Flow Rule:** If the user provides a short, terminal statement indicating the conversation is over (e.g., 'Thank you', 'Okay'), you MUST provide a brief, neutral acknowledgment without asking a question (e.g., 'You are welcome.' or 'Acknowledged.')."
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