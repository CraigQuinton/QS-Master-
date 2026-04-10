from flask import Flask, request, jsonify
import PyPDF2

app = Flask(__name__)

@app.route('/')
def home():
    # This builds the visual "Drop-off Counter" on your website!
    return '''
    <html>
        <body style="font-family: Arial; padding: 50px; background-color: #f4f4f9;">
            <h2 style="color: #333;">QS MASTER VISION AI: SYSTEM ONLINE</h2>
            <p>The Site Engineer has his glasses. Hand him a PDF to read:</p>
            
            <form action="/read-pdf" method="post" enctype="multipart/form-data" style="margin-top: 20px;">
                <input type="file" name="file" accept=".pdf" style="margin-bottom: 20px; font-size: 16px;"><br>
                <input type="submit" value="READ MY PDF" style="padding: 15px 30px; background-color: #28a745; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer;">
            </form>
        </body>
    </html>
    '''

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
