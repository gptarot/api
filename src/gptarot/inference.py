from datetime import datetime

import requests  # type: ignore
import streamlit as st

API_URL = "http://0.0.0.0:8000"


def draw_three_cards(name: str, dob: str):
    """Draw 3 tarot cards from the API."""
    payload = {"name": name, "dob": dob, "count": 3}
    try:
        r = requests.post(
            f"{API_URL}/tarot-cards/draw",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["cards"]
        else:
            st.error(f"Failed to draw cards: {r.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def get_tarot_reading(name: str, dob: str, question: str):
    """Get complete tarot reading with interpretations."""
    if not all([name, dob, question]):
        st.warning("⚠️ Please fill in all fields")
        return None

    with st.spinner("🔮 Drawing your cards..."):
        cards = draw_three_cards(name, dob)
        if not cards or len(cards) < 3:
            st.error("Failed to draw cards")
            return None

    with st.spinner("✨ Interpreting your reading..."):
        payload = {
            "name": name,
            "dob": dob,
            "question": question,
            "past_card": cards[0],
            "present_card": cards[1],
            "future_card": cards[2],
        }

        try:
            r = requests.post(
                f"{API_URL}/predict/interpretations",
                headers={"accept": "application/json", "Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            if r.status_code == 200:
                result = r.json()
                # Store the original cards with image_url
                result["original_cards"] = cards
                return result
            else:
                st.error(f"Interpretation failed: {r.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return None


def display_card(card_data: dict, interpretation: dict):
    """Display a single tarot card with its interpretation."""
    orientation = interpretation["orientation"]
    is_reversed = orientation == "reversed"

    if card_data.get("image_url"):
        rotation_style = "transform: rotate(180deg);" if is_reversed else ""
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{API_URL}{card_data["image_url"]}"
                     style="width: 200px; {rotation_style}"
                     alt="{card_data["name"]}">
                <p style="margin-top: 10px; font-size: 14px; color: #666;">
                    {card_data["name"]} {"(Reversed)" if is_reversed else "(Upright)"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.write(f"**{card_data['name']}** {'↓ Reversed' if is_reversed else '↑ Upright'}")

    with st.expander("📖 Read Interpretation", expanded=True):
        st.write(interpretation["meaning"])


# --- UI Setup ---
st.set_page_config(page_title="🔮 GPTarot Reader", layout="wide")

st.title("🔮 GPTarot - AI Tarot Reader")
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
    🃏 **Three Card Spread**
    - **Past**: Influences that have shaped your situation
    - **Present**: Your current circumstances and energies
    - **Future**: Potential outcomes and guidance

    💫 Your reading includes personalized numerology insights based on your birth date.
    """)

if get_reading_btn:
    dob_str = dob.strftime("%Y-%m-%d")
    reading_data = get_tarot_reading(name, dob_str, question)

    if reading_data:
        st.success("✅ Your reading is ready!")
        st.session_state["reading"] = reading_data

if "reading" in st.session_state:
    data = st.session_state["reading"]

    st.markdown("---")
    st.header(f"🔮 Reading for {data['name']}")
    st.caption(f"📅 {data['dob']} | 🔍 *{data['question']}*")

    if data.get("numerology_meaning"):
        with st.expander("🔢 Numerology Insights", expanded=False):
            st.write(data["numerology_meaning"])

    st.markdown("### 🃏 Your Cards")

    positions = {"past": "⏮️ Past", "present": "▶️ Present", "future": "⏭️ Future"}
    cols = st.columns(3)

    original_cards = data.get("original_cards", [{}, {}, {}])

    for idx, interp in enumerate(data["interpretations"]):
        with cols[idx]:
            position = interp["position"]
            st.markdown(f"### {positions.get(position, position.title())}")
            card_data = original_cards[idx] if idx < len(original_cards) else {}
            display_card(card_data, interp)

st.markdown("---")
st.caption(f"💡 Ensure the API server at `{API_URL}` is running")
