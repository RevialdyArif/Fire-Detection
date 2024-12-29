#include <WiFi.h>
#include <PubSubClient.h>  // Library untuk MQTT

// Konfigurasi WiFi
const char* ssid = "Wokwi-GUEST";  
const char* password = "";

// Konfigurasi MQTT Broker
const char* mqtt_server = "broker.hivemq.com"; // Ganti dengan broker MQTT Anda
const int mqtt_port = 1883;

// Pin LED
#define LED_PIN 12

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // Matikan LED di awal

  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  // Koneksi ke Broker MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Pastikan terkoneksi ke MQTT
  while (!client.connected()) {
    if (client.connect("ESP32_Client")) {
      Serial.println("Connected to MQTT Broker!");
      client.subscribe("fire/detected"); // Subscribe ke topik fire/detected
    } else {
      delay(1000);
      Serial.print(".");
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message received: " + message);

  // Menyalakan/mematikan LED berdasarkan pesan
  if (message == "1") {
    digitalWrite(LED_PIN, HIGH); // Nyalakan LED
  } else if (message == "0") {
    digitalWrite(LED_PIN, LOW); // Matikan LED
  }
}

void loop() {
  client.loop();  // Membaca pesan MQTT yang masuk
}
