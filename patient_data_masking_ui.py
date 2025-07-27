
# patient_data_masking_ui.py
"""
Astra Patient Data PII Masking & Remapping Prototype
----------------------------------------------------
Problem Statement:
------------------
Hospitals send patient data (including PII such as name, DOB, address, and treatment recommendations) to Astra, which acts as an intermediary to obtain billing codes and insurance approvals from various insurance companies. To comply with privacy regulations, Astra must mask all patient PII before sending data to insurance companies. Upon receiving insurance responses (billing codes, coverage limits, co-payments), Astra must accurately remap and restore the original patient details before sending the final data back to the hospital.
Solution Overview:
------------------
This Python-based prototype demonstrates a workflow for secure PII masking and remapping using a rule-based regex approach, with a Streamlit UI for interactive demonstration. The solution includes:
- Regex-based detection and redaction of PII from both structured fields and free-text notes.
- Assignment of a unique identifier (UUID) to each patient record for tracking and remapping.
- Simulated coding company and insurance billing response generation.
- Accurate restoration of original PII using stored mappings.
- Visual workflow diagram and step-by-step UI for user interaction.
Top 3 Approaches to Solve the Challenge:
----------------------------------------
1. **Rule-Based Regex Masking (Current Implementation):**
    - Use regular expressions to identify and mask PII in both structured and unstructured data.
    - Store mappings between placeholders and original values for later restoration.
    - Fast, simple, and does not require training data.
2. **Gen AI/NLP Model-Based Named Entity Recognition (NER):**
    - Use pre-trained NLP models (e.g., spaCy, Hugging Face Transformers) to detect and mask PII entities.
    - More robust and accurate, especially for complex or ambiguous text.
    - Can be fine-tuned for domain-specific entities.
3. **Database-Level Tokenization and Encryption:**
    - Tokenize or encrypt PII fields at the database level before exporting data.
    - Use secure key management and mapping tables for restoration.
    - Highest security, but may require infrastructure changes.
Recommended Approach:
---------------------
**Gen AI/NLP Model-Based Named Entity Recognition (NER)**
- This approach leverages advanced AI models to accurately detect and mask PII, including edge cases and complex entities that regex may miss.
- It is scalable, adaptable to new entity types, and can be integrated with existing Python libraries (spaCy, Transformers).
High-Level Steps to Achieve the Solution:
-----------------------------------------
1. **Data Ingestion:** Receive patient data from hospital in JSON format.
2. **PII Detection & Masking:** Use a Gen AI/NLP model to identify and mask PII in all fields and notes. Replace PII with placeholders and assign a unique UUID to each record.
3. **Send Masked Data:** Transmit masked data to insurance companies for billing code and approval processing.
4. **Receive coded with Insurance Response:** Collect insurance responses (billing codes, limits, co-payments) linked by UUID.
5. **PII Remapping:** Restore original PII using stored mappings and UUIDs, reconstructing the full patient record.
6. **Return to Hospital:** Send the final, remapped data back to the hospital.
This prototype demonstrates the workflow using regex-based masking, but can be enhanced with Gen AI/NLP models for production use.
"""

import uuid
import json
import streamlit as st
import pandas as pd
from typing import Dict
import re
import graphviz


if "PII_MAPPING_DB" not in st.session_state:
    st.session_state["PII_MAPPING_DB"] = {}


# Default example hospital data
default_hospital_data = [
    {
        "name": "John Doe",
        "dob": "1990-05-21",
        "address": "123 Main St",
        "diagnosis": "Type 2 Diabetes",
        "recommendation": "Insulin therapy",
        "notes": "John Doe is a 34-year-old male living at 123 Main St, diagnosed on 1990-05-21."
    },
    {
        "name": "Jane Smith",
        "dob": "1985-09-12",
        "address": "456 Oak Ave",
        "diagnosis": "Hypertension",
        "recommendation": "Lifestyle changes and medication",
        "notes": "Jane Smith was born on 1985-09-12 and resides at 456 Oak Ave."
    }
]

