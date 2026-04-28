import streamlit as st
import os
from datetime import date
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
    "Car shopping / vehicle changes",
    "Young drivers / kids approaching driving age",
    "Buying a new home or moving",
    "Home projects or renovations",
    "Starting a business",
    "Retiring",
    "Roof, trees, or property condition",
    "Claims strategy and deductibles",
    "Umbrella / liability limits",
    "Bundling opportunities",
    "Rental property changes",
    "Commercial business changes"
]

PVP_LINK = "https://www.progressive.com/auto/insurance-coverages/vehicle-protection-plan/"

# Progressive PVP: less than 3 model years old = current model year and prior 2 model years
current_year = date.today().year
pvp_min_model_year = current_year - 2

st.title("Client Check-In Email Generator")

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

customer_name = st.text_input("Customer First Name")

policies_written = st.multiselect(
    "Policies We Currently Write for This Customer",
    POLICIES
)

auto_carrier = "Not applicable"
if "Auto" in policies_written:
    auto_carrier = st.selectbox(
        "Auto Carrier",
        [
            "Unknown / do not mention",
            "Progressive",
            "Safeco",
            "Grange",
            "Westfield",
            "Travelers",
            "Farmers / Foremost Signature",
            "Other"
        ]
    )

    st.info(
        f"If this customer has Progressive auto and may be shopping for a vehicle, "
        f"consider mentioning Progressive Vehicle Protection for vehicles model year "
        f"{pvp_min_model_year} or newer."
    )

    if auto_carrier == "Progressive":
        st.markdown(f"[More info on Progressive Vehicle Protection]({PVP_LINK})")

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
    "Select up to 3 Topics",
    TOPICS,
    max_selections=3
)

context = st.text_area(
    "Personal Context / Notes",
    placeholder="Example: Long-time home/auto client. Son may be driving soon. Mentioned possibly replacing a vehicle."
)

avoid = st.text_area(
    "Anything to Avoid Mentioning?",
    placeholder="Example: Do not mention young drivers. Do not mention umbrella."
)

tone = st.selectbox(
    "Tone",
    ["Friendly professional", "Warm and conversational", "Very brief"]
)

if st.button("Generate Email"):

    if not customer_name:
        st.warning("Please enter the customer's first name.")
    else:

        progressive_pvp_instruction = ""
        if "Auto" in policies_written and auto_carrier == "Progressive":
            progressive_pvp_instruction = f"""
Because this customer has Progressive auto:
- If car shopping or vehicle changes are selected or mentioned, include a brief note about Progressive Vehicle Protection.
- Explain that it may be worth considering if they are looking at a vehicle model year {pvp_min_model_year} or newer.
- Describe it simply as an optional protection plan/extended warranty-style coverage for newer vehicles.
- Do not overpromise eligibility or coverage.
- Mention that we can review whether it fits once they know what vehicle they are considering.
"""

        prompt = f"""
You are writing a short client check-in email for Kelly Insurance Agency.

Every email must:
- Sound like a personal "just checking in" note.
- Avoid sounding like a newsletter or sales pitch.
- Invite the customer to tell us early if they are planning changes.
- Examples may include car shopping, buying a home, moving, starting a business, retiring, adding drivers, home projects, recreational vehicles, rental properties, or other life changes.
- Explain that early notice helps us proactively adjust coverage and keep pricing as fair as possible.
- Keep it concise, friendly, and professional.

Use the selected policies to guide the message:
- If Auto is included, mention vehicle changes or car shopping when natural.
- If Auto is included and the household stage suggests kids or young drivers, gently mention that new drivers are one of the biggest pricing changes and planning early helps.
- If Home is included, mention home projects, moving, roof/property changes, or buying another home when relevant.
- If Umbrella is included, mention keeping liability protection aligned.
- If Umbrella is not included but they have Auto or Home, you may gently mention reviewing an umbrella only if selected as a topic.
- If RV, Boat, or Motorcycle are included, mention recreational vehicles only if relevant.
- If Rental properties are included, mention tenant, occupancy, ownership, or property changes when relevant.
- If Commercial insurance is included, mention business changes, employees, vehicles, locations, or operations when relevant.
- If they only have one or two lines with us, lightly invite them to let us know if they would like us to review whether bundling other policies would help.

{progressive_pvp_instruction}

Selected agent: {selected_agent}
Customer first name: {customer_name}
Policies currently written: {", ".join(policies_written)}
Auto carrier: {auto_carrier}
Household / life stage: {household_stage}
Selected topics, maximum three: {", ".join(topics)}
Personal context: {context}
Anything to avoid: {avoid}
Tone: {tone}

Return exactly this format:

Subject:
<subject line>

Email:
<email body under 190 words>

Partner Note:
<short internal note saying the check-in email was drafted/sent and generally what was discussed>
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
