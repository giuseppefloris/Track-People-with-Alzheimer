/*
  Luca Scionis - Tracking People with Alzheimer: code for NodeMCU sending data to the platform
  Last Update: 10/08/23
*/

#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

#include <MPU9250.h>

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

#define WIFI_CONNECT  true
#define MQTT_CONNECT  false
#define CALIBRATE_MPU true

#define DATA_BUFFER 5

/* Global variables */
float bpm_read;
float lat, lng;
int   wifi_strength;
float yaw, pitch, roll;

int gps_flag = 0;
int buffer_i = 0;

/* Global objectse*/
WiFiClient nodeClient;
PubSubClient mqttClient(nodeClient);

TinyGPSPlus gps;
SoftwareSerial serialGPS(GPS_RX, GPS_TX);

MPU9250 mpu;


void setup() {
  /* Initializing serial and I2C communication */
  DEBUG_SERIAL.begin(115200);
  Wire.begin();
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
    while (!mqttClient.connect(MQTT_BROKER, MQTT_PORT))
    {
      DEBUG_SERIAL.print("MQTT connection failed! Error code = ");
      DEBUG_SERIAL.println(mqttClient.connectError());

      delay(500);
      // TODO: may insert a max number of trials, if exceeded exits the program
    }
    // mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    // delay(2000);
  #endif

  /* Sensors setup */
  DEBUG_SERIAL.println("Setting up sensors...");
  serialGPS.begin(GPS_BAUD);

  if (!mpu.setup(0x68))
  {
    DEBUG_SERIAL.println("There is no MPU device at 0x68");
  }else{
    #if CALIBRATE_MPU
      DEBUG_SERIAL.println("Calibrating MPU device");
      mpu.verbose(true);
      delay(2000);
      mpu.calibrateAccelGyro();
      delay(2000);
      mpu.calibrateMag();
      mpu.verbose(false);
    #endif
  }

  DEBUG_SERIAL.println("Setup completed: starting the device operations...");
  delay(1000);
}


void loop()
{
  /*
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
  */
  mqttClient.poll();

  float bpm_readings[DATA_BUFFER];
  float gps_coordinates[DATA_BUFFER][2];
  int   wifi_strengths[DATA_BUFFER];
  float mpu_angles[DATA_BUFFER][3];
  uint8_t i, j = 0;

  for(i = 0; i < DATA_BUFFER; i++)
  {
    bpm_readings[i] = 0.0;
    wifi_strengths[i] = 0;
    
    for(j = 0; j < 2; j++)
      gps_coordinates[i][j] = 0.0;
    for(j = 0; j < 3; j++)
      mpu_angles[i][j] = 0.0;
  }
  
  /* Retrieving sensors' readings */
  for(buffer_i = 0; buffer_i <= DATA_BUFFER; buffer_i++)
  {
    // BPM sensor (raw value)
    bpm_read = analogRead(BPM_SENSOR);
    bpm_readings[buffer_i] = bpm_read;
    // TODO: add a simple pre-processing to check if the reading is ok or not
    // DEBUG_SERIAL.print("BPM raw: ");
    // DEBUG_SERIAL.println(bpm_read);
    
    // GPS coordinates reading
    while (serialGPS.available() > 0 && gps_flag == 0)
    {
      gps.encode(serialGPS.read());

      if (gps.location.isValid())
      {
        lat = gps.location.lat();
        lng = gps.location.lng();
        gps_coordinates[buffer_i][0] = lat;
        gps_coordinates[buffer_i][1] = lng;

        /*
        DEBUG_SERIAL.print("Lat= ");
        DEBUG_SERIAL.println(lat, 6);
        DEBUG_SERIAL.print("Lng= ");
        DEBUG_SERIAL.println(lng, 6);
        */
        gps_flag = 1;
      }
    }
    // DEBUG_SERIAL.println();
    
    // WiFi strength (RSSI in dBm)  
    wifi_strength = WiFi.RSSI();
    wifi_strengths[buffer_i] = wifi_strength;
    /*
    DEBUG_SERIAL.print("WiFi strength: ");
    DEBUG_SERIAL.println(wifi_strength);
    DEBUG_SERIAL.println();
    */
    
    // MPU readings
    if (mpu.update())
    {
      yaw = mpu.getYaw();
      pitch = mpu.getPitch();
      roll = mpu.getRoll();
      mpu_angles[buffer_i][0] = yaw;
      mpu_angles[buffer_i][1] = pitch;
      mpu_angles[buffer_i][2] = roll;

      /*
      DEBUG_SERIAL.print("Yaw: ");
      DEBUG_SERIAL.println(yaw);

      DEBUG_SERIAL.print("Pitch: ");
      DEBUG_SERIAL.println(pitch);

      DEBUG_SERIAL.print("Roll: ");
      DEBUG_SERIAL.println(roll);
      */
    }
    // DEBUG_SERIAL.println();

    /* Set or reset variables */
    gps_flag = 0;
    delay(10);
  }

  /* Sending data to the platform */

  DEBUG_SERIAL.print("Sending data to the platform...");
  DEBUG_SERIAL.println();
  
  for(i = 0; i < buffer_i; i++)
  {
    /*
    DEBUG_SERIAL.print("Bpm raw: ");
    DEBUG_SERIAL.println(bpm_readings[i]);

    DEBUG_SERIAL.print("GPS coords: ");
    DEBUG_SERIAL.println();
    */
    #if MQTT_CONNECT
      mqttClient.beginMessage(bpm_topic);
      mqttClient.print(bpm_readings[i]);
      mqttClient.endMessage();
    #endif

    for(j = 0; j < 2; j++)
    {
      // DEBUG_SERIAL.print(coords[j]);
      // DEBUG_SERIAL.println(gps_coordinates[i][j]);
      #if MQTT_CONNECT
        mqttClient.beginMessage(gps_topics[j]);
        mqttClient.print(gps_coordinates[i][j]);
        mqttClient.endMessage();
      #endif
    }

    /*
    DEBUG_SERIAL.print("Wifi strength: ");
    DEBUG_SERIAL.println(wifi_strengths[i]);

    DEBUG_SERIAL.print("MPU angles: ");
    DEBUG_SERIAL.println();
    */
    for(j = 0; j < 3; j++)
    {
      // DEBUG_SERIAL.print(angles[j]);
      // DEBUG_SERIAL.println(mpu_angles[i][j]);
      #if MQTT_CONNECT
        mqttClient.beginMessage(mpu_topics[j]);
        mqttClient.print(mpu_angles[i][j]);
        mqttClient.endMessage();
      #endif
    }
  }
  
  // DEBUG_SERIAL.println();
  delay(2000);
}

 
