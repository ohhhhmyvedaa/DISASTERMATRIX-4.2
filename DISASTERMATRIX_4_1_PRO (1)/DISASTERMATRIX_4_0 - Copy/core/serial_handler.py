import json, time
try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None

FIELDS = {"water_level_cm": (int,float), "distance_cm": (int,float),
          "soil_moisture_pct": (int,float), "water_sensor": (int,bool),
          "pump_status": (int,bool), "buzzer_status": (int,bool), "valid": (bool,)}

def available_ports():
    if list_ports is None: return []
    return [p.device for p in list_ports.comports()]

def validate_message(payload):
    if not isinstance(payload, dict): raise ValueError("JSON message must be an object.")
    if payload.get("valid") is False: raise ValueError("Arduino marked the reading invalid.")
    for key in ("water_level_cm","distance_cm","soil_moisture_pct"):
        if key not in payload or payload[key] is None: continue
        value=float(payload[key])
        if not 0 <= value <= 500: raise ValueError(f"{key} outside accepted range.")
    return payload

class SerialReader:
    def __init__(self): self.connection=None
    def connect(self, port, baud=9600):
        if serial is None: raise RuntimeError("pyserial is not installed.")
        self.connection=serial.Serial(port, baudrate=baud, timeout=0.2)
        time.sleep(1.5)
    def disconnect(self):
        if self.connection and self.connection.is_open: self.connection.close()
        self.connection=None
    def read_one(self):
        if not self.connection or not self.connection.is_open: return None
        line=self.connection.readline().decode("utf-8",errors="replace").strip()
        if not line: return None
        return validate_message(json.loads(line))