# ---------------------------------------------
# Regex PII redaction
# ---------------------------------------------
def detect_and_redact_pii_with_regex(text, uid):
    # ---------------------------------------------
    # Uses simple regex pattern matching for common PII patterns
    # This is a form of Named-Entity Recognition (NER) using regular expressions,
    # similar to how NLP models identify entities, but here it's rule-based.
    # Patterns are defined for dates, person names, and addresses.
    # This approach is fast and does not require training data or ML models,
    # but may miss edge cases or complex entities that NLP/AI models could catch.
    # For more complex NER tasks, open source models like spaCy (with 'en_core_web_sm' or 'en_core_web_trf'),
    # Hugging Face Transformers (e.g., BERT, RoBERTa, DistilBERT for NER), and Flair are available.
    # These can be downloaded and used for more accurate and robust entity extraction.
    # ---------------------------------------------
    patterns = {
        'DATE1': r'\b\d{4}-\d{2}-\d{2}\b',
        'DATE2': r'\b\d{2}-\d{2}-\d{4}\b',
        'PERSON': r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b',
        'ADDRESS': r'\d+\s+[A-Za-z]+\s+(St|Ave|Rd)'
    }
    placeholder_map = {}
    redacted = text
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            placeholder = f"<{label}_{uid[:8]}>"
            redacted = redacted.replace(match, placeholder)
            placeholder_map[placeholder] = match
    return redacted, placeholder_map

# ---------------------------------------------
# Mask PII from structured fields and redact free-text notes
# Uses regex NER for PII redaction
# ---------------------------------------------
def mask_pii(data):
    masked_records = []
    for record in data:
        uid = str(uuid.uuid4())
        notes_redacted, notes_map = detect_and_redact_pii_with_regex(record.get("notes", ""), uid)

        # Save both original and placeholders in structured format
        st.session_state["PII_MAPPING_DB"][uid] = {
            "original": {
                "name": record["name"],
                "dob": record["dob"],
                "address": record["address"]
            },
            "placeholders": notes_map
        }

        masked_record = {
            "patient_id": uid,
            "diagnosis": record["diagnosis"],
            "recommendation": record["recommendation"],
            "notes": notes_redacted
        }
        masked_records.append(masked_record)
    return masked_records


# ---------------------------------------------
# Simulated Insurance Response
# ---------------------------------------------
def simulate_insurance_response(masked_data):
    response = []
    for record in masked_data:
        record.update({
            "billing_code": "B1234",
            "coverage_limit": "$10,000",
            "co_payment": "$100"
        })
        response.append(record)
    return response

# ---------------------------------------------
# PII Remapping
# ---------------------------------------------
def remap_to_pii(insurance_response):
    final_records = []
    for record in insurance_response:
        uid = record["patient_id"]
        pii = st.session_state["PII_MAPPING_DB"].get(uid, {})
        original_info = pii.get("original", {})
        placeholders = pii.get("placeholders", {})
        notes = record.get("notes", "")

        for placeholder, original_value in placeholders.items():
            notes = notes.replace(placeholder, original_value)

        final_record = {
            "name": original_info.get("name"),
            "dob": original_info.get("dob"),
            "address": original_info.get("address"),
            "diagnosis": record["diagnosis"],
            "recommendation": record["recommendation"],
            "billing_code": record["billing_code"],
            "coverage_limit": record["coverage_limit"],
            "co_payment": record["co_payment"],
            "notes": notes
        }
        final_records.append(final_record)
    return final_records

