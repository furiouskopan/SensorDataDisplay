#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include <Arduino_LSM6DS3.h>

// Network credentials
const char ssid[] = "Kostovi";
const char pass[] = "kostovi01";

// Server details
char serverAddress[] = "192.168.1.34"; // Flask server IP
int port = 5000; // Flask server port

WiFiClient wifi;
HttpClient client(wifi, serverAddress, port);

int status = WL_IDLE_STATUS;
const int aqiSensorPin = A0; // AQI sensor analog pin

void setup() {
  Serial.begin(9600);
  Serial.println("Initializing...");

  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    if (status == WL_CONNECTED) {
      Serial.println("Connected to WiFi");
    } else {
      Serial.println("Failed to connect to WiFi. Retrying...");
      delay(10000); // Retry every 10 seconds
    }
  }
}

void loop() {
  float x = 0, y = 0, z = 0;
  float aqiValue = readAqiSensor();

  if (IMU.begin()) {
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
    } else {
      Serial.println("Failed to read acceleration data.");
    }
  } else {
    Serial.println("Failed to initialize IMU sensor.");
  }

  sendData(aqiValue, x, y, z);

  Serial.print("AQI: ");
  Serial.print(aqiValue);
  Serial.print(", X: ");
  Serial.print(x);
  Serial.print(", Y: ");
  Serial.print(y);
  Serial.print(", Z: ");
  Serial.println(z);

  delay(1000); // Send data every second
}

float readAqiSensor() {
  int sensorValue = analogRead(aqiSensorPin);
  float aqiValue = sensorValue * (5.0 / 1023.0);
  // float aqiValue = map(voltage, 0, 5, 0, 500);
  return aqiValue;
}

void sendData(float aqiValue, float x, float y, float z) {
  String postData = "aqiValue=" + String(aqiValue) + "&x=" + String(x) + "&y=" + String(y) + "&z=" + String(z);
  client.beginRequest();
  client.post("/post_data_endpoint");
  client.sendHeader("Content-Type", "application/x-www-form-urlencoded");
  client.sendHeader("Content-Length", postData.length());
  client.beginBody();
  client.print(postData);
  client.endRequest();

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Status code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);
}
