from datetime import datetime

import requests  # type: ignore
import streamlit as st

API_URL = "http://0.0.0.0:8000"


def draw_three_cards(name: str, dob: str):
    payload = {"name": name, "dob": dob, "count": 3, "follow_numerology": False}
    try:
        r = requests.post(
            f"{API_URL}/tarot-cards/draw",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("cards", [])
        st.error(f"Failed to draw cards: {r.status_code}")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return []


def get_tarot_and_numerology(name: str, dob: str, question: str):
    """Perform 2-phase prediction with progress bar."""
    progress = st.progress(0, text="🔮 Starting your reading...")
    status = st.empty()

    # Phase 1: Draw Cards
    status.text("🎴 Drawing your tarot cards...")
    cards = draw_three_cards(name, dob)
    progress.progress(33)
    if not cards or len(cards) < 3:
        st.error("Failed to draw cards")
        return None

    # Prepare cards for interpretation
    payload_tarot = {
        "name": name,
        "question": question,
        "past_card": {
            "name": cards[0]["name"],
            "is_upright": cards[0]["is_upright"],
        },
        "present_card": {
            "name": cards[1]["name"],
            "is_upright": cards[1]["is_upright"],
        },
        "future_card": {
            "name": cards[2]["name"],
            "is_upright": cards[2]["is_upright"],
        },
    }

    # Phase 2: Tarot Interpretation
    status.text("✨ Interpreting tarot reading...")
    try:
        r = requests.post(
            f"{API_URL}/predict/tarot-interpretations",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload_tarot,
            timeout=60,
        )
        progress.progress(66)
        if r.status_code != 200:
            st.error(f"Tarot interpretation failed: {r.status_code}")
            return None
        tarot_data = r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Interpretation request failed: {e}")
        return None

    # Phase 3: Numerology
    status.text("🔢 Calculating numerology insights...")
    try:
        r2 = requests.post(
            f"{API_URL}/predict/numerology-interpretations",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={"name": name, "dob": dob, "question": question},
            timeout=30,
        )
        progress.progress(100)
        if r2.status_code == 200:
            tarot_data["numerology_meaning"] = r2.json().get("numerology_meaning", "")
        else:
            tarot_data["numerology_meaning"] = None
    except requests.exceptions.RequestException:
        tarot_data["numerology_meaning"] = None

    tarot_data["original_cards"] = cards
    status.text("✅ Reading complete.")
    return tarot_data


def display_card(card_data: dict, interpretation: dict):
    orientation = interpretation["orientation"]
    is_reversed = orientation.lower().startswith("rev")

    if card_data.get("image_url"):
        rotation = "transform: rotate(180deg);" if is_reversed else ""
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="{API_URL}{card_data["image_url"]}" style="width:200px;{rotation}">
                <p style="margin-top:10px;font-size:14px;color:#666;">
                    {card_data["name"]} {"(Reversed)" if is_reversed else "(Upright)"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.write(f"**{card_data.get('name', 'Unknown')}** {'↓ Reversed' if is_reversed else '↑ Upright'}")

    with st.expander("📖 Read Interpretation", expanded=True):
        st.write(interpretation["meaning"])


# --- UI ---
st.set_page_config(page_title="🔮 Tarotpedia Reader", layout="wide")

st.title("🔮 Tarotpedia - AI Tarot Reader")
st.markdown("*Discover insights through the ancient art of tarot, powered by AI*")

col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Your Information")
    name = st.text_input("Name", placeholder="Enter your name")
    dob = st.date_input("Date of Birth", value=datetime(2000, 1, 1), format="YYYY-MM-DD")
    question = st.text_area("Your Question", placeholder="What guidance do you seek?", height=100)
    get_reading_btn = st.button("✨ Get Reading", type="primary", use_container_width=True)

with col2:
    st.subheader("About Your Reading")
    st.markdown("""
    **Three Card Spread**
    - **Past**: Influences that have shaped your situation
    - **Present**: Your current circumstances and energies
    - **Future**: Potential outcomes and guidance

    💫 Your reading includes personalized numerology insights based on your birth date.
    """)

if get_reading_btn:
    if not all([name, dob, question]):
        st.warning("⚠️ Please fill in all fields.")
    else:
        dob_str = dob.strftime("%Y-%m-%d")
        reading_data = get_tarot_and_numerology(name, dob_str, question)
        if reading_data:
            st.session_state["reading"] = reading_data
            st.success("Your reading is ready!")

if "reading" in st.session_state:
    data: dict = st.session_state["reading"]
    st.markdown("---")
    st.header(f"🔮 Reading for {name}")

    if data.get("numerology_meaning"):
        with st.expander("🔢 Numerology Insights", expanded=True):
            st.write(data["numerology_meaning"])

    st.markdown("### Tarot Cards Deck")

    cols = st.columns(3)
    with cols[0]:
        st.markdown("<h3 style='text-align:center;'>Past</h3>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<h3 style='text-align:center;'>Present</h3>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("<h3 style='text-align:center;'>Future</h3>", unsafe_allow_html=True)

    cards = data.get("original_cards", [])
    interps = data.get("interpretations", [])
    for idx, interp in enumerate(interps):
        if idx < len(cols):
            with cols[idx]:
                display_card(cards[idx] if idx < len(cards) else {}, interp)

    st.markdown("---")
    st.write(data.get("summary", ""))
