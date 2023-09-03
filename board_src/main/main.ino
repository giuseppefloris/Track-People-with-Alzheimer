/*
  Luca Scionis - Tracking People with Alzheimer: code for NodeMCU sending data to the platform
  Last Update: 27/08/23
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

/* Define this "net-conf.h" header with:
      - SSID
      - PASS
      - MQTT_SERVER (name of the mqtt server)
      - MQTT_PORT
 */
#include "net-conf.h"

/* Sensors pins*/
#define GPS_RX      0
#define GPS_TX      2
#define GPS_BAUD    9600

/* Debug variables */
#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#define WIFI_CONNECT  true
#define MQTT_CONNECT  true

/* Global vars */
String clientId = "";
String rootTopic = "Device";

/* Global objects*/
WiFiClient nodeClient;
PubSubClient mqttClient(nodeClient);

TinyGPSPlus gps;
SoftwareSerial serialGPS(GPS_RX, GPS_TX);

char* toCharArray(String str) {
  return &str[0];
}

void mqtt_reconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    DEBUG_SERIAL.print("Attempting MQTT connection...");
    byte mac[5]; // create client ID from mac address
    WiFi.macAddress(mac); // get mac address
    clientId = String(mac[0]) + String(mac[4]); // use mac address to create clientID
    DEBUG_SERIAL.print("ClientId: ");
    DEBUG_SERIAL.println(clientId);
    // Attempt to connect
    // if (mqttClient.connect(clientId.c_str(), "user", "pass")) {
    if (mqttClient.connect(clientId.c_str())) {
      DEBUG_SERIAL.println("connected");
      rootTopic = rootTopic + "/" + clientId + "/";
    } else {
      DEBUG_SERIAL.print("failed, rc=");
      DEBUG_SERIAL.print(mqttClient.state());
      DEBUG_SERIAL.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


void setup() {
  /* Initializing serial and I2C communication */
  DEBUG_SERIAL.begin(9600);
  delay(3000);

  /* Setting WiFi connection (if enabled) */
  #if WIFI_CONNECT
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
  #endif

  /* Setting MQTT server (if enabled) */
  #if MQTT_CONNECT == true
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  #endif

  /* Sensors setup */
  DEBUG_SERIAL.println("Setting up sensors...");
  serialGPS.begin(GPS_BAUD);

  DEBUG_SERIAL.println("Setup completed: starting the device operations...");
  delay(1000);
}


void loop()
{
  if (!mqttClient.connected()) {
    DEBUG_SERIAL.println("Reconnecting to MQTT server...");
    mqtt_reconnect();
  }
  mqttClient.loop();

  float   gps_coordinates[2];
  int     wifi_strength = 0;
  uint8_t gps_flag = 0;

  for(int j = 0; j < 2; j++)
    gps_coordinates[j] = 0.0;


  // GPS coordinates reading
  while (serialGPS.available() > 0 && gps_flag == 0)
  {
    gps.encode(serialGPS.read());

    if (gps.location.isValid())
    {
      gps_coordinates[0] = gps.location.lat();
      gps_coordinates[1] = gps.location.lng();

      DEBUG_SERIAL.print("Lat= ");
      DEBUG_SERIAL.println(gps_coordinates[0], 6);
      DEBUG_SERIAL.print("Lng= ");
      DEBUG_SERIAL.println(gps_coordinates[1], 6);


      gps_flag = 1;
    }
  }
  // DEBUG_SERIAL.println();

  // WiFi strength (RSSI in dBm)
  wifi_strength = WiFi.RSSI();
  /*
  DEBUG_SERIAL.print("WiFi strength: ");
  DEBUG_SERIAL.println(wifi_strength);
  DEBUG_SERIAL.println();
  */


  /* Sending data to the platform */

  DEBUG_SERIAL.print("Sending data to the platform...");
  DEBUG_SERIAL.println();

  /*
  DEBUG_SERIAL.print("GPS coords: ");
  DEBUG_SERIAL.println(gps_coordinates[i][0]);
  DEBUG_SERIAL.println(gps_coordinates[i][1]);
  */

  String wifi_strength_s = String(wifi_strength);
  #if MQTT_CONNECT
    mqttClient.publish(toCharArray(rootTopic + wifi_topic), toCharArray(wifi_strength_s));
  #endif

  #if MQTT_CONNECT
    String gps_lat_s = String(gps_coordinates[0], 6);
    String gps_lng_s = String(gps_coordinates[1], 6);
    String gps_s = gps_lat_s + "," + gps_lng_s;

    mqttClient.publish(toCharArray(rootTopic + gps_topic), toCharArray(gps_s));
  #endif

  /*
  DEBUG_SERIAL.print("Wifi strength: ");
  DEBUG_SERIAL.println(wifi_strengths[i]);

  DEBUG_SERIAL.print("MPU angles: ");
  DEBUG_SERIAL.println();
  */


  // DEBUG_SERIAL.println();
  delay(2000);
}


