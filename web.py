from pdfminer.high_level import extract_text
import re
import multiprocessing

# Function to extract text from a PDF chunk
def extract_text_from_pdf_chunk(pdf_path, start_page, end_page):
    text = extract_text(pdf_path, page_numbers=range(start_page, end_page))
    return text

# Parse MCQs from extracted text
def parse_mcqs(text):
    pattern = r'\d+\.\s*(.*?)\n((?:\([A-D]\).*?\n?)+)Answer:\s*\((.*?)\)'
    matches = re.findall(pattern, text, re.S)
    return matches
    
# Generate HTML from MCQs
def generate_html(mcqs):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCQ Viewer</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div class="container">
            <h1>MCQ Viewer</h1>
    """
    for i, (question, options, answer) in enumerate(mcqs, 1):
        options_html = ''.join([f'<li>{opt.strip()}</li>' for opt in options.splitlines() if opt])
        html += f"""
        <div class="mcq">
            <h3>Question {i}.</h3>
            <p>{question.strip()}</p>
            <ul>{options_html}</ul>
            <button onclick="toggleAnswer({i})">Show Answer</button>
            <p class="answer" id="answer{i}" style="display:none;">Answer: ({answer})</p>
        </div>
        """
    html += """
        </div>
        <script>
            function toggleAnswer(id) {
                const answer = document.getElementById(`answer${id}`);
                answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
            }
        </script>
    </body>
    </html>
    """
    return html

# Function to handle chunking and parallel processing
def process_pdf_in_chunks(pdf_path, num_chunks):
    # Determine total number of pages in the PDF (you can adjust based on the PDF's page count)
    from pdfminer.pdfpage import PDFPage
    with open(pdf_path, 'rb') as f:
        total_pages = len(list(PDFPage.get_pages(f)))

    # Divide the PDF into chunks
    chunk_size = total_pages // num_chunks
    chunks = [(i * chunk_size, min((i + 1) * chunk_size, total_pages)) for i in range(num_chunks)]

    # Use multiprocessing to process chunks in parallel
    with multiprocessing.Pool() as pool:
        texts = pool.starmap(extract_text_from_pdf_chunk, [(pdf_path, start, end) for start, end in chunks])

    # Combine all extracted text
    full_text = ''.join(texts)
    return full_text

# Main function to run the process
def main(pdf_path, output_html, num_chunks=4):
    print("Starting PDF extraction in chunks...")
    full_text = process_pdf_in_chunks(pdf_path, num_chunks)
    print("Text extraction complete.")
    
    mcqs = parse_mcqs(full_text)
    if not mcqs:
        print("No MCQs found. Please check the regex or extracted text.")
    else:
        print(f"{len(mcqs)} MCQs extracted.")
    
    html_content = generate_html(mcqs)
    with open(output_html, 'w') as file:
        file.write(html_content)
    print(f"HTML generated and saved as {output_html}")

# Example usage
# main('mcq_file.pdf', 'index.html')

main('combined_output.pdf', 'index.html')
