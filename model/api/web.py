from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
import io
import numpy as np
import logging
from PIL import Image

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ตรวจสอบว่า TensorFlow ใช้ GPU ได้หรือไม่
physical_devices = tf.config.list_physical_devices("GPU")
if physical_devices:
    try:
        for device in physical_devices:
            tf.config.experimental.set_memory_growth(device, True)
        logging.info(f"✅ ตรวจพบ GPU: {physical_devices}")
    except RuntimeError as e:
        logging.error(f"🚨 เกิดข้อผิดพลาดในการตั้งค่า GPU: {e}")
else:
    logging.warning("⚠️ ไม่พบ GPU ใช้งาน CPU แทน...")

# โหลดโมเดล MobileNetV2
model_path = "model\MobileNet\MobileNetV2_lr0.001_Fold1.keras"
try:
    model = tf.keras.models.load_model(model_path)
    logging.info("✅ โหลดโมเดลสำเร็จ!")
except Exception as e:
    logging.error(f"🚨 โหลดโมเดลล้มเหลว: {e}")
    model = None  # ป้องกันกรณีโมเดลโหลดไม่สำเร็จ

# ฟังก์ชันตรวจสอบไฟล์รูปภาพ (รองรับเฉพาะ .jpg และ .jpeg)
ALLOWED_EXTENSIONS = {"jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/predict", methods=["POST"])
def predict():
    if not model:
        return jsonify({"error": "❌ ไม่สามารถโหลดโมเดลได้ กรุณาตรวจสอบการตั้งค่าเซิร์ฟเวอร์"}), 500

    if "file" not in request.files:
        logging.warning("⚠️ ไม่มีไฟล์ที่อัปโหลด")
        return jsonify({"error": "❌ กรุณาอัปโหลดไฟล์ภาพ"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        logging.warning("⚠️ ไม่ได้เลือกไฟล์")
        return jsonify({"error": "❌ กรุณาเลือกไฟล์ก่อนอัปโหลด"}), 400

    if not allowed_file(file.filename):
        logging.warning(f"⚠️ ประเภทไฟล์ไม่รองรับ: {file.filename}")
        return jsonify({"error": "❌ อัปโหลดได้เฉพาะไฟล์ .JPG เท่านั้น"}), 400

    try:
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # แปลงรูปเป็น 224x224 และ Normalize (0-1)
        image = image.resize((224, 224))
        image_array = np.array(image).astype("float32") / 255.0
        image_array = np.expand_dims(image_array, axis=0)  # เพิ่มมิติสำหรับ batch

        # ทำนายผล
        predictions = model.predict(image_array)
        predictions_list = predictions.tolist()

        logging.info(f"✅ ทำนายสำเร็จสำหรับไฟล์: {file.filename}")
        return jsonify({"predictions": predictions_list})
    
    except Exception as e:
        logging.error(f"🚨 เกิดข้อผิดพลาดระหว่างการทำนาย: {e}")
        return jsonify({"error": f"❌ ไม่สามารถประมวลผลภาพได้: {str(e)}"}), 500

# เสิร์ฟไฟล์ JavaScript ที่ถูกต้อง (แก้ไข MIME Type)
@app.route('/assets/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('assets/js', filename, mimetype='application/javascript')

if __name__ == "__main__":
    app.run(debug=True)
