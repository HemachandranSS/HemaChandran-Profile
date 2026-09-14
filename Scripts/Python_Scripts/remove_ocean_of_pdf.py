import fitz
import os
import tempfile
import shutil

ROOT_DIR = "./"  # change this

def clean_pdf_in_place(pdf_path):
    doc = fitz.open(pdf_path)

    modified = False

    for page in doc:
        instances = page.search_for("OceanofPDF.com")
        #www.it-ebooks.info
        #instances = page.search_for("www.it-ebooks.info")
        if instances:
            modified = True
            for inst in instances:
                page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

    if modified:
        # write to temp file first (prevents corruption)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_path = tmp.name

        doc.save(temp_path, deflate=True)
        doc.close()

        shutil.move(temp_path, pdf_path)  # overwrite original
        print(f"✔ Cleaned: {pdf_path}")
    else:
        doc.close()
        print(f"— No watermark: {pdf_path}")

for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.lower().endswith(".pdf"):
            clean_pdf_in_place(os.path.join(root, file))

