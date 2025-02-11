#include <HttpClient.h>
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include "secret.h"
#include <ArduinoJson.h>

unsigned long lastTime = 0;
unsigned long timerDelay = 5000;
long temp;
JsonDocument doc;

void setup() 
{
       Serial.begin(9600);
       delay(10);

       Serial.println("Connecting to ");
       Serial.println(SSID); 
       WiFi.begin(SSID, PASSWRD); 
       while (WiFi.status() != WL_CONNECTED) 
          {
            delay(500);
            Serial.print(".");
          }
  Serial.println("");
  Serial.println("WiFi connected"); 
  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());
  
}
  
void loop() 
{      

  if ((millis() - lastTime) > timerDelay) {
    if(WiFi.status()== WL_CONNECTED){
      temp=random(25,70);
      char jsonData;
      doc["source"] = "ESP8266";
      doc["temp"] = temp;
      serializeJson(doc, jsonData);

      HTTPClient http;
      WiFiClient client;     
      http.begin(client, serverIP);
        
      http.addHeader("Content-Type", "text/json");
      int httpResponseCode = http.POST(jsonData);
      
      // If you need an HTTP request with a content type: application/json, use the following:
      //http.addHeader("Content-Type", "application/json");
      //int httpResponseCode = http.POST("{\"api_key\":\"tPmAT5Ab3j7F9\",\"sensor\":\"BME280\",\"value1\":\"24.25\",\"value2\":\"49.54\",\"value3\":\"1005.14\"}");

      // If you need an HTTP request with a content type: text/plain
      //http.addHeader("Content-Type", "text/plain");
      //int httpResponseCode = http.POST("Hello, World!");
    
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      Serial.println(httpRequestData);
        
      // Free resources
      http.end();
      }
      else {
        Serial.println("WiFi Disconnected");
      }
      lastTime = millis();
    }
}