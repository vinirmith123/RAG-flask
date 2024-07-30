from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename  # Import secure_filename
from utils.pdf_utils import process_pdfs
from utils.vector_utils import create_vector_db, retrieve_and_invoke

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    files = request.files.getlist('pdf_files')

    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Use secure_filename here
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filepath)
        else:
            return jsonify({"error": "Invalid file format"}), 400

    if saved_files:
        # Process PDFs
        documents = process_pdfs(saved_files)
        vectordb = create_vector_db(documents)

        query = request.form.get('query')
        if query:
            response = retrieve_and_invoke(vectordb, query)
            answer = response["answer"]
            context = response["context"]

            return render_template('result.html', query=query, answer=answer, context=context)
        return render_template('index.html', message="PDFs uploaded successfully. Please enter a question.")
    return render_template('index.html', message="No valid PDF files uploaded")

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
