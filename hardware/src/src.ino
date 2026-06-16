#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHT.h"

// --- Configuration ---
#define DHTPIN 2          
#define DHTTYPE DHT11     

// Initialize LCD (Address 0x27, 16 chars, 2 rows)
LiquidCrystal_I2C lcd(0x27, 16, 2); 
DHT dht(DHTPIN, DHTTYPE);

// Provide your actual name here for the evaluation
// If it exceeds 16 characters, it will scroll automatically
String candidateName = "IGITANGAZA Noble Prince"; 

unsigned long lastUpdate = 0;
const long interval = 2000; // Temperature update interval (2 seconds)
int scrollIndex = 0;

void setup() {
  Serial.begin(9600); // Communication link to PC
  dht.begin();
  lcd.init();
  lcd.backlight();
  
  // Pad the name for smoother scrolling if it's long
  if (candidateName.length() > 16) {
    candidateName += "   "; 
  }
}

void loop() {
  unsigned long currentMillis = millis();

  // Part 1c: Horizontal Scrolling Logic
  static unsigned long lastScrollTime = 0;
  if (currentMillis - lastScrollTime >= 350) { // Scroll speed: 350ms
    lastScrollTime = currentMillis;
    lcd.setCursor(0, 0);
    
    if (candidateName.length() <= 16) {
      lcd.print(candidateName);
    } else {
      // Calculate display window for scrolling text
      String displayStr = candidateName.substring(scrollIndex, scrollIndex + 16);
      if (displayStr.length() < 16) {
        displayStr += candidateName.substring(0, 16 - displayStr.length());
      }
      lcd.print(displayStr);
      scrollIndex = (scrollIndex + 1) % candidateName.length();
    }
  }

  // Part 1b: Periodic Temperature Reading & Serial Transmission
  if (currentMillis - lastUpdate >= interval) {
    lastUpdate = currentMillis;
    float t = dht.readTemperature();

    if (isnan(t)) {
      lcd.setCursor(0, 1);
      lcd.print("Temp: Error     ");
      return;
    }

    // Display on Second Row
    lcd.setCursor(0, 1);
    lcd.print("Temp: ");
    lcd.print(t, 1);
    lcd.print((char)223); // Degree symbol
    lcd.print("C        ");

    // Part 2: Push telemetry to Serial for PC ingestion
    Serial.println(t);
  }
}
