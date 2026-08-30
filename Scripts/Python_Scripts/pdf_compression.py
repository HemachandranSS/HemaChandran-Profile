from pypdf import PdfReader, PdfWriter

def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Transfer the page to the writer
        new_page = writer.add_page(page)
        # Compress the text and drawing instructions
        new_page.compress_content_streams() 

    # Instead of manual loops, we use the writer's built-in 
    # capability to compress images/streams during the write process.
    with open(output_path, "wb") as f:
        writer.write(f)

compress_pdf("BiologyTodayApril2026.pdf", "BiologyTodayApril2026Compressed.pdf")
print("Compression complete!")


----------------------------------------------------------------------------------------

import subprocess

def extreme_compress(input_path, output_path):
    # Setting -dPDFSETTINGS to /screen drops images to 72dpi
    # Use /ebook for 150dpi (better balance)
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    subprocess.run(cmd)

extreme_compress("Civil Services Examination Syllabus as on April 2026.pdf", "Civil Services Examination Syllabus as on April 2026-Compressed.pdf")


---------------------------------------------------------------------------------------


import subprocess

def ultra_compress(input_path, output_path):
    cmd = [
        "gs", 
        "-sDEVICE=pdfwrite", 
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",        # Lowers DPI to 72 (Screen Quality)
        "-dAlwaysOptimizeBitmaps=true", # Forces bitmap optimization
        "-dDownsampleColorImages=true", # Resizes color images
        "-dColorImageResolution=72",    # Sets max resolution for color
        "-dGrayImageResolution=72",     # Sets max resolution for grayscale
        "-dMonoImageResolution=72",     # Sets max resolution for monochrome
        "-dCreateJobTicket=false",      # Strips print job info
        "-dPreserveAnnots=false",       # Strips comments/annotations
        "-dEmbedAllFonts=false",        # Avoids embedding full font sets
        "-dSubsetFonts=true",           # Only embeds characters used
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", 
        input_path
    ]
    subprocess.run(cmd)

ultra_compress("BiologyTodayApril2026.pdf", "BiologyToday_UltraTiny.pdf")
print("Extreme compression complete!")
