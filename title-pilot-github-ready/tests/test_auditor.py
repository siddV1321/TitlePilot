from title_pilot.auditor import audit_packet

def test_missing_vin_is_high():
    packet = {
        "text": "Certificate of Title\nYear: 2023\nMake: Example\nModel: Sedan",
        "documents": [
            {"name": "title.txt", "type": "title", "text": "Certificate of Title", "characters": 21}
        ],
    }
    result = audit_packet(packet, "Florida")
    titles = [x["title"] for x in result["issues"]]
    assert "VIN not detected" in titles
    assert result["summary"]["status"] == "BLOCKED — MANUAL REVIEW"

def test_clean_minimal_packet():
    packet = {
        "text": "Certificate of Title\nVIN: 1HGCM82633A123456\nOwner: Example Dealer",
        "documents": [
            {"name": "title.txt", "type": "title", "text": "Certificate of Title", "characters": 21}
        ],
    }
    result = audit_packet(packet, "Unknown")
    assert result["summary"]["issues"] == 0
    assert result["summary"]["status"] == "READY TO REVIEW"
