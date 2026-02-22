import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from fpdf import FPDF
from datetime import datetime
import re

# ---------------- CONFIG ----------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="TravelGuideAI+",
    page_icon="🌍",
    layout="wide"
)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🌍 TravelGuideAI+</h1>
<p style='text-align: center; font-size:18px;'>
AI-Powered Smart Travel Planner
</p>
<hr>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ✈️ Trip Details")

    destination = st.text_input("Destination")
    days = st.slider("Duration (Days)", 1, 15, 3)
    nights = max(days - 1, 0)

    budget = st.selectbox("Budget Type", ["Low", "Medium", "Luxury"])
    travel_type = st.radio("Travel Type", ["Solo", "Couple", "Family", "Friends"])

    interests = st.multiselect(
        "Interests",
        ["Adventure", "Food", "Culture", "Nature", "Shopping", "Relaxation"]
    )

    generate_btn = st.button("Generate Smart Itinerary")
    reset_btn = st.button("Reset Trip")

# ---------------- RESET ----------------
if reset_btn:
    st.session_state.clear()
    st.rerun()

# ---------------- HELPER FUNCTIONS ----------------
def estimate_budget():
    base = {"Low": 1500, "Medium": 3500, "Luxury": 7000}
    daily = base[budget]
    return daily, daily * days

def best_time_to_visit():
    return "October to March" if budget != "Luxury" else "Year-round"

def packing_list():
    items = ["ID Proof", "Mobile Charger"]
    if "Adventure" in interests:
        items += ["Sports Shoes", "Backpack"]
    if "Nature" in interests:
        items += ["Sunscreen", "Cap"]
    if "Food" in interests:
        items += ["Hand Sanitizer"]
    return items

def fallback_itinerary():
    return f"""
DESTINATION: {destination}

DURATION: {days} Days / {nights} Nights
BUDGET: {budget}
TRAVEL TYPE: {travel_type}

DAY-WISE PLAN
Day 1: Arrival & local exploration
Day 2: Major attractions & food tour
Day 3: Shopping & departure

HOTEL:
Well-rated hotels near city center

TRANSPORT:
Cabs / Metro / Rentals

TRAVEL TIPS:
- Keep documents safe
- Follow local rules
- Stay hydrated
"""

def generate_ai_itinerary():
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
        Create a professional travel itinerary.

        Destination: {destination}
        Days: {days}
        Nights: {nights}
        Budget: {budget}
        Travel Type: {travel_type}
        Interests: {', '.join(interests)}

        Include day-wise plan, hotels, transport, food, safety tips.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception:
        return fallback_itinerary()

# 🔥 CLEAN TEXT FOR PDF (FIXES ERROR)
def clean_text_for_pdf(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def export_pdf(content):
    cleaned_content = clean_text_for_pdf(content)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    for line in cleaned_content.split("\n"):
        pdf.multi_cell(0, 8, line)

    filename = f"TravelGuideAI_{destination}.pdf"
    pdf.output(filename)
    return filename

# ---------------- MAIN LOGIC ----------------
if generate_btn:
    if not destination:
        st.warning("Please enter a destination.")
    else:
        with st.spinner("Designing your trip..."):
            itinerary = generate_ai_itinerary() if API_KEY else fallback_itinerary()

            if "history" not in st.session_state:
                st.session_state["history"] = []

            st.session_state["itinerary"] = itinerary
            st.session_state["history"].append({
                "destination": destination,
                "date": datetime.now().strftime("%d %b %Y")
            })

            st.success("Itinerary Generated!")

# ---------------- DASHBOARD ----------------
if "itinerary" in st.session_state:

    daily_cost, total_cost = estimate_budget()

    st.markdown("## Trip Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Destination", destination)
    c2.metric("Days", days)
    c3.metric("Daily Cost (₹)", daily_cost)
    c4.metric("Total Cost (₹)", total_cost)

    st.markdown("## Travel Insights")
    colA, colB = st.columns(2)
    colA.info(f"Best Time to Visit: {best_time_to_visit()}")
    colB.info(f"Packing Checklist: {', '.join(packing_list())}")

    st.markdown("## Your Personalized Itinerary")
    st.write(st.session_state["itinerary"])

    st.markdown("### Export")
    if st.button("Download PDF"):
        pdf = export_pdf(st.session_state["itinerary"])
        with open(pdf, "rb") as f:
            st.download_button("Download Itinerary PDF", f, file_name=pdf)

# ---------------- HISTORY ----------------
if "history" in st.session_state:
    st.markdown("## Previous Trips")
    for h in reversed(st.session_state["history"]):
        st.write(f"{h['destination']} ({h['date']})")

# ---------------- FOOTER ----------------
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
TravelGuideAI+ | Internship Project | AI-Enabled Travel Planning System
</p>
""", unsafe_allow_html=True)
