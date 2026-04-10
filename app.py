from flask import Flask, request, jsonify
import PyPDF2

app = Flask(__name__)

@app.route('/')
def home():
    return "QS MASTER VISION AI: SYSTEM ONLINE. THE ENGINEER HAS HIS GLASSES AND IS READY TO READ."

@app.route('/read-pdf', methods=['POST'])
def read_pdf():
    # Check if a file was sent
    if 'file' not in request.files:
        return jsonify({"error": "No file provided. Please hand me a document!"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file. The document is blank!"}), 400

    try:
        # Put on the glasses and read the PDF
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        
        # Hand the extracted text back to the boss
        return jsonify({"success": True, "extracted_text": text})
    
    except Exception as e:
        return jsonify({"error": f"I had trouble reading that: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
