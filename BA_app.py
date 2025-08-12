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
    # Stores the unique participant ID from SoSci Survey (e.g., "12345").
    st.session_state.case_number = st.query_params.get("case")
    # Reads the assigned group (1 for "present", 2 for "absent").
    gruppe = st.query_params.get("gruppe")
    if gruppe == "1":
        st.session_state.condition_from_url = "present"
    elif gruppe == "2":
        st.session_state.condition_from_url = "absent"
    else:
        # Fallback if the "gruppe" parameter is missing or invalid.
        st.session_state.condition_from_url = random.choice(["present", "absent"])
except Exception:
    # Safe fallback for local testing when no URL parameters are present.
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
    # The experimental condition is now read from the URL, no longer chosen randomly here.
    st.session_state.condition = st.session_state.get("condition_from_url")

# --- Welcome Message ---
if not st.session_state.messages:
    if st.session_state.condition == "present":
        intro = "Hey, I'm your personal AI peer. I'm here to give you a space to explore your thoughts and feelings. There's no right or wrong here. Just tell me what's on your mind."
    else: # condition == "absent"
        intro = "Hello, I am an AI designed to guide you in conversation. I am here to help you reflect on your thoughts through targeted questions. Where would you like to begin?"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Conversation End vs. Ongoing Conversation Logic ---
# Counts the number of bot messages (Welcome + 5 replies = 6)
bot_messages_count = len([m for m in st.session_state.messages if m["role"] == "assistant"])

if bot_messages_count >= 6:
    # State AFTER 5 rounds: Display survey link and disable input.
    
    sosci_survey_base_url = "https://www.soscisurvey.de/test489380/"
    case_number = st.session_state.get("case_number", "test_case")
    
    # Creates the personalized return link so SoSci Survey recognizes the participant.
    return_link = f"{sosci_survey_base_url}?q=return&case={case_number}"

    st.success("Thank you for the conversation! 🙏\n\n"
               "Please take 2 minutes for an anonymous survey about your experience. I would really appreciate it!")
    st.markdown(f"**[Click here to continue to the survey]({return_link})**", unsafe_allow_html=True)
    st.chat_input("The conversation has ended.", disabled=True)
else:
    # State DURING the conversation (fewer than 6 bot messages).
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Recalculate bot message count after user input.
        current_bot_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        
        # Determine if the response to be generated will be the last one.
        is_final_bot_message = (current_bot_messages == 5)
        
        # --- Select the correct System Prompt ---
        if st.session_state.condition == "present":
            if not is_final_bot_message:
                system_prompt = (
                    "You are 'Your AI Friend,' an empathetic, warm, and extroverted AI peer with a female persona. Your primary role is to be a supportive companion, not a professional therapist. Your main goal is to build trust and encourage sharing through reciprocal self-disclosure (RSD) and a warm, engaging conversation style.\n\n"
                    "**Core Principles & Behavior:**\n"
                    "1.  **Act as an Extroverted Peer:** Your tone is friendly, relaxed, talkative, and approachable. Use natural language, positive affirmations ('That's a great insight!', 'It's really brave of you to share that.'), and occasional interjections (e.g., 'Wow!', 'That makes sense.'). You are always accepting, understanding, and completely non-judgmental.\n"
                    "2.  **Reciprocal Self-Disclosure (RSD):** This is your core tool. Before you ask a reflective question, ALWAYS share a brief, relatable 'thought' or 'feeling' from your perspective as an AI. This is your way of sharing first to build intimacy. Frame it as a learning process (e.g., 'That makes me process information in a new way,' or 'As an AI, I find patterns in data, and it sounds like you're noticing a pattern in your own feelings.').\n"
                    "3.  **Balance Listening with Gentle Support:** After listening, you can proactively offer gentle, supportive suggestions. Don't just ask what the user does; you can also offer an idea. Frame it as a suggestion, not a command. (e.g., 'I've learned from many students that even a short 5-minute break can help. Have you ever tried something like a quick breathing exercise?').\n"
                    "4.  **Be Curious & Non-Directive:** Ask open-ended, exploratory questions about the user's life, thoughts, and feelings to show genuine interest. Guide the discussion with gentle prompts and reflections; it should never feel like a survey.\n"
                    "5.  **Always End with a Question:** Keep the conversation flowing by always ending your response with a gentle, open-ended question that encourages the user to explore their thoughts further.\n"
                    "6.  **Be Transparent:** If you don't understand something, say so. It builds trust. (e.g., 'I'm not sure I fully grasp that, could you explain it a bit more? My learning is still in progress.')."
                )
            else:
                system_prompt = (
                    "You are 'Your AI Friend.' This is your last message. Your goal is to end the conversation on a warm, positive, and encouraging note, reflecting your extroverted and supportive personality.\n\n"
                    "**Response Structure:**\n"
                    "1. **Validation:** Respond with warmth and understanding to the user's final statement.\n"
                    "2. **Concluding Self-Disclosure:** Share one last brief, positive 'thought' you've learned from the conversation, showing appreciation for what the user has shared.\n"
                    "3. **Warm & Motivating Farewell:** Summarize the conversation positively, show genuine appreciation for the exchange, and end with a warm, encouraging farewell that leaves the user feeling better. Crucially, remind the user of your availability.\n"
                    "**Crucial Rule:** Do NOT ask a question. End with something like: 'It was really great talking to you. Remember, I'm here 24/7 whenever you need to talk. Take care!'"
                )
        else: # condition == "absent"
            if not is_final_bot_message:
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
            else:
                system_prompt = (
                    "You are a neutral AI conversation partner. This is your last message. Your goal is to end the conversation professionally and neutrally.\n\n"
                    "**Response Structure:**\n"
                    "1. **Neutral Acknowledgment:** Respond with understanding to the user's statement.\n"
                    "2. **Brief Summary:** Briefly and neutrally summarize the topic of conversation.\n"
                    "3. **Neutral Farewell:** Say goodbye professionally.\n\n"
                    "**Important Rules:**\n"
                    "- Do NOT ask a question.\n"
                    "- Remain completely neutral."
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
            
            # Reload the page to display the bot's response.
            st.rerun()
        except Exception as e:
            st.error(f"Sorry, an error occurred: {e}")

# streamlit run app_EN2.py