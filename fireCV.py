import cv2
import numpy as np
import paho.mqtt.client as mqtt

# Konfigurasi MQTT
mqtt_broker = "broker.hivemq.com"  # Ganti dengan broker MQTT Anda
mqtt_port = 1883
mqtt_topic = "fire/detected"

# Setup MQTT Client
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)

# Fungsi untuk mendeteksi api
def detect_fire(frame):
    # Konversi frame ke HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Rentang warna untuk api (dapat disesuaikan berdasarkan kondisi)
    lower_fire = np.array([10, 100, 100])  # Batas bawah HSV untuk api
    upper_fire = np.array([20, 255, 255])  # Batas atas HSV untuk api

    
    # Membuat masker berdasarkan rentang warna
    mask = cv2.inRange(hsv_frame, lower_fire, upper_fire)
    
    # Melakukan operasi morfologi untuk menghilangkan noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

# Membuka kamera atau video
cap = cv2.VideoCapture(0)  # Gunakan '0' untuk kamera atau ganti dengan path video

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Deteksi api
    mask = detect_fire(frame)
    
    # Cari kontur pada masker
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Jika kontur ditemukan, tampilkan peringatan dan gambar kotak
    fire_detected = False  # Variabel flag untuk deteksi api
    
    if len(contours) > 0:
        for contour in contours:
            # Abaikan kontur kecil (filter noise)
            if cv2.contourArea(contour) > 500:  # Sesuaikan threshold area
                # Gambar bounding box di sekitar area api
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "FIRE DETECTED!", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                fire_detected = True  # Jika ada kontur besar, api terdeteksi
        
        # Kirim pesan ke broker MQTT jika api terdeteksi
        if fire_detected:
            client.publish(mqtt_topic, "1")  # Kirim "1" untuk menyalakan LED
            print("Api terdeteksi!")
        else:
            client.publish(mqtt_topic, "0")  # Kirim "0" untuk mematikan LED
    
    else:
        # Tidak ada kontur ditemukan, api tidak terdeteksi
        client.publish(mqtt_topic, "0")  # Kirim "0" untuk mematikan LED
        print("Api tidak terdeteksi.")
    
    # Menampilkan frame dengan deteksi
    cv2.imshow("Fire Detection", frame)
    
    # Keluar dengan menekan tombol 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
