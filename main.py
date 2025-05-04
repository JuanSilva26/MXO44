"""Main script for MXO44 oscilloscope control."""
from instrument import (
    MXO44, ChannelSettings, TriggerSettings, TimebaseSettings,
    WaveformSettings, ArbitraryWaveformSettings, WaveformType,
    DataAcquisitionSettings
)
import os
from datetime import datetime
import numpy as np

def create_example_waveform(waveform_type: str = "damped_sine") -> str:
    """Create an example arbitrary waveform CSV file.
    
    Args:
        waveform_type (str): Type of waveform to generate:
            - "damped_sine": Damped sine wave
            - "chirp": Frequency sweep
            - "gaussian_pulse": Gaussian pulse
            
    Returns:
        str: Path to the created CSV file
    """
    # Create data directory if it doesn't exist
    os.makedirs("waveform_data", exist_ok=True)
    
    # Generate waveform data
    sample_rate = 1000000  # 1 MHz
    duration = 0.001      # 1 ms
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    if waveform_type == "damped_sine":
        freq = 10000     # 10 kHz
        decay = 2000     # decay factor
        voltage = np.exp(-decay * t) * np.sin(2 * np.pi * freq * t)
        filename = "damped_sine.csv"
        
    elif waveform_type == "chirp":
        f0, f1 = 1000, 100000  # Frequency sweep from 1kHz to 100kHz
        voltage = np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t**2 / (2 * duration)))
        filename = "chirp.csv"
        
    elif waveform_type == "gaussian_pulse":
        center = duration / 2
        width = duration / 10
        voltage = np.exp(-(t - center)**2 / (2 * width**2))
        filename = "gaussian_pulse.csv"
        
    else:
        raise ValueError(f"Unknown waveform type: {waveform_type}")
    
    # Scale voltage to be within ±1V
    voltage = voltage / np.max(np.abs(voltage))
    
    # Save to CSV file
    csv_file = f"waveform_data/{filename}"
    with open(csv_file, 'w') as f:
        f.write(f"Rate = {sample_rate}  // Sample rate for the ARB file\n")
        for v in voltage:
            f.write(f"{v}\n")
            
    return csv_file

def main():
    """Test MXO44 oscilloscope control functionality."""
    # Create instrument instance
    scope = MXO44()
    
    try:
        # Connect to instrument
        if not scope.connect():
            print("Failed to connect to instrument")
            return
            
        # Get instrument identification
        print(f"Instrument: {scope.instrument.idn_string}")
        print(f"Options: {scope.instrument.instrument_options}")
        
        # Reset instrument to default state
        scope.write("*RST")
        
        # Configure Channel 1 using dataclass
        channel_settings = ChannelSettings(
            state="ON",
            coupling="DC",
            range=1.0,  # 1V/div
            offset=0.0
        )
        scope.configure_channel(1, channel_settings)
        
        # Configure trigger using dataclass
        trigger_settings = TriggerSettings(
            mode="NORMAL",
            source="CH1",
            level=0.0,
            slope="POS"
        )
        scope.configure_trigger(trigger_settings)
        
        # Configure timebase using dataclass
        timebase_settings = TimebaseSettings(
            scale=0.0001  # 100µs/div
        )
        scope.configure_timebase(timebase_settings)
        
        # Choose between standard waveform or arbitrary waveform
        use_arbitrary = True
        
        if use_arbitrary:
            # Create and configure arbitrary waveform
            print("\nCreating arbitrary waveform...")
            csv_file = create_example_waveform("chirp")  # Try different waveform types
            print(f"Created waveform file: {csv_file}")
            
            print("\nConfiguring arbitrary waveform generator...")
            arb_settings = ArbitraryWaveformSettings(
                csv_file=csv_file,
                sample_rate=2e6,  # Optional: override sample rate
                run_mode="REPetitive"
            )
            scope.configure_arbitrary_waveform(arb_settings)
            
        else:
            # Configure standard waveform
            print("\nConfiguring standard waveform generator...")
            wgen_settings = WaveformSettings(
                function=WaveformType.SQUARE,
                frequency=1000,  # 1kHz
                amplitude=1.0,   # 1Vpp
                offset=0.0,      # 0V DC offset
                duty_cycle=50,   # 50% duty cycle
                output="ON"
            )
            scope.configure_waveform_generator(wgen_settings)
        
        # Create data directory if it doesn't exist
        data_dir = "waveform_data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(data_dir, f"captured_waveform_{timestamp}.csv")
        plot_filename = os.path.join(data_dir, f"captured_waveform_{timestamp}.png")
        
        # Customize plot settings (optional)
        scope.plot_settings.figure_size = (15, 8)  # Larger plot
        scope.plot_settings.dpi = 300  # Higher resolution
        scope.plot_settings.show_grid = True
        scope.plot_settings.show_info = True
        
        # Save waveform data to CSV
        print("\nSaving captured waveform data...")
        scope.save_waveform_data(1, csv_filename)
        print(f"Waveform data saved to {csv_filename}")
        
        # Plot waveform
        print("\nPlotting captured waveform...")
        scope.plot_waveform(1, plot_filename)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Disconnect from instrument
        scope.disconnect()

if __name__ == "__main__":
    main() 