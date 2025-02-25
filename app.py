# app.py - Main Flask Application

import os
import cv2
import time
import sqlite3
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('patient_records.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        height REAL,
        pulse INTEGER,
        temperature REAL,
        timestamp TEXT,
        day TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# Global variables for OpenCV processing
camera = None
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
patient_data = {
    "height": None,
    "pulse": None,
    "temperature": None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_capture', methods=['POST'])
def start_capture():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    
    # Reset patient measurements
    patient_data["height"] = None
    patient_data["pulse"] = None
    patient_data["temperature"] = None
    
    return jsonify({"status": "Capture started"})

@app.route('/stop_capture', methods=['POST'])
def stop_capture():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    
    # Simulate measurements if they weren't detected
    if patient_data["height"] is None:
        patient_data["height"] = round(np.random.uniform(150, 190), 1)  # height in cm
    if patient_data["pulse"] is None:
        patient_data["pulse"] = int(np.random.uniform(60, 100))  # pulse in bpm
    if patient_data["temperature"] is None:
        patient_data["temperature"] = round(np.random.uniform(36.0, 37.5), 1)  # temp in celsius
    
    return jsonify(patient_data)

def process_frame(frame):
    # Detect face for height estimation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        ratio = 0.8
        # Estimate height (in a real app, you would calibrate this)
        # This is a simplified simulation
        if patient_data["height"] is None:
            # Simulate height based on face size and camera position
            patient_data["height"] =  round(h * ratio, 1)  # Simple estimation
        # Simulate pulse detection from facial color changes
        # In a real app, this would analyze color changes over time
        if patient_data["pulse"] is None:
            # ROI for pulse detection (forehead area)
            forehead = frame[y:y+int(h*0.3), x:x+w]
            if len(forehead) > 0:
                # Simple simulation, a real implementation would track color changes over time
                mean_color = np.mean(forehead)
                # Simulate pulse based on color variations
                patient_data["pulse"] = int(70 + (mean_color % 30))
        
        # Simulate temperature detection
        # In real applications, this would use thermal imaging or external sensors
        if patient_data["temperature"] is None:
            # Simple simulation for demonstration
            patient_data["temperature"] = round(36.5 + np.random.uniform(0, 1.0), 1)
    
    # Add information text to the frame
    cv2.putText(frame, f"Height: {patient_data['height'] if patient_data['height'] else 'Measuring...'} cm", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Pulse: {patient_data['pulse'] if patient_data['pulse'] else 'Measuring...'} bpm", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Temp: {patient_data['temperature'] if patient_data['temperature'] else 'Measuring...'} °C", 
                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame

def generate_frames():
    global camera
    while True:
        if camera is None:
            # If camera is not initialized, return a blank frame
            blank_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
            cv2.putText(blank_frame, "Camera Off", (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            break
        else:
            # Process the frame for biometric measurements
            frame = process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_record', methods=['POST'])
def save_record():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    height = patient_data.get('height')
    pulse = patient_data.get('pulse')
    temperature = patient_data.get('temperature')
    
    # Get current time and day
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    day = now.strftime("%A")
    
    # Save to database
    conn = sqlite3.connect('patient_records.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO patients (name, age, height, pulse, temperature, timestamp, day)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, height, pulse, temperature, timestamp, day))
    
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success", 
        "id": patient_id,
        "name": name,
        "age": age,
        "height": height,
        "pulse": pulse,
        "temperature": temperature,
        "timestamp": timestamp,
        "day": day
    })

@app.route('/get_records')
def get_records():
    conn = sqlite3.connect('patient_records.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    records = [dict(row) for row in rows]
    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True)