// NURA OSINT Edge Display — ESP32 client scaffold
// Dependencies: WiFi, HTTPClient, ArduinoJson, and your display driver (TFT_eSPI/LovyanGFX/etc.).
// Keep Wi-Fi/API secrets outside source control for production builds.

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";
const char* DISPLAY_STATE_URL = "https://CHANGE_ME/api/v1/display-state";

struct DisplayState {
  String systemStatus;
  String threatLevel;
  int p0Alerts;
  String sourceHealth;
  String briefStatus;
  String signalTitle;
  String signalPriority;
  String signalConfidence;
  String signalDomain;
};

DisplayState lastGood;
bool hasLastGood = false;

bool fetchState(DisplayState &out) {
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  http.begin(DISPLAY_STATE_URL);
  http.setTimeout(5000);
  int code = http.GET();
  if (code != HTTP_CODE_OK) { http.end(); return false; }
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, http.getString());
  http.end();
  if (err) return false;
  out.systemStatus = doc["system_status"] | "UNKNOWN";
  out.threatLevel = doc["threat_level"] | "UNKNOWN";
  out.p0Alerts = doc["p0_alerts"] | 0;
  out.sourceHealth = doc["source_health"] | "UNKNOWN";
  out.briefStatus = doc["brief_status"] | "UNKNOWN";
  out.signalTitle = doc["top_signal"]["title"] | "No verified signal";
  out.signalPriority = doc["top_signal"]["priority"] | "-";
  out.signalConfidence = doc["top_signal"]["confidence"] | "-";
  out.signalDomain = doc["top_signal"]["domain"] | "-";
  return true;
}

void renderState(const DisplayState &s, bool stale) {
  // Replace Serial output with the selected TFT/e-paper renderer.
  Serial.println("NURA OSINT // EDGE DISPLAY");
  Serial.printf("SYSTEM: %s%s\n", s.systemStatus.c_str(), stale ? " / STALE" : "");
  Serial.printf("THREAT: %s | P0: %d\n", s.threatLevel.c_str(), s.p0Alerts);
  Serial.printf("SOURCES: %s | BRIEF: %s\n", s.sourceHealth.c_str(), s.briefStatus.c_str());
  Serial.printf("TOP: %s\n", s.signalTitle.c_str());
  Serial.printf("%s | %s | %s\n", s.signalDomain.c_str(), s.signalPriority.c_str(), s.signalConfidence.c_str());
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 15000) delay(250);
}

void loop() {
  DisplayState current;
  if (fetchState(current)) {
    lastGood = current;
    hasLastGood = true;
    renderState(current, false);
  } else if (hasLastGood) {
    renderState(lastGood, true);
  } else {
    Serial.println("NURA DISPLAY: API OFFLINE / NO CACHE");
  }
  delay(30000);
}