# ---------------------------------------------
# Workflow Diagram
# ---------------------------------------------
def render_workflow_diagram():
    diagram = graphviz.Digraph()
    diagram.attr(rankdir="LR", bgcolor="#f9f9f9")
    diagram.attr("node", shape="box", style="filled", color="#4A90E2", fontcolor="white", fontname="Arial", fontsize="12")

    diagram.node("A", "🏥 Raw Hospital Data\n(Name, DOB, Address, Notes)")
    diagram.node("B", "🔒 Regex-Based (later model based as needed)\nPII Redaction including Notes")
    diagram.node("C", "📤 Sent to coding company then Insurance\nUUID for PII data and \n<PERSON>, <DATE> in Notes")
    diagram.node("D", "💸 Billing Info with coded data\n(Code like B1234, payment like $10,000 Limit)")
    diagram.node("E", "📥 Reconstructed Data\nOriginal PII data and Notes Restored")
    diagram.node("F", "📥 Receive payment or denial data from insurance companies.\n Close feedback loop")
    

    diagram.edge("A", "B", label="Submit to Redact PII")
    diagram.edge("B", "C", label="Masked Data")
    diagram.edge("C", "D", label="Simulated Coded & Insurance Response")
    diagram.edge("D", "E", label="Map PII Back", style="dotted") # Dotted line from D to E
    diagram.edge("D", "F", label="Payment/Denial/Feedback", arrowhead="normal") # Arrow from D to F

    # Force D and E into a new row
    with diagram.subgraph() as s:
        s.attr(rank="same")
        s.node("D")
        s.node("E")
    
    return diagram

# ---------------------------------------------
# Streamlit UI
# ---------------------------------------------

st.set_page_config(
    page_title="Astra Patient PII Redaction Demo",
    page_icon="🧬",
    layout="centered",
)
st.title("🏥 Astra Demo for Patient Data Processing & PII Masking")
st.subheader("Named-Entity Recognition (NER) via Regex Based similar to NLP model, can be enhanced with AI models on need basis")
# Display a logo from a local file
st.logo("Astra_logo.png", size="large")

st.graphviz_chart(render_workflow_diagram())

# ---------------------------------------------
# Streamlit interactive UI
# ---------------------------------------------
# Step 1: Editable hospital data
with st.expander("1️⃣ Enter or Modify Hospital Data"):
    default_json = json.dumps(default_hospital_data, indent=2)
    user_input = st.text_area("Modify patient records as JSON:", default_json, height=300)
    if st.button("➡️ Submit Hospital Data"):
        try:
            parsed_data = json.loads(user_input)
            st.session_state["parsed_data"] = parsed_data
            st.session_state["masked_data"] = mask_pii(parsed_data)
            st.success("✅ Hospital data submitted successfully. Now click on the next tab 2️⃣ Masked Data Sent to Coding Company")
        except Exception as e:
            st.error(f"❌ Invalid JSON format: {e}")

# Step 2: Masked data (if available)
if "masked_data" in st.session_state:
    with st.expander("2️⃣ Masked Data Sent to Coding Company"):
        st.json(st.session_state["masked_data"])
        if st.button("➡️ Simulate Coding/Insurance Response"):
            st.session_state["insurance_response"] = simulate_insurance_response(st.session_state["masked_data"])
            st.success("✅ Simulated the response from Coding/Insurance company successfully. Now click on the next tab 3️⃣ Simulated Coded Company and Insurance Billing Response")

# Step 3: Insurance response (if available)
if "insurance_response" in st.session_state:
    with st.expander("3️⃣ Simulated Coded Company and Insurance Billing Response"):
        st.json(st.session_state["insurance_response"])
        if st.button("➡️ Click to view Re-mapped data"):
            st.session_state["final_data"] = remap_to_pii(st.session_state["insurance_response"])
            st.success("✅ Re-stitched all the data successfully. Now click on the next tab 4️⃣ View Remapped Data")

# Step 4: Final remapping (if available)
if "final_data" in st.session_state:
    with st.expander("4️⃣ View Remapped Data"):
        st.json(st.session_state["final_data"])
        st.success("🎉 Data remapped successfully with PII restored! ")
        st.info("➡️ Next Steps: Working with Insurance Company for Further Approval Process. \n End of Demo; Thanks for following all the steps :)")

########
# ---------------------------------------------
# End of Streamlit UI
# ---------------------------------------------

