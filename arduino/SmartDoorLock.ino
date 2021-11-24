#include <SPI.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"


DHTesp dht;
constexpr uint8_t RST_PIN = 5;
constexpr uint8_t SS_PIN = 4;
const char* mqtt_server = "192.168.50.-";
int mqtt_port = 1883;
const char* user_name = "-"; // 連接 MQTT broker 的帳號密碼
const char* user_password = "-";
int relayPin = 2;                     // 連接繼電器腳位           
const char* topic_subscribe = "-/-"; 
const char* dht_topic = "-/-";
int ledPin = 16;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // 建立 MFRC522

WiFiClient espClient;
PubSubClient client(espClient);

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(),user_name,user_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) 
{
  Serial.print("Command from MQTT broker is : [");
  Serial.print(topic);
  Serial.print("]");
 
  if((char)payload[0] == 'o') // MQTT 傳來 0 熄滅 D2 上的 LED
  {
    digitalWrite(2, HIGH);               // 繼電器常開端(NO)導通
    delay(1000);                                // 延遲1秒
    digitalWrite(2, LOW);                // 繼電器常閉端(NC)導通
    Serial.println("已開門!" );
  }
  
   else if((char)payload[0] == 'L') // MQTT 傳來 0 熄滅 D2 上的 LED
  {
    digitalWrite(ledPin, HIGH);               // 繼電器常開端(NO)導通
    delay(1000);                                // 延遲1秒     
    Serial.println("已開燈!" );
  }
     else if((char)payload[0] == 'l') // MQTT 傳來 0 熄滅 D2 上的 LED
  {
    digitalWrite(ledPin, LOW);               // 繼電器常開端(NO)導通
    delay(1000);                                // 延遲1秒     
    Serial.println("已關燈!" );
  }
} //end callback

void setup()
{
  Serial.begin(9600);
  WiFi.begin("-","-");
   while (WiFi.status() != WL_CONNECTED) { 
     delay(500); 
     Serial.print("."); 
   } 
   Serial.println(); 
   Serial.println("WiFi connected"); 
   Serial.println("Local IP address: "); 
   Serial.println(WiFi.localIP()); 
  pinMode(relayPin, OUTPUT);          // 設定繼電器接腳為輸出腳位
  pinMode(ledPin, OUTPUT); 
  while (!Serial);
  SPI.begin();

  dht.setup(4, DHTesp::DHT22);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  digitalWrite(relayPin, LOW);

  
  Serial.println("可開始讀取卡片");
  Serial.println();

}

void loop()
{
  char msg[30];
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  delay(dht.getMinimumSamplingPeriod());
  float humi = dht.getHumidity();
  float temp = dht.getTemperature();
  sprintf(msg,"%.1f %.1f",temp,humi);
  Serial.println(temp);
  Serial.println(humi);
  Serial.println(msg);
  client.publish(dht_topic,msg);
  memset(msg,0,30);
  

}
