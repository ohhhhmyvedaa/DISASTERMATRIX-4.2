#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Verify I2C address (0x27 or 0x3F) and water module polarity before use.
#define TRIG_PIN 8
#define ECHO_PIN 9
#define SOIL_PIN A0
#define WATER_DO_PIN 2
#define BUZZER_PIN 6
#define PUMP_PIN 5

const byte LCD_ADDRESS = 0x27;
const float TANK_REFERENCE_CM = 30.0;
const int SOIL_DRY_ADC = 800; // Calibrate in your soil
const int SOIL_WET_ADC = 350; // Calibrate in saturated soil
const bool WATER_ACTIVE_HIGH = true;
const float PUMP_ON_DEPTH_CM = 12.0;
const float PUMP_OFF_DEPTH_CM = 8.0;
const unsigned long MAX_PUMP_RUNTIME_MS = 15000UL;
const unsigned long SENSOR_INTERVAL_MS = 1000UL;

LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);
unsigned long lastSample = 0, pumpStarted = 0;
bool pumpOn = false;
bool manualStop = false;

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 25000UL);
  if (duration == 0) return -1.0;
  float cm = duration * 0.0343f / 2.0f;
  if (cm < 2.0f || cm > TANK_REFERENCE_CM + 5.0f) return -1.0;
  return cm;
}
void stopPump() {
  pumpOn = false; digitalWrite(PUMP_PIN, LOW);
}
void setup() {
  pinMode(TRIG_PIN, OUTPUT); pinMode(ECHO_PIN, INPUT);
  pinMode(WATER_DO_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT); pinMode(PUMP_PIN, OUTPUT);
  stopPump(); digitalWrite(BUZZER_PIN, LOW);
  Serial.begin(9600);
  lcd.init(); lcd.backlight(); lcd.print("DISASTERMATRIX");
  lcd.setCursor(0,1); lcd.print("Starting...");
}
void loop() {
  unsigned long now=millis();
  if (now-lastSample < SENSOR_INTERVAL_MS) return;
  lastSample=now;

  float distance=readDistanceCm();
  bool valid=distance >= 0.0f;
  float depth=valid ? TANK_REFERENCE_CM-distance : -1.0f;
  int soilRaw=analogRead(SOIL_PIN);
  float soilPct=100.0f*(SOIL_DRY_ADC-soilRaw)/(float)(SOIL_DRY_ADC-SOIL_WET_ADC);
  soilPct=constrain(soilPct,0.0f,100.0f);
  int waterRaw=digitalRead(WATER_DO_PIN);
  bool waterContact = WATER_ACTIVE_HIGH ? (waterRaw==HIGH) : (waterRaw==LOW);

  // Safety: invalid ultrasonic data never starts the pump. Timeout always stops it.
  if (!valid || manualStop) stopPump();
  else {
    if (!pumpOn && depth >= PUMP_ON_DEPTH_CM) { pumpOn=true; pumpStarted=now; }
    if (pumpOn && depth <= PUMP_OFF_DEPTH_CM) stopPump();
    if (pumpOn && now-pumpStarted >= MAX_PUMP_RUNTIME_MS) stopPump();
  }
  bool buzzer = valid && (depth >= PUMP_ON_DEPTH_CM || waterContact);
  digitalWrite(BUZZER_PIN,buzzer ? HIGH:LOW);
  digitalWrite(PUMP_PIN,pumpOn ? HIGH:LOW);

  Serial.print("{\"water_level_cm\":");
  if(valid) Serial.print(depth,1); else Serial.print("null");
  Serial.print(",\"distance_cm\":");
  if(valid) Serial.print(distance,1); else Serial.print("null");
  Serial.print(",\"soil_moisture_pct\":"); Serial.print(soilPct,1);
  Serial.print(",\"water_sensor\":"); Serial.print(waterContact?1:0);
  Serial.print(",\"pump_status\":"); Serial.print(pumpOn?1:0);
  Serial.print(",\"buzzer_status\":"); Serial.print(buzzer?1:0);
  Serial.print(",\"valid\":"); Serial.print(valid?"true":"false");
  Serial.println("}");

  lcd.clear();
  lcd.setCursor(0,0);
  if(valid){ lcd.print("Water:"); lcd.print(depth,1); lcd.print("cm"); }
  else lcd.print("Sensor invalid");
  lcd.setCursor(0,1);
  lcd.print("Soil:"); lcd.print((int)soilPct); lcd.print("% P:");
  lcd.print(pumpOn?"ON":"OFF");
}
