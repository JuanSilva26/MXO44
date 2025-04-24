# MXO44 Oscilloscope Command Reference

This document provides a comprehensive reference for the MXO44 oscilloscope commands, their usage, and configuration options.

## Table of Contents
1. [Basic Commands](#basic-commands)
2. [Channel Configuration](#channel-configuration)
3. [Trigger Configuration](#trigger-configuration)
4. [Timebase Configuration](#timebase-configuration)
5. [Waveform Generator](#waveform-generator)
6. [Arbitrary Waveform Generation](#arbitrary-waveform-generation)
7. [Data Acquisition](#data-acquisition)
8. [Measurements](#measurements)
9. [Additional Features](#additional-features)

## Basic Commands

### Instrument Identification
```scpi
*IDN?  # Query instrument identification
```
Returns: Manufacturer, Model, Serial Number, Firmware Version

### Reset and Status
```scpi
*RST   # Reset instrument to default state
*CAL   # Perform internal calibration
*OPC?  # Query operation complete status
```

### Display Settings
```scpi
SYSTem:DISPlay:UPDate ON|OFF  # Enable/disable display updates
DISPlay:DIAGram:CROSshair ON|OFF  # Enable/disable crosshair
DISPlay:DIAGram:FINegrid ON|OFF  # Enable/disable fine grid
```

## Channel Configuration

### Basic Channel Settings
```scpi
CHAN<n>:STAT ON|OFF  # Enable/disable channel
CHAN<n>:COUP DC|AC|GND  # Set coupling
CHAN<n>:RANG <value>  # Set vertical range (V/div)
CHAN<n>:OFFS <value>  # Set vertical offset (V)
```

Where:
- `<n>`: Channel number (1-4)
- Coupling options:
  - `DC`: Direct coupling
  - `AC`: AC coupling (blocks DC)
  - `GND`: Ground coupling

### Bandwidth Settings
```scpi
CHAN<n>:BANDwidth:FULL|LIMited  # Set bandwidth mode
CHAN<n>:BANDwidth:LIMit <value>  # Set bandwidth limit (Hz)
```

## Trigger Configuration

### Trigger Mode
```scpi
TRIG:MODE AUTO|NORMAL|SINGLE  # Set trigger mode
```
Modes:
- `AUTO`: Auto-trigger if no trigger occurs
- `NORMAL`: Only trigger when conditions met
- `SINGLE`: Single acquisition on trigger

### Edge Trigger Settings
```scpi
TRIG:EVEN1:SOUR C<n>  # Set trigger source (C1, C2, etc.)
TRIG:EVEN1:LEV1:VAL <value>  # Set trigger level (V)
TRIG:EVEN1:EDGE:SLOP POS|NEG  # Set trigger slope
```

### Additional Trigger Types
```scpi
TRIG:EVEN1:TYPE EDGE|PULS|RUNT|WIND|TIMEOUT|VIDEO|PATTERN|STATE|DELAY
```
Each trigger type has specific parameters:
- `PULS`: Pulse width trigger
- `RUNT`: Runt pulse trigger
- `WIND`: Window trigger
- `TIMEOUT`: Timeout trigger
- `VIDEO`: Video trigger
- `PATTERN`: Pattern trigger
- `STATE`: State trigger
- `DELAY`: Delay trigger

## Timebase Configuration

### Basic Timebase Settings
```scpi
TIM:SCAL <value>  # Set time/div (s)
TIM:POS <value>  # Set horizontal position (s)
TIM:MODE MAIN|XY|ROLL  # Set timebase mode
TIM:REF CENTer|LEFT|RIGHT  # Set time reference
```

### Acquisition Settings
```scpi
ACQuire:COUNt <value>  # Set number of acquisitions
ACQuire:POINts <value>  # Set number of points
ACQuire:TYPE NORMal|AVERage|PEAK|HRESolution  # Set acquisition type
```

## Waveform Generator

### Basic Waveform Settings
```scpi
WGENerator1:PRES  # Reset waveform generator
WGENerator1:SOURce FUNCgen|ARBGenerator  # Set generator mode
WGENerator1:FUNCtion:SELect SINusoid|SQUare|RAMP|PULSe|NOISe|DC|ARBitrary  # Select waveform
WGENerator1:FREQ <value>  # Set frequency (Hz)
WGENerator1:VOLT:VPP <value>  # Set amplitude (Vpp)
WGENerator1:VOLT:OFFS <value>  # Set offset (V)
WGENerator1:ENABle ON|OFF  # Enable/disable output
```

### Waveform-Specific Settings
```scpi
# Square Wave
WGENerator1:FUNCtion:SQUare:DCYCle <value>  # Set duty cycle (%)

# Ramp Wave
WGENerator1:FUNCtion:RAMP:SYMMetry <value>  # Set symmetry (%)

# Pulse Wave
WGENerator1:FUNCtion:PULSe:WIDTh <value>  # Set pulse width (s)
```

## Arbitrary Waveform Generation

### File Format
The arbitrary waveform generator accepts CSV files in three formats:

1. With Sample Rate:
```csv
Rate = 500000  //Sample rate of the arbitrary waveform
voltage1
voltage2
...
```

2. With Time and Voltage Values:
```csv
time1,voltage1
time2,voltage2
...
```

3. With Voltage Values Only:
```csv
voltage1
voltage2
...
```

### Arbitrary Waveform Commands
```scpi
# Configuration Sequence
WGENerator1:SOURce FUNCgen  # First set to function generator mode
WGENerator1:FUNCtion:SELect ARBitrary  # Select arbitrary function
WGENerator1:SOURce ARBGenerator  # Switch to arbitrary generator mode

# File Operations
WGENerator1:ARBGen:NAME '<file_path>'  # Specify waveform file
WGENerator1:ARBGen:OPEN  # Load the file
WGENerator1:ARBGen:SRATe <value>  # Set sample rate
WGENerator1:ARBGen:RUNMode REPetitive  # Set to repetitive mode
```

## Data Acquisition

### Acquisition Settings
```scpi
SYSTem:DISPlay:UPDate ON|OFF  # Enable/disable display updates during acquisition
RUNSingle  # Perform single acquisition
ACQuire:POINts?  # Query number of sample points

# Data Format Configuration
FORMat:DATA REAL,32  # Set to 32-bit float format
FORMat:BORDer LSBFirst  # Set byte order
```

### Waveform Data Transfer
```scpi
CHAN<n>:DATA?  # Query waveform data from channel n
TIM:SCAL?  # Query time/div for x-axis scaling
CHAN<n>:RANG?  # Query V/div for y-axis scaling
CHAN<n>:OFFS?  # Query offset for y-axis positioning
```

## Measurements

### Basic Measurements
```scpi
MEAS:FREQ CHAN<n>  # Measure frequency
MEAS:VPP CHAN<n>  # Measure peak-to-peak voltage
MEAS:VRMS CHAN<n>  # Measure RMS voltage
MEAS:VMAX CHAN<n>  # Measure maximum voltage
MEAS:VMIN CHAN<n>  # Measure minimum voltage
```

### Measurement Statistics
```scpi
MEAS<n>:STATistics:ENABle ON|OFF  # Enable/disable statistics
MEAS<n>:RESult:PPEak?  # Query maximum value
MEAS<n>:RESult:NPEak?  # Query minimum value
MEAS<n>:RESult:AVG?  # Query mean value
MEAS<n>:RESult:RMS?  # Query RMS value
MEAS<n>:RESult:STDDev?  # Query standard deviation
```

## Additional Features

### FFT Analysis
```scpi
CALC:FFT:MODE ON|OFF  # Enable/disable FFT
CALC:FFT:SPAN <value>  # Set frequency span
CALC:FFT:CENTer <value>  # Set center frequency
CALC:FFT:WINDow RECTangular|HAMMing|HANning|BLACkman|FLATtop  # Set window
```

### Cursor Measurements
```scpi
CURSor:MODE OFF|MANual|TRACk|AUTO  # Set cursor mode
CURSor:SOUR CHAN<n>  # Set cursor source
CURSor:FUNC HORizontal|VERTical|PAIR  # Set cursor function
```

### Save/Recall Settings
```scpi
*SAV <value>  # Save instrument state
*RCL <value>  # Recall instrument state
```

### Screen Capture
```scpi
HCOP:DEV:LANG PNG|BMP|TIFF  # Set image format
HCOP:ITEM ALL|GRATicule|WAVEform  # Set capture items
HCOP:IMM  # Execute screen capture
```

## Common Use Cases

1. **Basic Waveform Display**:
   ```scpi
   *RST
   CHAN1:STAT ON
   CHAN1:COUP DC
   CHAN1:RANG 1.0
   TIM:SCAL 1E-6
   TRIG:MODE AUTO
   ```

2. **Frequency Measurement**:
   ```scpi
   MEAS:FREQ CHAN1
   MEAS:STATistics:ENABle ON
   ACQuire:COUNt 100
   ```

3. **FFT Analysis**:
   ```scpi
   CALC:FFT:MODE ON
   CALC:FFT:SPAN 1E6
   CALC:FFT:WINDow HANning
   ```

4. **Waveform Generator**:
   ```scpi
   WGENerator1:PRES
   WGENerator1:FUNCtion:SELect SINusoid
   WGENerator1:FREQ 1E6
   WGENerator1:VOLT:VPP 0.5
   WGENerator1:ENABle ON
   ```

### Arbitrary Waveform Generation
```scpi
# Setup
WGENerator1:SOURce FUNCgen
WGENerator1:FUNCtion:SELect ARBitrary
WGENerator1:SOURce ARBGenerator

# Load and Configure
WGENerator1:ARBGen:NAME '/path/to/waveform.csv'
WGENerator1:ARBGen:OPEN
WGENerator1:ARBGen:SRATe 1E6
WGENerator1:ARBGen:RUNMode REPetitive
WGENerator1:ENABle ON
```

### Data Capture and Analysis
```scpi
# Prepare Acquisition
SYSTem:DISPlay:UPDate ON
RUNSingle

# Configure Data Transfer
FORMat:DATA REAL,32
FORMat:BORDer LSBFirst

# Capture Data
CHAN1:DATA?
```

## Tips and Best Practices

1. **Command Format**:
   - Commands are case-insensitive
   - Use `?` for queries
   - Use `*` for common commands

2. **Error Handling**:
   - Check `SYST:ERR?` after critical commands
   - Use `*OPC?` for synchronization
   - Set appropriate timeouts

3. **Performance**:
   - Minimize display updates during automation
   - Use binary format for waveform transfer
   - Set appropriate acquisition parameters

4. **Measurement Accuracy**:
   - Allow sufficient settling time
   - Use appropriate trigger settings
   - Consider noise and bandwidth limitations

5. **Arbitrary Waveform Generation**:
   - Ensure proper file format and sample rate
   - Follow the correct mode switching sequence
   - Consider memory limitations
   - Validate voltage ranges

6. **Data Acquisition**:
   - Enable display updates for visual feedback
   - Use binary format for efficient transfer
   - Consider buffer sizes for large transfers
   - Calculate proper scaling factors

## Error Handling

Common error codes and their meanings:
- -141: Invalid character data
- -222: Data out of range
- -256: File name not found
- -350: Queue overflow

Best practices for error handling:
1. Check instrument status after critical commands
2. Implement proper timeouts for long operations
3. Validate file paths and data formats
4. Monitor buffer sizes during data transfer

## Error Handling

Common error codes and their meanings:
- -141: Invalid character data
- -222: Data out of range
- -256: File name not found
- -350: Queue overflow

Best practices for error handling:
1. Check instrument status after critical commands
2. Implement proper timeouts for long operations
3. Validate file paths and data formats
4. Monitor buffer sizes during data transfer 