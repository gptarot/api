import time
from datetime import datetime

import requests  # type: ignore
import streamlit as st

API_URL = "http://0.0.0.0:8000/predict/interpretations"
TAROT_CARDS = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]


ANSWER_SKELETON = """# 🔮 Tarot Reading for {name}

**Date of Birth:** {dob}
**Question:** *{question}*

---

{numerology}

# 🃏 Tarot Card Interpretations

{interpretations}
"""

INTERPRETATION_TEMPLATE = """## {emoji} {position} - {card_name} ({orientation})

{meaning}

"""


def format_response(data):
    numerology = data.get("numerology_meaning", "")
    interpretation_blocks = []

    position_emoji = {"past": "⏮️", "present": "▶️", "future": "⏭️"}
    for interp in data["interpretations"]:
        block = INTERPRETATION_TEMPLATE.format(
            emoji=position_emoji.get(interp["position"], "🔮"),
            position=interp["position"].title(),
            card_name=interp["card_name"],
            orientation="↑ Upright" if interp["orientation"] == "upright" else "↓ Reversed",
            meaning=interp["meaning"],
        )
        interpretation_blocks.append(block)

    return ANSWER_SKELETON.format(
        name=data["name"],
        dob=data["dob"],
        question=data["question"],
        numerology=numerology + "\n---\n" if numerology else "",
        interpretations="\n".join(interpretation_blocks),
    )


def get_tarot_reading(
    name: str,
    dob: datetime,
    question: str,
    past_card: str,
    past_upright: bool,
    present_card: str,
    present_upright: bool,
    future_card: str,
    future_upright: bool,
) -> str:
    if not name or not dob or not question:
        return "Please fill in all required fields (Name, Date of Birth, Question)"

    payload = {
        "name": name,
        "dob": dob.strftime("%Y-%m-%d"),
        "question": question,
        "past_card": {"name": past_card, "is_upright": past_upright},
        "present_card": {"name": present_card, "is_upright": present_upright},
        "future_card": {"name": future_card, "is_upright": future_upright},
    }

    progress = st.progress(0)
    messages = ["🔄 Preparing your request...", "🧠 Asking the oracle...", "✨ Reading received. Formatting..."]

    for i, msg in enumerate(messages):
        progress.progress(int((i + 1) / len(messages) * 100))
        st.info(msg)
        time.sleep(0.7)

    try:
        response = requests.post(
            API_URL,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )

        if response.status_code == 200:
            data = response.json()
            progress.progress(100)
            st.success("✅ Reading complete.")
            return format_response(data)
        else:
            return f"API Error: {response.status_code}\n\n{response.text}"

    except requests.exceptions.ConnectionError:
        return "Connection Error: Could not connect to API. Is the server running?"
    except requests.exceptions.Timeout:
        return "Timeout Error: The request took too long. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"


# --- UI Layout ---
st.set_page_config(page_title="🔮 GPTarot - AI Tarot Reader", layout="wide")

st.title("🔮 GPTarot - AI Tarot Reader")
st.write(
    "Get personalized tarot readings powered by AI. Fill in your details and select three cards for past, present, and future."
)

with st.sidebar:
    st.header("👤 Your Information")
    name = st.text_input("Name", "John Doe")
    dob = st.date_input("Date of Birth", format="YYYY-MM-DD", value=datetime(2000, 1, 1))
    question = st.text_area("Your Question", "Will my current love last forever?")

    st.header("🃏 Select Your Cards")

    st.subheader("⏮️ Past Card")
    past_card = st.selectbox("Past Card", TAROT_CARDS, index=7)
    past_upright = st.checkbox("Upright (Past)", value=False)

    st.subheader("▶️ Present Card")
    present_card = st.selectbox("Present Card", TAROT_CARDS, index=0)
    present_upright = st.checkbox("Upright (Present)", value=True)

    st.subheader("⏭️ Future Card")
    future_card = st.selectbox("Future Card", TAROT_CARDS, index=1)
    future_upright = st.checkbox("Upright (Future)", value=True)

    if st.button("✨ Get Reading"):
        with st.spinner("Summoning the spirits..."):
            result = get_tarot_reading(
                name, dob, question, past_card, past_upright, present_card, present_upright, future_card, future_upright
            )
            st.session_state["reading_result"] = result

# --- Output display ---
st.header("📖 Your Reading")
if "reading_result" in st.session_state:
    st.markdown(st.session_state["reading_result"], unsafe_allow_html=True)
else:
    st.markdown("*Your tarot reading will appear here...*")

st.markdown("---")
st.info("💡 Tip: Make sure your API server is running on `http://127.0.0.1:8000` before submitting.")
