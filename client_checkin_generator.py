import streamlit as st
import os
from openai import OpenAI

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

POLICIES = [
    "Auto",
    "Home",
    "Umbrella",
    "RV",
    "Boat",
    "Motorcycle",
    "Rental properties",
    "Commercial insurance"
]

TOPICS = [
    "General life changes",
    "Car shopping or vehicle changes",
    "Buying a new home or moving",
    "Starting a business",
    "Retiring",
    "Young drivers / kids approaching driving age",
    "Home projects or renovations",
    "Roof, trees, or property condition",
    "Claims strategy and deductibles",
    "Umbrella / liability limits",
    "Bundling opportunities"
]

st.title("Client Check-In Email Generator")

# ---- Remember agent using URL/session ----

query_params = st.query_params

if "agent" in query_params:
    st.session_state.agent = query_params["agent"]

if "agent" not in st.session_state:
    st.session_state.agent = AGENTS[0]

selected_agent = st.selectbox(
    "Agent",
    AGENTS,
    index=AGENTS.index(st.session_state.agent) if st.session_state.agent in AGENTS else 0
)

st.session_state.agent = selected_agent
st.query_params["agent"] = selected_agent

# ---- Client inputs ----

customer_name = st.text_input("Customer First Name")

policies_written = st.multiselect(
    "Policies We Currently Write for This Customer",
    POLICIES
)

household_stage = st.selectbox(
    "Household / Life Stage",
    [
        "Unknown / do not mention",
        "May have kids approaching driving age",
        "Has young drivers",
        "No known young driver concern",
        "Retired or approaching retirement",
        "Business owner or may start a business"
    ]
)

topics = st.multiselect(
    "Specific Topics to Work In",
    TOPICS
)

context = st.text_area(
    "Personal Context / Notes",
    placeholder="Example: Long-time home/auto client. Recently discussed roof age. Has a son who may be driving soon."
)

avoid = st.text_area(
    "Anything to Avoid Mentioning?",
    placeholder="Example: Do not mention umbrella. Do not mention young drivers."
)

tone = st.selectbox(
    "Tone",
    ["Friendly professional", "Warm and conversational", "Very brief"]
)

# ---- Generate ----

if st.button("Generate Email"):

    if not customer_name:
        st.warning("Please enter the customer's first name.")
    else:

        prompt = f"""
You are writing a short client check-in email for Kelly Insurance Agency.

The email should sound like a personal "just checking in" note from the agent, not a newsletter and not a sales pitch.

Core management message that should appear in every email:
- We are just checking in.
- Invite the customer to tell us early if they are planning any changes.
- Examples may include car shopping, buying a new home, moving, starting a business, retiring, adding drivers, home projects, buying recreational vehicles, rental properties, or other life changes.
- Explain that early notice helps the agency proactively adjust coverage and keep pricing as fair as possible.
- Keep it friendly, professional, concise, and helpful.

Use the policies we currently represent them on to guide the message:
- If Auto is included, it is okay to mention vehicle changes, car shopping, and drivers in the household.
- If Auto is included and the household stage suggests kids or young drivers, gently mention that new drivers are one of the biggest pricing changes and planning early helps.
- If Home is included, it is okay to mention home projects, moving, roof/property changes, and buying another home.
- If Umbrella is included, it is okay to mention liability protection and keeping underlying policies aligned.
- If Umbrella is NOT included but they have Auto or Home, you may gently mention that an umbrella can be worth reviewing, but do not make it the focus unless selected as a topic.
- If RV, Boat, or Motorcycle are included, mention recreational vehicles only if it fits naturally.
- If Rental properties are included, mention letting us know about tenant, occupancy, ownership, or property changes.
- If Commercial insurance is included, mention business changes, employees, vehicles, locations, or operations.
- If they only have one or two lines with us, lightly invite them to let us know if they would like us to review whether bundling other policies would be helpful.
- Do not be pushy. Bundling should sound like a service opportunity, not a sales pitch.

Selected agent: {selected_agent}
Customer first name: {customer_name}
Policies currently written: {", ".join(policies_written)}
Household / life stage: {household_stage}
Topics to work in: {", ".join(topics)}
Personal context: {context}
Anything to avoid: {avoid}
Tone: {tone}

Write the output in exactly this format:

Subject:
<subject line>

Email:
<email body>

Partner Note:
<short note saying the check-in email was drafted/sent and generally what was discussed>
"""

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            output = response.output_text

            st.success("Generated")

            st.text_area("Copy / Paste Output", output, height=450)

        except Exception as e:
            st.error("AI request failed. Check API billing, quota, key, or model access.")
            st.code(str(e))
