#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#define RELAY 0   //定義GPIO0
const char* ssid = "-";
const char* password = "-";
 
const char* mqtt_server = "192.168.50.-";
int mqtt_port = 1883;
const char* user_name = "-"; // 連接 MQTT broker 的帳號密碼
const char* user_password = "-";

const char* topic_subscribe = "-"; 
int i = 0;
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
 
  if((char)payload[0] == 'n') // MQTT 傳來 0 熄滅 D2 上的 LED
  {
    digitalWrite(RELAY, HIGH);
  }
  else if((char)payload[0] == 'f') // MQTT 傳來 0 熄滅 D2 上的 LED
  {
    digitalWrite(RELAY, LOW);
  }

} //end callback

void setup() {
  Serial.begin(115200);
  Serial.print( "Start..." );
 
  // 繼電器
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, HIGH);
 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println(".");
  }
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}
 
void loop() { 
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
 
}
