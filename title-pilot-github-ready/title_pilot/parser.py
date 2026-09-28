from io import BytesIO
import re

def _pdf_text(data: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""

def _ocr_image(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
        image = Image.open(BytesIO(data))
        return pytesseract.image_to_string(image)
    except Exception:
        return ""

def classify(name: str, text: str) -> str:
    s = f"{name} {text[:3000]}".lower()
    if "title" in s or "certificate of title" in s:
        return "title"
    if "lien" in s or "lienholder" in s:
        return "lien document"
    if "bill of sale" in s:
        return "bill of sale"
    if "odometer" in s or "mileage" in s:
        return "odometer disclosure"
    if "release" in s:
        return "release"
    return "unknown"

def extract_packet(uploaded_files) -> dict:
    documents = []
    combined = []

    for f in uploaded_files:
        data = f.getvalue()
        suffix = f.name.lower().rsplit(".", 1)[-1] if "." in f.name else ""
        if suffix == "pdf":
            text = _pdf_text(data)
        elif suffix in {"png", "jpg", "jpeg"}:
            text = _ocr_image(data)
        else:
            text = data.decode("utf-8", errors="ignore")

        doc = {
            "name": f.name,
            "type": classify(f.name, text),
            "text": text,
            "characters": len(text),
        }
        documents.append(doc)
        combined.append(f"\n--- {f.name} ---\n{text}")

    return {
        "documents": documents,
        "text": "\n".join(combined),
    }

def find_first(patterns, text):
    for pattern in patterns:
        m = re.search(pattern, text, re.I | re.M)
        if m:
            return m.group(1).strip()
    return None

def extract_record(text: str) -> dict:
    vin = find_first([
        r"\bVIN\b\s*[:#]?\s*([A-HJ-NPR-Z0-9]{17})\b",
        r"\b([A-HJ-NPR-Z0-9]{17})\b",
    ], text)

    year = find_first([r"\b(?:model\s*)?year\b\s*[:#]?\s*(20\d{2})"], text)
    make = find_first([r"\bmake\b\s*[:#]?\s*([A-Za-z0-9 ._-]+)"], text)
    model = find_first([r"\bmodel\b\s*[:#]?\s*([A-Za-z0-9 ._-]+)"], text)
    owner = find_first([r"\b(?:owner|buyer|purchaser)\b\s*[:#]?\s*([^\n]+)"], text)
    lienholder = find_first([r"\b(?:lienholder|lien holder)\b\s*[:#]?\s*([^\n]+)"], text)

    return {
        "vin": vin,
        "year": year,
        "make": make,
        "model": model,
        "owner": owner,
        "lienholder": lienholder,
    }
