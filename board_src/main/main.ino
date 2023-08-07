#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

/* Sensors pins*/
#define BPM_SENSOR  0
#define GPS_RX      4
#define GPS_TX      3
#define GPS_BAUD    9600

/* Net conf */
#define SSID        "ssid"
#define PASS        "pass"
#define MQTT_SERVER "broker.mqtt.com"
#define MQTT_CH_ID  0
#define MQTT_PORT   1883

/* Debug variables */
#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#define MQTT_CONNECT false


/* Global variables */
float bpm_read = 0.0;
float lat, lng;

WiFiClient nodeClient;
PubSubClient mqttClient(nodeClient);

TinyGPSPlus gps;
SoftwareSerial gps_s(GPS_RX, GPS_TX);

void setup() {
  DEBUG_SERIAL.begin(115200);
  DEBUG_SERIAL.println();

  gps_s.begin(GPS_BAUD);
  delay(3000);

  /* Setting WiFi connection */
  WiFi.begin(SSID, PASS);

  DEBUG_SERIAL.print("Connecting...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    DEBUG_SERIAL.print(".");
  }

  DEBUG_SERIAL.println();
  DEBUG_SERIAL.print("Connected, IP address: ");
  DEBUG_SERIAL.println(WiFi.localIP());

  /* Setting MQTT server */
  #if MQTT_CONNECT == true
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  #endif
}

void loop()
{
  
  #if MQTT_CONNECT == true
    if (!mqttClient.connected())
    {
      DEBUG_SERIAL.print("Attempting MQTT connection...");

      // Create a random client ID
      String clientId = "ESP8266-";
      clientId += String(random(0xffff), HEX);
      // Attempt to connect
      if (client.connect(clientId.c_str()))
      {
        DEBUG_SERIAL.println("connected");
      }
      else
      {
        DEBUG_SERIAL.print("failed, rc=");
        DEBUG_SERIAL.print(client.state());
        DEBUG_SERIAL.println(" try again in 5 seconds");
        // Wait 5 seconds before retrying
        delay(5000);
      }
    }
  #endif
  
  // Retrieve sensors' readings
  // bpm
  bpm_read = analogRead(BPM_SENSOR);
  // TODO: add a simple pre-processing to check if the reading is ok or not
  DEBUG_SERIAL.println(bpm_read);

  while (gps_s.available() > 0)
  {
    gps.encode(gps_s.read());
  }

  if (gps.location.isUpdated())
  {
    lat = gps.location.lat();
    lng = gps.location.lng();
    DEBUG_SERIAL.print("Lat= ");
    DEBUG_SERIAL.println(lat, 6);
    DEBUG_SERIAL.print("Lng= ");
    DEBUG_SERIAL.println(lng, 6);
  }

  delay(20);
}

 
