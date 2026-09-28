from .parser import extract_record

def audit_packet(packet: dict, state: str) -> dict:
    text = packet["text"]
    docs = packet["documents"]
    record = extract_record(text)
    issues = []

    if not docs:
        issues.append({
            "severity": "high",
            "title": "No documents supplied",
            "description": "The audit cannot begin without packet documents.",
            "action": "Upload the available title/deal documents."
        })

    if not any(d["type"] == "title" for d in docs):
        issues.append({
            "severity": "high",
            "title": "Title document not detected",
            "description": "No uploaded document was classified as a title document.",
            "action": "Confirm that the title/certificate of title is included."
        })

    if not record["vin"]:
        issues.append({
            "severity": "high",
            "title": "VIN not detected",
            "description": "No 17-character VIN was confidently extracted from the packet.",
            "action": "Verify the VIN manually and ensure it appears consistently across documents."
        })

    if not record["owner"]:
        issues.append({
            "severity": "medium",
            "title": "Owner/buyer not detected",
            "description": "A buyer or owner name could not be confidently extracted.",
            "action": "Verify the owner/buyer fields and signatures on the applicable documents."
        })

    if any(d["type"] == "lien document" for d in docs) and not record["lienholder"]:
        issues.append({
            "severity": "medium",
            "title": "Lienholder information unclear",
            "description": "Lien-related content exists, but a lienholder name was not confidently extracted.",
            "action": "Verify whether a lien exists and whether the required release/perfection evidence is present."
        })

    if any(len(d["text"].strip()) < 15 for d in docs):
        issues.append({
            "severity": "low",
            "title": "Document has little or no extractable text",
            "description": "At least one document may be scanned, image-only, blank, or poorly recognized.",
            "action": "Open the source document and manually verify its contents."
        })

    status = "READY TO REVIEW"
    if any(i["severity"] == "high" for i in issues):
        status = "BLOCKED — MANUAL REVIEW"
    elif issues:
        status = "NEEDS REVIEW"

    report_lines = [
        "TITLE PILOT — AUDIT REPORT",
        "=" * 32,
        f"Target state: {state}",
        f"Status: {status}",
        "",
        "EXTRACTED RECORD",
        "-" * 32,
    ]
    for k, v in record.items():
        report_lines.append(f"{k}: {v or '[not detected]'}")

    report_lines += ["", "ISSUES", "-" * 32]
    if not issues:
        report_lines.append("No obvious completeness issues detected.")
    else:
        for i, issue in enumerate(issues, 1):
            report_lines += [
                f"{i}. [{issue['severity'].upper()}] {issue['title']}",
                f"   {issue['description']}",
                f"   Action: {issue['action']}",
            ]

    return {
        "record": record,
        "issues": issues,
        "summary": {
            "documents": len(docs),
            "issues": len(issues),
            "status": status,
        },
        "report": "\n".join(report_lines),
    }
