import serial
import time
import paho.mqtt.client as mqtt

# --- Configuration Profiles ---
# IMPORTANT: Update SERIAL_PORT to match your active Arduino port (e.g., 'COM3', '/dev/ttyUSB0')
SERIAL_PORT = 'COM7'  
BAUD_RATE = 9600
MQTT_BROKER = "broker.hivemq.com"  # Public test broker
MQTT_PORT = 1883
MQTT_TOPIC = "rca/candidate/temperature"

# --- MQTT Client Initialization ---
# For paho-mqtt 2.0+ we must specify the callback API version
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
except AttributeError:
    # Fallback for older paho-mqtt versions
    client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected successfully to MQTT Broker: {MQTT_BROKER}")
    else:
        print(f"❌ Connection failed with code {rc}")

client.on_connect = on_connect

try:
    print(f"Attempting to connect to {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"CRITICAL: MQTT Broker connection failure: {e}")
    exit(1)

# --- Serial Port Initialization ---
try:
    print(f"Opening Serial Port {SERIAL_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino reboot after serial connection
    print(f"🚀 Monitoring telemetry from {SERIAL_PORT}...")
except Exception as e:
    print(f"CRITICAL: Port configuration error on {SERIAL_PORT}: {e}")
    print("Check if the Arduino is connected and if the COM port is correct.")
    exit(1)

# --- Main Runtime Loop ---
try:
    while True:
        if ser.in_waiting > 0:
            # Read line from Arduino
            raw_payload = ser.readline().decode('utf-8').strip()
            
            if raw_payload:
                try:
                    # Convert to float and validate
                    temperature = float(raw_payload)
                    
                    # Requirement Part 2: Real-time local display
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] [MONITOR] Temperature: {temperature} °C")
                    
                    # Requirement Part 2: Publish to MQTT Broker
                    result = client.publish(MQTT_TOPIC, str(temperature))
                    
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        print(f"   -> Successfully published to topic: '{MQTT_TOPIC}'")
                    else:
                        print(f"   -> ⚠️ Failed to publish (Error code: {result.rc})")
                        
                except ValueError:
                    # Handle non-numeric debug data
                    print(f"[DEBUG/DATA]: {raw_payload}")
                    
        time.sleep(0.1) # Prevent CPU pegging

except KeyboardInterrupt:
    print("\n\nShutting down application...")
finally:
    # Clean release of resources
    if 'ser' in locals() and ser.is_open:
        ser.close()
    client.loop_stop()
    client.disconnect()
    print("✨ All connections closed. System offline.")
