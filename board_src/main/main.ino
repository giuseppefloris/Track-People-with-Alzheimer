#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

/* Define this "net-conf.h" header with:
      - SSID
      - PASS
      - MQTT_SERVER (name of the mqtt server)
      - MQTT_CH_ID  (channel id)
      - MQTT_PORT
 */
#include "net-conf.h"

/* Sensors pins*/
#define BPM_SENSOR  0
#define GPS_RX      4
#define GPS_TX      3
#define GPS_BAUD    9600

/* Debug variables */
#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#define MQTT_CONNECT false


/* Global variables */
float bpm_read;
float lat, lng;
int   wifi_strength;

/* Globa objects */
WiFiClient nodeClient;
PubSubClient mqttClient(nodeClient);

TinyGPSPlus gps;
SoftwareSerial serialGPS(GPS_RX, GPS_TX);

void setup() {
  DEBUG_SERIAL.begin(115200);
  serialGPS.begin(GPS_BAUD);

  DEBUG_SERIAL.println();
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

  delay(2000);

  /* Setting MQTT server */
  #if MQTT_CONNECT == true
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  #endif

  delay(2000);
}

int getWifiQuality() {
  if (WiFi.status() != WL_CONNECTED)
    return -1;

  int dBm = WiFi.RSSI();
  if (dBm <= -100)
    return 0;

  return 2 * (dBm + 100);
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
  
  /* Retrieving sensors' readings */

  // BPM sensor (raw value)
  bpm_read = analogRead(BPM_SENSOR);
  // TODO: add a simple pre-processing to check if the reading is ok or not
  DEBUG_SERIAL.println(bpm_read);

  // GPS coordinates reading
  while (serialGPS.available() > 0)
  {
    DEBUG_SERIAL.print("There is something for the gps!");
    gps.encode(serialGPS.read());

    if (gps.location.isValid())
    {
      lat = gps.location.lat();
      lng = gps.location.lng();
      DEBUG_SERIAL.print("Lat= ");
      DEBUG_SERIAL.println(lat, 6);
      DEBUG_SERIAL.print("Lng= ");
      DEBUG_SERIAL.println(lng, 6);
    }
  }

  // WiFi strength (RSSI in dBm)  
  // wifi_strength = getWifiQuality();
  wifi_strength = WiFi.RSSI();
  DEBUG_SERIAL.print("WiFi strength: ");
  DEBUG_SERIAL.println(wifi_strength);

  delay(20);
}

 
