# MXO44 Oscilloscope Control - User Guide

This guide provides detailed information about using the MXO44 oscilloscope control system.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Configuration Classes](#configuration-classes)
4. [Core Functions](#core-functions)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.8 or newer
- RsInstrument package
- NumPy and Matplotlib
- R&S VISA software
- MXO44 oscilloscope with USB connection

### Installation
1. Install required packages:
```bash
pip install RsInstrument numpy matplotlib
```

2. Install R&S VISA software from the official website

3. Connect the oscilloscope via USB

## Basic Usage

### 1. Import and Initialize
```python
from instrument import MXO44

# Create instrument instance
scope = MXO44()

try:
    # Connect to instrument
    if scope.connect():
        # Your code here
finally:
    scope.disconnect()
```

### 2. Basic Configuration
```python
from instrument import ChannelSettings, TriggerSettings, TimebaseSettings

# Configure channel
channel_settings = ChannelSettings(
    state="ON",
    coupling="DC",
    range=1.0,  # 1V/div
    offset=0.0
)
scope.configure_channel(1, channel_settings)

# Configure trigger
trigger_settings = TriggerSettings(
    mode="NORMAL",
    source="CH1",
    level=0.0,
    slope="POS"
)
scope.configure_trigger(trigger_settings)

# Configure timebase
timebase_settings = TimebaseSettings(
    scale=0.0001  # 100µs/div
)
scope.configure_timebase(timebase_settings)
```

## Configuration Classes

### 1. ChannelSettings
```python
@dataclass
class ChannelSettings:
    state: Literal["ON", "OFF"] = "ON"
    coupling: Literal["DC", "AC", "GND"] = "DC"
    range: float = 1.0  # V/div
    offset: float = 0.0  # V
```

### 2. TriggerSettings
```python
@dataclass
class TriggerSettings:
    mode: Literal["AUTO", "NORMAL", "SINGLE"] = "AUTO"
    source: str = "CH1"
    level: float = 0.0  # V
    slope: Literal["POS", "NEG"] = "POS"
```

### 3. TimebaseSettings
```python
@dataclass
class TimebaseSettings:
    scale: float = 1e-3  # s/div
```

### 4. WaveformSettings
```python
@dataclass
class WaveformSettings:
    function: WaveformType = WaveformType.SINUSOID
    frequency: float = 1000.0  # Hz
    amplitude: float = 1.0  # Vpp
    offset: float = 0.0  # V
    duty_cycle: float = 50.0  # % (for square wave)
    symmetry: float = 50.0  # % (for ramp wave)
    width: float = 1e-6  # s (for pulse wave)
    output: Literal["ON", "OFF"] = "ON"
```

## Core Functions

### 1. Connection Management
```python
def connect(self, resource: str = "USB0::0x0AAD::0x0197::1335.5050k04-201064::INSTR") -> bool:
    """Connect to the instrument."""
    
def disconnect(self) -> None:
    """Disconnect from the instrument."""
```

### 2. Channel Configuration
```python
def configure_channel(self, channel: int, settings: Union[Dict[str, Any], ChannelSettings]) -> None:
    """Configure an oscilloscope channel."""
```

### 3. Trigger Configuration
```python
def configure_trigger(self, settings: Union[Dict[str, Any], TriggerSettings]) -> None:
    """Configure the oscilloscope trigger."""
```

### 4. Timebase Configuration
```python
def configure_timebase(self, settings: Union[Dict[str, Any], TimebaseSettings]) -> None:
    """Configure the oscilloscope timebase."""
```

### 5. Waveform Generation
```python
def configure_waveform_generator(self, settings: Union[Dict[str, Any], WaveformSettings]) -> None:
    """Configure the waveform generator."""
```

### 6. Data Acquisition
```python
def capture_waveform(self, channel: int) -> Dict[str, Any]:
    """Capture waveform data from specified channel."""
```

### 7. Data Saving and Plotting
```python
def save_waveform_data(self, channel: int, filename: str) -> None:
    """Save waveform data to CSV file."""
    
def plot_waveform(self, channel: int, filename: Optional[str] = None) -> None:
    """Plot waveform data from specified channel."""
```

## Advanced Features

### 1. Arbitrary Waveform Generation
```python
def configure_arbitrary_waveform(self, settings: Union[Dict[str, Any], ArbitraryWaveformSettings]) -> None:
    """Configure arbitrary waveform generator."""
```

### 2. Custom Plot Settings
```python
@dataclass
class PlotSettings:
    figure_size: Tuple[int, int] = (12, 6)
    show_grid: bool = True
    show_info: bool = True
    dpi: int = 300
```

## Troubleshooting

### Common Issues

1. **Connection Problems**
   - Verify USB connection
   - Check VISA installation
   - Ensure correct resource string

2. **Command Errors**
   - Check command syntax
   - Verify parameter ranges
   - Ensure proper initialization

3. **Data Transfer Issues**
   - Check buffer sizes
   - Verify data format
   - Ensure proper synchronization

### Error Handling

The code includes comprehensive error handling:
```python
try:
    # Your code here
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    scope.disconnect()
```

### Debugging Tips

1. Enable verbose output:
```python
scope.instrument.logger.mode = LoggingMode.On
```

2. Check instrument status:
```python
print(scope.query("*STB?"))
```

3. Verify settings:
```python
print(scope.query("CHAN1:STAT?"))
print(scope.query("TRIG:MODE?"))
print(scope.query("TIM:SCAL?"))
```

## Best Practices

1. **Resource Management**
   - Always use try/finally blocks
   - Properly disconnect after use
   - Handle errors gracefully

2. **Configuration**
   - Set appropriate timeouts
   - Configure proper trigger conditions
   - Use appropriate scaling

3. **Data Acquisition**
   - Enable display updates for feedback
   - Use binary format for efficiency
   - Consider buffer sizes

4. **Waveform Generation**
   - Follow proper mode switching sequence
   - Validate parameters
   - Check output status

## Additional Resources

1. [MXO44 User Manual](https://www.rohde-schwarz.com/manual/mxo44)
2. [RsInstrument Documentation](https://www.rohde-schwarz.com/us/driver-pages/rsinstrument_132_10152.html)
3. [SCPI Command Reference](https://www.rohde-schwarz.com/webhelp/mxo44_html_usermanual_en/Content/Remote_Control/Remote_Control.htm) 