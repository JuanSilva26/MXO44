# MXO44 Oscilloscope Control

A Python-based control system for the Rohde & Schwarz MXO44 oscilloscope, providing a high-level interface for instrument control, waveform generation, and data acquisition.

## Project Structure

```
mxo44_control/
├── instrument.py      # Core instrument control class
├── main.py           # Example usage and test script
├── config.py         # Configuration settings
├── README.md         # This file
└── MXO44_COMMANDS.md # Command reference
```

## Core Components

### 1. MXO44 Class (`instrument.py`)

The main class that provides a high-level interface to the oscilloscope. Key features:

- Instrument connection and initialization
- Channel configuration
- Trigger setup
- Timebase control
- Waveform generation (standard and arbitrary)
- Data acquisition and transfer
- Waveform plotting and saving

### 2. Configuration Classes

- `ChannelSettings`: Channel configuration (state, coupling, range, offset)
- `TriggerSettings`: Trigger configuration (mode, source, level, slope)
- `TimebaseSettings`: Timebase configuration (scale)
- `WaveformSettings`: Waveform generator settings
- `ArbitraryWaveformSettings`: Arbitrary waveform configuration
- `DataAcquisitionSettings`: Data acquisition parameters
- `PlotSettings`: Plot configuration

### 3. Main Script (`main.py`)

Example script demonstrating:

- Instrument connection
- Basic configuration
- Waveform generation
- Data acquisition
- Data saving and plotting

## Key Features

1. **Instrument Control**

   - USB connection management
   - Error handling and status checking
   - Command synchronization

2. **Channel Configuration**

   - Channel state control
   - Coupling settings
   - Vertical scaling
   - Offset adjustment

3. **Trigger System**

   - Mode selection (AUTO/NORMAL/SINGLE)
   - Source selection
   - Level and slope control

4. **Waveform Generation**

   - Standard waveforms (sine, square, ramp, pulse)
   - Arbitrary waveform support
   - Frequency and amplitude control
   - Output enable/disable

5. **Data Acquisition**

   - Single-shot acquisition
   - Binary data transfer
   - Time and voltage scaling
   - CSV file export

6. **Visualization**
   - Waveform plotting
   - Grid and info display
   - Figure customization
   - PNG export

## Dependencies

- Python 3.8+
- RsInstrument
- NumPy
- Matplotlib
- VISA software (R&S VISA 5.12.x or newer)

## Installation

1. Install required Python packages:

```bash
pip install RsInstrument numpy matplotlib
```

2. Install R&S VISA software from the official website

3. Clone this repository:

```bash
git clone <repository-url>
cd mxo44_control
```

## Usage Example

```python
from instrument import MXO44, ChannelSettings, TriggerSettings, TimebaseSettings

# Create instrument instance
scope = MXO44()

try:
    # Connect to instrument
    if scope.connect():
        # Configure channel
        channel_settings = ChannelSettings(
            state="ON",
            coupling="DC",
            range=1.0
        )
        scope.configure_channel(1, channel_settings)

        # Configure trigger
        trigger_settings = TriggerSettings(
            mode="NORMAL",
            source="CH1",
            level=0.0
        )
        scope.configure_trigger(trigger_settings)

        # Configure timebase
        timebase_settings = TimebaseSettings(
            scale=0.0001  # 100µs/div
        )
        scope.configure_timebase(timebase_settings)

        # Capture and save waveform
        scope.save_waveform_data(1, "waveform.csv")
        scope.plot_waveform(1, "waveform.png")

finally:
    scope.disconnect()
```

## Error Handling

The code includes comprehensive error handling:

- Connection status verification
- Command execution verification
- Data validation
- Resource cleanup

## Future Enhancements

1. **Advanced Measurements**

   - Frequency analysis
   - Statistical measurements
   - FFT capabilities

2. **Extended Control**

   - Multi-channel synchronization
   - Advanced trigger modes
   - Custom measurement scripts

3. **Data Analysis**
   - Automated analysis routines
   - Custom measurement definitions
   - Data export formats

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:

1. Check the documentation
2. Review the example code
3. Open an issue in the repository

## MNIST Waveform Generation

This project now includes functionality to convert MNIST digit images into arbitrary waveforms that can be loaded on the MXO44 oscilloscope's waveform generator.

### Prerequisites

The MNIST waveform generation requires additional Python packages:

```
torch
torchvision
h5py
```

These have been added to `requirements.txt`. Install them with:

```
pip install -r requirements.txt
```

### Generating MNIST Waveforms

To generate the MNIST waveforms, run:

```
python generate_mnist_waveforms.py
```

This script will:

1. Download the MNIST dataset (if not already present)
2. Select a balanced subset of 100 digit images (10 per digit 0-9)
3. Convert each digit image to a pulse waveform
4. Save individual CSV files in `waveform_data/mnist/` for each digit
5. Save all waveforms to an HDF5 file for batch processing
6. Generate example plots for visualization

The generated CSV files follow the format expected by the MXO44 oscilloscope's arbitrary waveform generator.

### Using MNIST Waveforms in main.py

The `main.py` script has been updated to use these MNIST waveforms:

```python
# To use a random MNIST digit waveform
digit, csv_file = use_mnist_waveform(scope)

# To use a specific digit (e.g., digit 5)
digit, csv_file = use_mnist_waveform(scope, digit=5)

# To use a specific sample by index (e.g., index 42)
digit, csv_file = use_mnist_waveform(scope, index=42)
```

You can switch between waveform types by changing the `waveform_type` variable in `main.py`:

- `"mnist"`: Use a MNIST digit waveform
- `"arbitrary"`: Use a standard arbitrary waveform (damped sine, chirp, etc.)
- `"standard"`: Use a standard function generator waveform (sine, square, etc.)
