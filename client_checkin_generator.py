import streamlit as st
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.set_page_config(page_title="Client Check-In Generator", layout="centered")

st.title("Client Check-In Email Generator")

# ---- INPUTS ----

customer_name = st.text_input("Customer First Name")
agent_name = st.text_input("Agent Name")

context = st.text_area(
    "Personal Context (optional)",
    placeholder="Example: Added teen driver last year, long-time client, discussed roof, etc."
)

tone = st.selectbox(
    "Tone",
    ["Friendly professional", "Warm and conversational", "Very brief"]
)

purpose = st.selectbox(
    "Purpose",
    ["Annual check-in", "Semiannual check-in", "Renewal-season review"]
)

topics = st.multiselect(
    "Coverage Reminders to Include",
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

avoid = st.text_area("Anything to avoid mentioning? (optional)")

# ---- GENERATE BUTTON ----

if st.button("Generate Email"):

    if not customer_name or not agent_name:
        st.warning("Please enter at least the customer name and agent name.")
    else:
        prompt = f"""
You are helping an independent insurance agency write a short, personal client check-in email.

Write a professional but natural email that:
- Feels like it was written personally by the agent (not marketing)
- Is under 180 words
- Encourages the client to share upcoming life changes early so coverage can be adjusted proactively and pricing stays fair
- Includes ONLY the relevant coverage reminders selected
- Uses simple, clear language
- Ends with a low-pressure invitation to reply

Customer name: {customer_name}
Agent name: {agent_name}
Purpose: {purpose}
Tone: {tone}
Context: {context}
Topics to include: {", ".join(topics)}
Avoid mentioning: {avoid}

Return format:

Subject line:
<subject>

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

            st.success("Email generated successfully")

            st.subheader("Copy / Paste Output")
            st.text_area("Generated Email", output, height=400)

        except Exception as e:
            st.error("Something went wrong with the AI request.")
            st.write("Common causes:")
            st.write("- API billing not set up")
            st.write("- Invalid API key")
            st.write("- Temporary rate limits")

            st.code(str(e))
