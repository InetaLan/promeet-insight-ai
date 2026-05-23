from pathlib import Path
import tempfile
import streamlit as st

from promeet.pipeline import process_transcript
from promeet.jira_mapper import to_jira_payload

import sys

sys.path.append(str(Path(__file__).parent / "src"))

st.set_page_config(page_title="ProMeet Insight AI MVP", layout="wide")

st.title("ProMeet Insight AI — MVP Demo")
st.caption("Transcript → AI tasks → JSON validation → Human approval → Jira-ready payload")

use_openai = st.sidebar.toggle("Use GPT-4o extraction", value=False)
st.sidebar.info("Jei OPENAI_API_KEY nėra nustatytas, sistema naudos rule-based demo fallback.")

uploaded = st.file_uploader("Įkelk MS Teams transcript .docx arba .txt", type=["docx", "txt"])

if uploaded:
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    with st.spinner("Analizuojama transkripcija..."):
        result = process_transcript(tmp_path, use_openai=use_openai)

    st.subheader("Validation summary")
    st.json(result.validation_summary)

    st.subheader("AI sugeneruotos užduotys")
    if not result.tasks:
        st.warning("Užduočių nerasta arba transcriptas nepraėjo validacijos.")

    for i, task in enumerate(result.tasks, start=1):
        with st.expander(f"{i}. {task.task_name} — {task.assignee} — confidence {task.confidence_score}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**JSON output**")
                st.json(task.model_dump())
            with col2:
                st.write("**Jira-ready payload**")
                st.json(to_jira_payload(task))

            action = st.radio(
                f"PM veiksmas užduočiai {i}",
                ["Needs review", "Approve", "Reject", "Edit manually in Jira"],
                horizontal=True,
                key=f"action_{i}"
            )
            st.write(f"Pasirinkta: **{action}**")

    st.subheader("Sprendimai")
    st.json([d.model_dump() for d in result.decisions])

    st.subheader("Rizikos")
    st.json(result.risks)
