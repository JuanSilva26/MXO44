"""Configuration settings for MXO44 oscilloscope control."""


CONNECTION_STRING = "USB0::0x0AAD::0x0197::1335.5050k04-201064::INSTR"

# Timeout settings (in milliseconds)
TIMEOUT_MS = 5000  # General VISA timeout
OPC_TIMEOUT_MS = 10000  # Timeout for operations that require completion

# Channel Settings
CHANNEL_SETTINGS = {
    "coupling": "DC",  # DC or AC
    "range": 1.0,  # Volts per division
    "offset": 0.0,  # Vertical offset in volts
    "bandwidth": "FULL",  # FULL or limit bandwidth
    "state": "ON"  # ON or OFF
}

# Trigger Settings
TRIGGER_SETTINGS = {
    "mode": "AUTO",  # AUTO, NORMAL, or SINGLE
    "source": "CH1",  # Trigger source channel
    "level": 0.0,  # Trigger level in volts
    "slope": "POS",  # POS or NEG slope
    "coupling": "DC"  # DC or AC coupling
}

# Waveform Generator Settings
WAVEFORM_SETTINGS = {
    "frequency": 1000,  # Hz
    "amplitude": 1.0,  # Volts peak-to-peak
    "offset": 0.0,  # DC offset in volts
    "output": "OFF"  # ON or OFF
}

# Data Acquisition Settings
ACQUISITION_SETTINGS = {
    "points": 1000,  # Number of points to acquire
    "format": "ASCII",  # ASCII or BINARY
    "average": 1  # Number of averages
} 