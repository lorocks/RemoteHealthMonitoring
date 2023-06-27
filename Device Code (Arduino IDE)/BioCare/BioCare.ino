#include "Firebase_Arduino_WiFiNINA.h"
#define FIREBASE_HOST "remote-health-79c43-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "aTblk9AKlg7fXzl69Vg9fxvce7ohacyUxN1LAbVj"
#define WIFI_SSID "MDX welcomes you"
#define WIFI_PASSWORD "MdxL0vesyou"
FirebaseData firebaseData;
const int buttonPin = 11;     // the number of the pushbutton pin
int counter = 0;
int buttonState = 0; 
int buttonState1 = 0;
int val;
int tempPin = A3;  
String path = "PATIENT";
#include <Wire.h>
#include "MAX30105.h"

#include "heartRate.h"

MAX30105 particleSensor;

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;
int ALERT = 0;

void setup()
{ 
  pinMode(buttonPin, INPUT);
  Serial.begin(115200);
  Serial.print("Connecting to WiFi...");
  int status = WL_IDLE_STATUS;
  while (status != WL_CONNECTED) {
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print(".");
    delay(300);
  }
  Serial.print(" IP: ");
  Serial.println(WiFi.localIP());
  Serial.println();

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH, WIFI_SSID, WIFI_PASSWORD);
  Firebase.reconnectWiFi(true);
  Serial.println("Initializing...");

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
}

void loop()
{ 
  val = analogRead(tempPin);
  float mv = ( val/1024.0)*5000;
  float cel = mv/10;
  long irValue = particleSensor.getIR();
  buttonState = digitalRead(buttonPin);

  Serial.println(counter);
  if (buttonState == HIGH) {
    counter+=1;
    // turn LED on:
    
    Serial.println(counter);
    delay(100);
  }
  if(counter>=3){
    Serial.println("Alert Sent");
    counter = 0;
    ALERT = 1;
    if (Firebase.setInt(firebaseData, path + "/P001/ALERT",ALERT )) {
      Serial.println(firebaseData.dataPath() + " = " + ALERT);
    }
    delay(3000);
    ALERT = 0;
    if (Firebase.setInt(firebaseData, path + "/P001/ALERT",ALERT )) {
      Serial.println(firebaseData.dataPath() + " = " + ALERT);
    }
  }
  
  if (checkForBeat(irValue) == true)
  {
    //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable

      //Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print("IR=");
  Serial.print(irValue);
//  Serial.print(", BPM=");
//  Serial.print(beatsPerMinute);
//  Serial.print(", Avg BPM=");
//  Serial.print(beatAvg);
  Serial.print("Temperature:");
  Serial.println(cel);
  if (Firebase.setInt(firebaseData, path + "/P001/IRF",irValue )) {
      Serial.println(firebaseData.dataPath() + " = " + irValue);
    }
  if (Firebase.setFloat(firebaseData, path + "/P001/Cel",cel )) {
      Serial.println(firebaseData.dataPath() + " = " + cel);
    }
//    if (Firebase.setFloat(firebaseData, path + "/Heart/IR", irValue)) {
//      Serial.println(firebaseData.dataPath() + " = " + irValue);
//    }
//    if (Firebase.setFloat(firebaseData, path + "/Heart/BPM", beatsPerMinute)) {
//      Serial.println(firebaseData.dataPath() + " = " + beatsPerMinute);
//    }
//    if (Firebase.setFloat(firebaseData, path + "/Heart/AvgBpm", beatAvg)) {
//      Serial.println(firebaseData.dataPath() + " = " + beatAvg);
//    }

   if (buttonState == HIGH) {
    counter+=1;
    // turn LED on:
    
    Serial.println(counter);
    delay(100);
  }

  
  if (irValue < 50000)
    Serial.print(" No finger?");

  Serial.println();
  buttonState1 = digitalRead(buttonPin);
}

void avgb(int beatAvg){
  
  if (Firebase.setFloat(firebaseData, path + "/Heart/AvgBpm", beatAvg)) {
      Serial.println(firebaseData.dataPath() + " = " + beatAvg);
    }
  
}
