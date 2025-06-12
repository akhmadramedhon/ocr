from fileinput import filename
import os
import cv2
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, redirect
from model.ocr import validate_nik as vn, extract_data as ed
from flask_cors import CORS

app  = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = 'pdf', 'png', 'jpg', 'jpeg'
UPLOAD_FOLDER = 'images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/extract-ktp", methods=["POST"])
def extract_ktp():
    if 'image' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if allowed_file(file.filename):
        # Save file to local storage/folder
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        try:
            process_img = cv2.imread(save_path,0)
            data = ed(process_img)
            return  jsonify(
                {
                    "message" : "Data extract successfully",
                    "data": data
                })
        except Exception as e:
            return jsonify({"message":f"Error processing image: {str(e)}"}), 500
    else:
        return jsonify({"message": "Invalid file type"})

@app.route("/validate-nik", methods=["POST"])
def validate_nik():
    if 'image' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)
    if allowed_file(file.filename):
        # Save file to local storage/folder
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        try:
            process_img = cv2.imread(save_path,0)
            res = vn(process_img)
            if res:
                return jsonify({"message": "NIK valid"}) 
            else: 
                return jsonify({"message": "NIK tidak valid"})
        except Exception as e:
            return jsonify({"message": f"Error processing image: {str(e)}"}), 500
    else:
        return jsonify({"message": "Invalid file type"})



""" FOR DEVELOPMENT PURPOSE
    Code below used for further development. Use it by uncomment the code
"""
""" Endpoint -> /upload
    Keyword arguments:
    images -- multipart/form-data
    Return: response message that file uploaded to images folder.
"""
""
# @app.route("/upload", methods=["POST"])
# def validate_nik():
#     file = request.files['image']
#     if file.filename == '':
#         return redirect(request.url)
#     if allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(UPLOAD_FOLDER, filename))
#         response = {
#             "message":"Data Uploaded successfully",
#             "filename": filename
#         }
#     else:
#         response = {
#             "message": "Invalid file type"
#         }
#     return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)