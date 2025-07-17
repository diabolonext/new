
from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "news.json"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 初始化資料夾和檔案
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/get_news", methods=["GET"])
def get_news():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/add_news", methods=["POST"])
def add_news():
    data = request.json
    new_data = {
        "title": data.get("title"),
        "content": data.get("content"),
        "image": data.get("image"),
        "time": datetime.now().isoformat()
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "success", "message": "新聞已更新"})

@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "未提供圖片"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "未選擇圖片"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return jsonify({"status": "success", "filename": filename})
    return jsonify({"status": "error", "message": "不支援的圖片格式"}), 400

@app.route("/delete_news", methods=["POST"])
def delete_news():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return jsonify({"status": "success", "message": "新聞已刪除"})
    else:
        return jsonify({"status": "error", "message": "找不到新聞檔案"}), 404


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
