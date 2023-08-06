#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>

const char* ssid = "ssid";
const char* pass = "pass";
// const char* mqtt_server = "broker.mqttdash.com";

WiFiClient esp_client;
PubSubClient client(esp_client);

/* Serial communication objects */
SoftwareSerial bpm_serial(5,6);  // RX, TX

void connectWifi()
{
  Serial.println("ESP8266 connecting to WiFi...");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("ESP8266 connected!");
}

void setup()
{
  Serial.begin(115200);
  Serial.println("ESP8266 started");

  connectWifi();
  /* TODO: setup MQTT connection */
  
  Serial.println("ESP8266 starting serial comm. with arduino");
  bpm_serial.begin(9600);
}

void loop()
{
  String bpm_reading = "";
  
  if (WiFi.status() !=  WL_CONNECTED)
  {
    connectWifi();
  }

  /* Retrieving data from arduino */
  if (bpm_serial.available())
  {
    bpm_reading = bpm_serial.readStringUntil('\n');
    Serial.print("Received bpm from arduino: ");
    Serial.println(bpm_reading);
  }
}
