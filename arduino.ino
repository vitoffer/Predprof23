#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <FS.h>
#include<LittleFS.h>
#include "I2Cdev.h" 
#include "Wire.h"
#include <SPI.h>
#define APSSID "ESPap"
#define APPSK  "iamsorry"
#define LEDPIN D7
ESP8266WebServer server(80);
File file;
int ctr = 1;
bool race = false;
const char *logname = "/racedata.txt";

const int MPU_addr=0x68;
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
 
int minVal=265;
int maxVal=402;
 
double x;
double y;
double z;


void setup() {
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
  pinMode(LEDPIN, OUTPUT);
  Serial.begin(115200);
  LittleFS.begin();
  WiFi.softAP(APSSID, APPSK);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
  MDNS.begin("esp8266"); 
  server.on("/download", HTTP_GET, [](){
    digitalWrite(LEDPIN, LOW);
    file.close();
      Serial.println("finished");
      race = false;
      ctr = 0;
      File f = LittleFS.open(logname, "r");
      for(int i=0;i<f.size();i++) 
        {
          Serial.print((char)f.read());
        }
      f.close();
      File upfile = LittleFS.open(logname, "r");
      server.streamFile(upfile, "text/plain");
      upfile.close(); 
  });
  server.on("/start", HTTP_GET, [](){
    LittleFS.format();
    file = LittleFS.open(logname, "w");
    digitalWrite(LEDPIN, HIGH);
    Serial.println("started");
    race = true;
    server.send(200, "text/plain", "");
  });
  server.begin();
  MDNS.addService("http", "tcp", 80);

}

void loop() {
  
  if(race)
  {
    //---------------------------------------place for reading gyro----------------------------------------------------
    Wire.beginTransmission(MPU_addr);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_addr,14,true);
    AcX=Wire.read()<<8|Wire.read();
    AcY=Wire.read()<<8|Wire.read();
    AcZ=Wire.read()<<8|Wire.read();
    int xAng = map(AcX,minVal,maxVal,-90,90);
    int yAng = map(AcY,minVal,maxVal,-90,90);
    int zAng = map(AcZ,minVal,maxVal,-90,90);
     
    x= RAD_TO_DEG * (atan2(-yAng, -zAng)+PI);
    y= RAD_TO_DEG * (atan2(-xAng, -zAng)+PI);
    z= RAD_TO_DEG * (atan2(-yAng, -xAng)+PI);
    
    Serial.print("AngleZ= ");
    Serial.println(z);
    Serial.println("-----------------------------------------");
    file.print(String(z)+ ";\n");
    delay(50);
  }
  MDNS.update();
  server.handleClient();
}