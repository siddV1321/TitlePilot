import streamlit as st
from pathlib import Path
from title_pilot.parser import extract_packet
from title_pilot.auditor import audit_packet

st.set_page_config(page_title="Title Pilot", page_icon="🚗", layout="wide")

st.title("🚗 Title Pilot")
st.caption("AI-ready title packet auditing for independent auto dealers")

st.info(
    "V0.1 is a document-review prototype. It does not file titles, contact a DMV, "
    "provide legal advice, or guarantee that a packet will be accepted."
)

with st.sidebar:
    st.header("Packet settings")
    state = st.selectbox(
        "Target state",
        ["Unknown", "Florida", "Texas", "California", "Michigan", "Wisconsin", "Missouri", "Other"],
    )
    st.write("V0.1 checks document completeness and internal consistency. State-specific rules are intentionally conservative.")

uploaded = st.file_uploader(
    "Upload a title packet",
    type=["pdf", "txt", "md", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if not uploaded:
    st.markdown("""
### What Title Pilot does

1. **Upload** the documents in a deal packet.
2. **Extract** available text and document metadata.
3. **Audit** for missing information, conflicting values, and obvious completeness issues.
4. **Review** a prioritized checklist before submission.

> Start with one clean packet and one intentionally incomplete packet when testing the MVP.
""")
    st.stop()

packet = extract_packet(uploaded)
result = audit_packet(packet, state)

c1, c2, c3 = st.columns(3)
c1.metric("Documents", result["summary"]["documents"])
c2.metric("Issues", result["summary"]["issues"])
c3.metric("Review status", result["summary"]["status"])

st.divider()

st.subheader("Audit result")
if result["summary"]["status"] == "READY TO REVIEW":
    st.success("🟢 No obvious completeness problems were detected.")
elif result["summary"]["status"] == "NEEDS REVIEW":
    st.warning("🟡 Potential issues were detected. Review the checklist before submission.")
else:
    st.error("🔴 Significant missing information was detected.")

for issue in result["issues"]:
    icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}[issue["severity"]]
    with st.expander(f"{icon} {issue['title']} — {issue['severity'].upper()}"):
        st.write(issue["description"])
        st.write(f"**Recommended action:** {issue['action']}")

st.subheader("Extracted deal data")
st.json(result["record"])

st.subheader("Documents")
for doc in packet["documents"]:
    st.write(f"- **{doc['name']}** — {doc['type']} — {doc['characters']} extracted characters")

report = result["report"]
st.download_button(
    "Download audit report",
    data=report,
    file_name="title_pilot_audit.txt",
    mime="text/plain",
)
