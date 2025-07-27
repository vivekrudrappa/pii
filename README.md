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
- Simulated insurance response generation.
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
4. **Receive Insurance Response:** Collect insurance responses (billing codes, limits, co-payments) linked by UUID.
5. **PII Remapping:** Restore original PII using stored mappings and UUIDs, reconstructing the full patient record.
6. **Return to Hospital:** Send the final, remapped data back to the hospital.
This prototype demonstrates the workflow using regex-based masking, but can be enhanced with Gen AI/NLP models for production use.
