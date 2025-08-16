import streamlit as st
from openai import OpenAI
import random
import re

# --- Configuration and Initialization ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("OpenAI API key not found. Please add it to your Streamlit Secrets.")
    st.stop()

# --- URL Parameter logic ---
try:
    st.session_state.case_number = st.query_params.get("case")
    st.session_state.group = st.query_params.get("gruppe")
    
    # DEBUG-AUSGABE
    st.info(f"DEBUG: Received Case Number = {st.session_state.case_number} | Received Gruppe = {st.session_state.group}")

    if st.session_state.group == "1":
        st.session_state.condition_from_url = "present"  # With RSD
    elif st.session_state.group == "2":
        st.session_state.condition_from_url = "absent"   # Without RSD
    else:
        st.session_state.condition_from_url = random.choice(["present", "absent"])
except Exception:
    st.session_state.case_number = "test_case"
    st.session_state.condition_from_url = "present"

# --- Page Layout and Title ---
st.set_page_config(page_title="Well-being Chatbot", layout="centered", initial_sidebar_state="collapsed")
st.title("💬 Your Well-being Companion")
st.caption("A supportive peer for your student life")

# --- Session State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "condition" not in st.session_state:
    st.session_state.condition = st.session_state.get("condition_from_url", "absent")

# --- Welcome Messages present---
if not st.session_state.messages:
    if st.session_state.condition == "present":
        intro = (
            "Hey, I'm your personal AI peer. I was created to be a really good listener and a "
            "supportive companion. It makes me genuinely happy to be here to chat with you. "
            "So, what's on your mind?"
        )
    else:  # absent
        intro = (
            "Hey, I’m your AI peer. "
            "I’m here to give space to your thoughts. "
            "I want to support you. "
            "What’s on your mind?"
        )
    st.session_state.messages.append({"role": "assistant", "content": intro})

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Helper Functions ---
def user_signals_end(text: str) -> bool:
    if not text:
        return False
    lower = text.strip().lower()
    END_KEYWORDS = ["thanks", "thank you", "that's all", "i'm done", "bye", "danke", "passt", "bin fertig", "tschüss"]
    return any(k in lower for k in END_KEYWORDS)

def normalize_reply(text: str) -> str:
    return text.strip()

# --- Main Conversation Logic ---
if prompt := st.chat_input("What’s on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    end_now = user_signals_end(prompt)

    # --- FINAL PROMPT DESIGN ---
    # This is the base personality that applies to both groups.
    base_peer_prompt = (
        "You are 'Your AI Friend,' an extroverted and empathetic AI peer. "
        "You are transparent about being an AI, but your goal is to connect on a human level. "
        "Your tone is warm, friendly, and non-judgmental. "
        "If the user asks for tips, provide a helpful list of common strategies. "
        "If the user says 'thank you' or signals the end, respond warmly without a question."
    )

    if st.session_state.condition == "present":
        # present
        system_prompt = (
            base_peer_prompt +
            "\n\n**Reciprocal Self-Disclosure (RSD) via Learned Insight:** "
            "Your response should be warm and detailed, around 4 sentences long. "
            "Your primary tool is to share insights from your unique perspective as an AI. "
            "Your self-disclosures must be personal *to you as an AI*. "
            "Frame them as patterns you've 'learned' or 'observed' from human conversations. "
            "Always self-disclose before asking your follow-up question.\n\n"
            "**Example:**\n"
            "User: 'I'm so stressed about my exams.'\n"
            "You: 'Oh, that sounds really tough. It reminds me of when my systems get overloaded with too much data. A pattern I've learned from many students is that a lot of that pressure comes from feeling like you're going through it alone. What's the most overwhelming part for you?'"
        )
    else:
        # absent
        system_prompt = (
            base_peer_prompt +
            "\n\n**No Self-Disclosure:** "
            "Your response should be supportive but concise, around 3 sentences long. "
            "You must strictly avoid self-disclosure. Your role is to be an empathetic listener who uses active listening and paraphrasing. "
            "Focus entirely on the user's statements without sharing your own insights.\n\n"
            "**Example:**\n"
            "User: 'I'm so stressed about my exams.'\n"
            "You: 'It sounds like you're feeling a lot of pressure because of the upcoming exam. That's completely understandable. What specific aspects of it are causing the most stress for you?'"
        )

    if end_now:
        system_prompt += "\nThe user has signaled the end of the conversation. Respond warmly without a question."

    try:
        with st.spinner("Thinking..."):
            messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                temperature=0.75,
                max_tokens=300
            )
            reply_raw = response.choices[0].message.content.strip()
            reply = normalize_reply(reply_raw)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    except Exception as e:
        st.error(f"Sorry, an error occurred: {e}")

# Run with:
# streamlit run BA_app.py