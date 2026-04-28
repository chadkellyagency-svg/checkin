import streamlit as st
import os
from openai import OpenAI

# ---- CONFIG ----
st.set_page_config(page_title="Client Check-In Generator", layout="centered")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

AGENTS = [
    "Ben Kelly",
    "Chad Kelly",
    "Tonya Woodlee",
    "Jay Woodlee",
    "Jay Mason Woodlee",
    "Lindsay Sullivan",
    "Mark Renicker",
    "Meghan Dye"
]

# ---- REMEMBER AGENT (via URL + session state) ----

query_params = st.query_params

# Load from URL if exists
if "agent" in query_params:
    st.session_state.agent = query_params["agent"]

# Default if nothing set
if "agent" not in st.session_state:
    st.session_state.agent = AGENTS[0]

# ---- UI ----

st.title("Client Check-In Email Generator")

selected_agent = st.selectbox(
    "Agent",
    AGENTS,
    index=AGENTS.index(st.session_state.agent) if st.session_state.agent in AGENTS else 0
)

# Save selection to session + URL
st.session_state.agent = selected_agent
st.query_params["agent"] = selected_agent

customer_name = st.text_input("Customer First Name")

context = st.text_area(
    "Personal Context (optional)",
    placeholder="Example: Long-time client, added teen driver last year, discussed roof age, etc."
)

tone = st.selectbox(
    "Tone",
    ["Friendly professional", "Warm and conversational", "Very brief"]
)

topics = st.multiselect(
    "Coverage Reminders",
    [
        "Life changes",
        "Young drivers",
        "Home projects or renovations",
        "Roof, trees, or property condition",
        "Claims strategy and deductibles",
        "Umbrella / liability limits",
        "Bundling advantages",
        "Vehicle changes or business use"
    ]
)

# ---- GENERATE ----

if st.button("Generate Email"):

    if not customer_name:
        st.warning("Please enter the customer's name.")
    else:

        prompt = f"""
You are writing a short, natural client check-in email for an insurance agent.

Write ONLY the final answer. Do NOT explain anything.

Requirements:
- Under 180 words
- Personal, not marketing
- Encourages early communication about life changes
- Includes selected coverage reminders naturally
- Simple, clear language
- Ends with a low-pressure invitation to reply

Agent: {selected_agent}
Customer: {customer_name}
Context: {context}
Topics: {", ".join(topics)}

Return EXACTLY in this format:

Subject:
<subject line>

Email:
<body>

Partner Note:
<short internal note>
"""

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            output = response.output_text

            st.success("Generated")

            st.text_area("Copy Email", output, height=400)

        except Exception as e:
            st.error("AI request failed. Likely billing or quota issue.")
            st.code(str(e))
