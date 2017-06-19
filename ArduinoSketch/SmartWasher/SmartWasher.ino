/*
 * Author: Christian Kjaer Laustsen // 20176018 @ KAIST // s124324 @ DTU
 * 
 * Read data from an Analog Sound Sensor[0], and submit them using a POST request
 * to an external API server, via cURL.
 * 
 * Built for Arduino Yun[1].
 * 
 * [0] https://www.dfrobot.com/wiki/index.php/Analog_Sound_Sensor_SKU:_DFR0034
 * [1] https://www.arduino.cc/en/Guide/ArduinoYun
 */
#include <Bridge.h>
#include <Process.h>

const boolean outputProcessResponse = true;

const int ledPin = 13;
const int sensorPin = 0;

const String apiEndpoint = "http://192.168.240.162:5000/api/data/audio";
const String building = "W6";
const String floorNumber = "1";
const String room = "Washing Room";

const int maxDataLength = 20;
int audioDataIndex = 0;
int audioData[maxDataLength];


void setup() {
  Bridge.begin();
  pinMode(ledPin, OUTPUT);

  // Wait for a console to be connected (like with 'telnet localhost 6571').
  while (!Console);

  Console.println("Console connected! Beginning readings...");
  digitalWrite(ledPin, LOW);
}

void loop() {
  if (dataIsFilled()) {
    digitalWrite(ledPin, HIGH);
    postData(audioData);
    digitalWrite(ledPin, LOW);
    delay(1000);
  }

  // Read the audio data value, and keep track of it.
  int sensorValue = analogRead(sensorPin);
  addValueToAudioData(sensorValue);

  delay(10);
}

/*
 * Add a value to the audio data array, making sure it doesn't overflow.
 */
void addValueToAudioData(int value) {
  if (audioDataIndex >= (maxDataLength - 1)) {
    audioDataIndex = 0;
  }
  audioData[audioDataIndex] = value;
  audioDataIndex++;
}


/*
 * Check if the audio data array has been filled.
 */
boolean dataIsFilled() {
  if (audioDataIndex >= (maxDataLength - 1)) {
    return true;
  }
  return false;
}

/*
 * Convert an array of ints to a JSON array of ints. Also
 * removes all 0 values, unless all of them are 0, then it 
 * returns "[0]" to indicate this.
 */
String convertArrayToJson(int data[]) {
  String dataString = "[";
  boolean foundValuesAboveZero = false;
  boolean reachedLastValue = false;
  for (int i = 0; i < maxDataLength; i++) {
    String delimiter = ",";
    // Only add data if it's above 0.
    if (data[i] > 0) {
      // Don't use a delimiter if it's the last row.
      if (i == (maxDataLength - 1)) {
        delimiter = "";
        reachedLastValue = true;
      }
      dataString += data[i] + delimiter;
      foundValuesAboveZero = true;
    }
  }
  // If only 0's were found, return an array with just one 0.
  if (!foundValuesAboveZero && !reachedLastValue) {
    dataString += "0";
  } else if (!reachedLastValue) {
    // Else, make sure that the ending is correct by removing the last comma 
    // if it didn't reach the end.
    dataString = dataString.substring(0, dataString.length() - 1);
  }
  dataString += "]";
  return dataString;
}

/*
 * Construct the JSON request.
 */
String constructJsonRequest(int audioData[]) {
  String audioDataString = convertArrayToJson(audioData);
  String jsonData = "{";
  jsonData += "\"building\":";
  jsonData += "\"" + building + "\"";
  jsonData += ", \"floor\":";
  jsonData += "\"" + floorNumber + "\"";
  jsonData += ", \"room\":";
  jsonData += "\"" + room + "\"";
  jsonData += ", \"audioData\":";
  jsonData += audioDataString;
  jsonData += "}";
  return jsonData;
}

/*
 * Construct the JSON request and POST it to the API endpoint
 * via cURL.
 */
void postData(int audioData[]) {
  String jsonData = constructJsonRequest(audioData);
  
  Console.println("Beginning cURL call");
  Process p;
  String cUrlCommand = "/usr/bin/curl -H \"Content-Type: application/json\" -X POST -d '";
  cUrlCommand += jsonData + "' " + apiEndpoint;
  p.runShellCommand(cUrlCommand);

  if (outputProcessResponse) {
    while (p.available() > 0) {
      char c = p.read();
      Console.print(c);
    }
    Console.flush();
  }
}

