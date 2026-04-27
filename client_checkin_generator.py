# client_checkin_generator.py

import streamlit as st
from openai import OpenAI

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("Client Check-In Email Generator")

customer_name = st.text_input("Customer first name")
agent_name = st.text_input("Agent name")
context = st.text_area("Personal context / notes")
tone = st.selectbox("Tone", ["Friendly professional", "Very brief", "Warm and conversational"])
purpose = st.selectbox("Purpose", ["Annual check-in", "Semiannual check-in", "Renewal-season review"])

topics = st.multiselect(
    "Coverage reminders to include",
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

avoid = st.text_area("Anything to avoid mentioning?")

if st.button("Generate Email"):
    prompt = f"""
You are helping an independent insurance agency write a professional customer check-in email.

Write a short, warm, polished email from the agent to the customer.

Requirements:
- Do not sound like a newsletter.
- Do not sound salesy.
- Keep it under 200 words.
- Make it feel personally written.
- Encourage the customer to tell us early about life changes so we can proactively adjust coverage and keep pricing as fair as possible.
- Include only the selected coverage reminders.
- Use plain language.
- Do not over-explain.
- End with a simple invitation to reply.

Customer first name: {customer_name}
Agent name: {agent_name}
Purpose: {purpose}
Tone: {tone}
Personal context: {context}
Coverage reminders: {", ".join(topics)}
Avoid mentioning: {avoid}

Return:
1. Subject line
2. Email body
3. Short Partner AMS note
"""

try:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    st.text_area("Copy Email", response.output_text, height=350)

except Exception as e:
    st.error("The AI request failed. Check that API billing is active, the model name is valid, and your OpenAI project has usage available.")
    st.code(str(e))

    st.subheader("Generated Message")
    st.write(response.output_text)
