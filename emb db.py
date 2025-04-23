from deepface import DeepFace
import os
import mysql.connector
import numpy as np
import cv2
import base64

# --- إعداد الاتصال بقاعدة البيانات ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="attendance_db"
)
cursor = conn.cursor()

# --- مسار مجلد الصور ---
database_path = r"C:\Users\MCC\Desktop\New folder (4)\pic"

# --- دالة استخراج الإيمبيدينغ وتخزينه مع الصورة ---
def save_embeddings_and_images_from_folder(folder_path):
    for image_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_name)

        if os.path.isfile(image_path) and image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            person_name = os.path.splitext(image_name)[0]

            # التأكد من عدم وجود الاسم مسبقًا
            cursor.execute('SELECT COUNT(*) FROM persons WHERE name = %s', (person_name,))
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"⚠️ الاسم '{person_name}' موجود مسبقًا. تم تخطي الصورة {image_name}.")
                continue

            try:
                # استخراج الإيمبيدينغ
                result = DeepFace.represent(img_path=image_path, model_name="ArcFace", enforce_detection=False)

                if result:
                    embedding = np.array(result[0]["embedding"], dtype=np.float32)

                    if embedding.shape[0] != 512:
                        print(f"❌ تخطي الصورة {image_name}: حجم الإيمبيدينغ {embedding.shape[0]} ليس 512.")
                        continue

                    embedding_blob = embedding.tobytes()

                    # قراءة الصورة وتحويلها إلى Base64
                    img = cv2.imread(image_path)
                    _, buffer = cv2.imencode('.jpg', img)
                    img_base64 = base64.b64encode(buffer).decode('utf-8')

                    # تخزين الاسم والإيمبيدينغ والصورة في قاعدة البيانات
                    cursor.execute(
                        'INSERT INTO persons (name, embedding, image) VALUES (%s, %s, %s)',
                        (person_name, embedding_blob, img_base64)
                    )
                    conn.commit()

                    print(f"✅ تم استخراج وتخزين الإيمبيدينغ والصورة للصورة: {image_name}")
                else:
                    print(f"⚠️ لم يتم العثور على وجه في الصورة: {image_name}")

            except Exception as e:
                print(f"❌ خطأ أثناء معالجة الصورة {image_name}: {e}")

# --- تنفيذ ---
save_embeddings_and_images_from_folder(database_path)

# --- إنهاء الاتصال ---
cursor.close()
conn.close()

print("🎯 تم استخراج وتخزين جميع الإيمبيدينغات والصور بنجاح!")
