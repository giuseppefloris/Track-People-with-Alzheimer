/*
  Luca Scionis - Tracking People with Alzheimer: code for NodeMCU sending data to the platform
  Last Update: 27/08/23
*/

#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>
#include <Wire.h>

#include <MPU9250.h>

/* Define this "net-conf.h" header with:
      - SSID
      - PASS
      - MQTT_SERVER (name of the mqtt server)
      - MQTT_PORT
 */
#include "net-conf.h"

/* Sensors pins*/
#define BPM_SENSOR  0
#define GPS_RX      0
#define GPS_TX      2
#define GPS_BAUD    9600

/* Debug variables */
#define DEBUG true  //set to true for debug output, false for no debug output
#define DEBUG_SERIAL if(DEBUG)Serial

#define WIFI_CONNECT  true
#define MQTT_CONNECT  true
#define CALIBRATE_MPU false


/* Global variables */
float bpm_read;
float lat, lng;
int   wifi_strength;
float yaw, pitch, roll;

int gps_flag = 0;

/* Global variables for BPM processing */


/* Global objects*/
WiFiClient nodeClient;
MqttClient mqttClient(nodeClient);

TinyGPSPlus gps;
SoftwareSerial serialGPS(GPS_RX, GPS_TX);

MPU9250 mpu;


void setup() {
  /* Initializing serial and I2C communication */
  DEBUG_SERIAL.begin(9600);
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
  mqttClient.poll();

  float bpm_readings[2]; // store bpm_raw and millis() time
  int   bpm_values;
  float gps_coordinates[2];
  int   wifi_strengths;
  float mpu_angles[3];
  uint8_t gps_flag = 0;


    for(int j = 0; j < 2; j++)
      gps_coordinates[j] = 0.0;
    for(int j = 0; j < 3; j++)
      mpu_angles[j] = 0.0;


  /* Retrieving sensors' readings */
    // BPM sensor (raw value)
    bpm_read = analogRead(BPM_SENSOR);
    bpm_readings[0] = bpm_read;
    bpm_readings[1] = millis();
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
        gps_coordinates[0] = lat;
        gps_coordinates[1] = lng;


        DEBUG_SERIAL.print("Lat= ");
        DEBUG_SERIAL.println(lat, 6);
        DEBUG_SERIAL.print("Lng= ");
        DEBUG_SERIAL.println(lng, 6);


        gps_flag = 1;
      }
    }
    // DEBUG_SERIAL.println();

    // WiFi strength (RSSI in dBm)
    wifi_strength = WiFi.RSSI();
    wifi_strengths = wifi_strength;
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
      mpu_angles[0] = yaw;
      mpu_angles[1] = pitch;
      mpu_angles[2] = roll;

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


  /* Processing BPM raw values to obtain real BPM */


  /* Sending data to the platform */

  DEBUG_SERIAL.print("Sending data to the platform...");
  DEBUG_SERIAL.println();


    /*
    DEBUG_SERIAL.print("Bpm raw: ");
    DEBUG_SERIAL.println(bpm_readings[i]);


    DEBUG_SERIAL.print("GPS coords: ");
    DEBUG_SERIAL.println(gps_coordinates[i][0]);
    DEBUG_SERIAL.println(gps_coordinates[i][1]);
    */

    #if MQTT_CONNECT
      mqttClient.beginMessage(wifi_topic);
      mqttClient.print(wifi_strengths);
      mqttClient.endMessage();
    #endif

    #if MQTT_CONNECT
      mqttClient.beginMessage(bpm_topic);
      // DEBUG_SERIAL.print(bpm_readings[i]);
      mqttClient.print(bpm_values);
      mqttClient.endMessage();
    #endif

    #if MQTT_CONNECT
      String gps_lat_s = String(gps_coordinates[0], 2);
      String gps_lng_s = String(gps_coordinates[1], 2);
      String gps_s = gps_lat_s + "," + gps_lng_s;

      mqttClient.beginMessage(gps_topic);
      mqttClient.print(gps_s);
      mqttClient.endMessage();
    #endif

    /*
    DEBUG_SERIAL.print("Wifi strength: ");
    DEBUG_SERIAL.println(wifi_strengths[i]);

    DEBUG_SERIAL.print("MPU angles: ");
    DEBUG_SERIAL.println();
    */

    #if MQTT_CONNECT
      String yaw_s = String(mpu_angles[0], 2);
      String pitch_s = String(mpu_angles[1], 2);
      String roll_s = String(mpu_angles[2], 2);
      String mpu_msg = yaw_s + "," + pitch_s + "," + roll_s;

      mqttClient.beginMessage(mpu_topic);
      mqttClient.print(mpu_msg);
      mqttClient.endMessage();
    #endif


  // DEBUG_SERIAL.println();
  delay(2000);
}
