import mysql.connector
import numpy as np
import os
from datetime import datetime

# إعدادات الاتصال بقاعدة البيانات
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'attendance_db'
}

# إنشاء اتصال
conn = mysql.connector.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password']
)
cursor = conn.cursor()

# إنشاء قاعدة البيانات إذا مش موجودة
cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_db")
conn.database = db_config['database']

# إنشاء جدول الأشخاص (اسم + إيمبيدينغ)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS persons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        embedding LONGBLOB NOT NULL
    )
''')

# إنشاء جدول الحضور (اسم + وقت + حالة الحضور + الصورة)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_name VARCHAR(255) NOT NULL,
        match_time DATETIME NOT NULL,
        status VARCHAR(50) NOT NULL,
        captured_image LONGBLOB
    )
''')

# إنشاء جدول المحاضرات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lectures (
        id INT AUTO_INCREMENT PRIMARY KEY,
        lecture_name VARCHAR(255) NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        date DATE NOT NULL,
        location VARCHAR(255)
    )
''')

# إنشاء جدول ربط الطلاب بالمحاضرات
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lecture_students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        lecture_id INT NOT NULL,
        person_name VARCHAR(255) NOT NULL,
        FOREIGN KEY (lecture_id) REFERENCES lectures(id) ON DELETE CASCADE
    )
''')

conn.commit()
conn.close()

# --- دوال للمساعدة ---

def save_person(name, embedding_array):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    embedding_blob = embedding_array.tobytes()
    sql = 'INSERT INTO persons (name, embedding) VALUES (%s, %s)'
    cursor.execute(sql, (name, embedding_blob))

    conn.commit()
    conn.close()

def insert_attendance(person_name, status, captured_image_path):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    with open(captured_image_path, 'rb') as f:
        img_blob = f.read()

    match_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = 'INSERT INTO attendance (person_name, match_time, status, captured_image) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (person_name, match_time, status, img_blob))

    conn.commit()
    conn.close()
