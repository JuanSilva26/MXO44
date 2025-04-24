"""MXO44 Oscilloscope control module."""
from RsInstrument import RsInstrument, BinFloatFormat
from typing import Optional, Dict, Any, Literal, List, Tuple, Union
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from enum import Enum, auto

class WaveformType(Enum):
    """Available waveform types."""
    SINUSOID = "SINusoid"
    SQUARE = "SQUare"
    RAMP = "RAMP"
    PULSE = "PULSe"
    NOISE = "NOISe"
    DC = "DC"
    ARBITRARY = "ARBitrary"

@dataclass
class ChannelSettings:
    """Channel configuration settings."""
    state: Literal["ON", "OFF"] = "ON"
    coupling: Literal["DC", "AC", "GND"] = "DC"
    range: float = 1.0  # V/div
    offset: float = 0.0  # V

@dataclass
class TriggerSettings:
    """Trigger configuration settings."""
    mode: Literal["AUTO", "NORMAL", "SINGLE"] = "AUTO"
    source: str = "CH1"
    level: float = 0.0  # V
    slope: Literal["POS", "NEG"] = "POS"

@dataclass
class TimebaseSettings:
    """Timebase configuration settings."""
    scale: float = 1e-3  # s/div

@dataclass
class WaveformSettings:
    """Waveform generator settings."""
    function: WaveformType = WaveformType.SINUSOID
    frequency: float = 1000.0  # Hz
    amplitude: float = 1.0  # Vpp
    offset: float = 0.0  # V
    duty_cycle: float = 50.0  # % (for square wave)
    symmetry: float = 50.0  # % (for ramp wave)
    width: float = 1e-6  # s (for pulse wave)
    output: Literal["ON", "OFF"] = "ON"

@dataclass
class ArbitraryWaveformSettings:
    """Arbitrary waveform generator settings."""
    csv_file: str
    sample_rate: Optional[float] = None  # Hz
    inst_file_path: str = "/home/storage/userData/arb_waveform.csv"
    run_mode: Literal["REPetitive", "SINGle"] = "REPetitive"

@dataclass
class DataAcquisitionSettings:
    """Data acquisition settings."""
    points: int = 1000
    format: Literal["REAL,32"] = "REAL,32"
    byte_order: Literal["LSBFirst", "MSBFirst"] = "LSBFirst"
    chunk_size: int = 100000
    sample_rate: float = 1e9  # Default to 1 GSa/s
    record_length: int = 1000  # Number of points to acquire
    acquisition_type: Literal["NORMAL", "AVERAGE", "PEAK", "HRESOLUTION"] = "NORMAL"
    num_averages: int = 1  # Number of averages when using AVERAGE mode

@dataclass
class PlotSettings:
    """Plot configuration settings."""
    figure_size: Tuple[int, int] = (12, 6)
    show_grid: bool = True
    show_info: bool = True
    dpi: int = 300

class MXO44:
    """Class for controlling Rohde&Schwarz MXO44 oscilloscope."""
    
    def __init__(self):
        """Initialize the MXO44 instrument."""
        self.instrument: Optional[RsInstrument] = None
        self.plot_settings = PlotSettings()
        self.data_settings = DataAcquisitionSettings()
        
    def connect(self, resource: str = "USB0::0x0AAD::0x0197::1335.5050k04-201064::INSTR") -> bool:
        """Connect to the instrument.
        
        Args:
            resource (str): VISA resource string
        """
        try:
            self.instrument = RsInstrument(
                resource,
                True,  # ID Query
                True   # Reset
            )
            
            # Configure instrument settings
            self.instrument.visa_timeout = 5000
            self.instrument.opc_timeout = 8000
            self.instrument.instrument_status_checking = True
            
            return True
            
        except Exception as e:
            print(f"Error connecting to instrument: {str(e)}")
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the instrument."""
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            
    def write(self, command: str) -> None:
        """Send a command to the instrument."""
        if not self.instrument:
            raise RuntimeError("Not connected to instrument")
        self.instrument.write(command)
        
    def query(self, command: str) -> str:
        """Send a query to the instrument and return the response."""
        if not self.instrument:
            raise RuntimeError("Not connected to instrument")
        return self.instrument.query_str(command)
        
    def query_float(self, command: str) -> float:
        """Send a query to the instrument and return the response as float."""
        if not self.instrument:
            raise RuntimeError("Not connected to instrument")
        return self.instrument.query_float(command)
        
    def configure_channel(self, channel: int, settings: Union[Dict[str, Any], ChannelSettings]) -> None:
        """Configure an oscilloscope channel."""
        if isinstance(settings, dict):
            settings = ChannelSettings(**settings)
            
        if not 1 <= channel <= 4:
            raise ValueError("Channel must be between 1 and 4")
            
        self.write(f'CHAN{channel}:STAT {settings.state}')
        self.write(f'CHAN{channel}:COUP {settings.coupling}')
        self.write(f'CHAN{channel}:RANG {settings.range}')
        self.write(f'CHAN{channel}:OFFS {settings.offset}')
        
    def configure_trigger(self, settings: Union[Dict[str, Any], TriggerSettings]) -> None:
        """Configure the oscilloscope trigger."""
        if isinstance(settings, dict):
            settings = TriggerSettings(**settings)
            
        self.write(f'TRIG:MODE {settings.mode}')
        source = settings.source.replace("CH", "C")
        self.write(f'TRIG:EVEN1:SOUR {source}')
        self.write(f'TRIG:EVEN1:LEV1:VAL {settings.level}')
        self.write('TRIG:EVEN1:TYPE EDGE')
        self.write(f'TRIG:EVEN1:EDGE:SLOP {settings.slope}')
        
    def configure_timebase(self, settings: Union[Dict[str, Any], TimebaseSettings]) -> None:
        """Configure the oscilloscope timebase."""
        if isinstance(settings, dict):
            settings = TimebaseSettings(**settings)
            
        self.write(f'TIM:SCAL {settings.scale:E}')
        
    def configure_waveform_generator(self, settings: Union[Dict[str, Any], WaveformSettings]) -> None:
        """Configure the waveform generator."""
        if isinstance(settings, dict):
            settings = WaveformSettings(**{k: (WaveformType[v.upper()] if k == "function" else v) 
                                        for k, v in settings.items()})
            
        # Reset waveform generator
        self.write('WGENerator1:PRES')
        
        # Set function
        self.write(f'WGENerator1:FUNCtion:SELect {settings.function.value}')
        
        # Set common parameters
        if settings.function != WaveformType.DC:
            self.write(f'WGENerator1:FREQ {settings.frequency}')
            self.write(f'WGENerator1:VOLT:VPP {settings.amplitude}')
            
        self.write(f'WGENerator1:VOLT:OFFS {settings.offset}')
        
        # Set waveform-specific parameters
        if settings.function == WaveformType.SQUARE:
            self.write(f'WGENerator1:FUNCtion:SQUare:DCYCle {settings.duty_cycle}')
        elif settings.function == WaveformType.RAMP:
            self.write(f'WGENerator1:FUNCtion:RAMP:SYMMetry {settings.symmetry}')
        elif settings.function == WaveformType.PULSE:
            self.write(f'WGENerator1:FUNCtion:PULSe:WIDTh {settings.width}')
            
        # Enable output
        self.write(f'WGENerator1:ENABle {settings.output}')
        
    def load_arbitrary_waveform(self, csv_file: str) -> Tuple[float, List[float]]:
        """Load arbitrary waveform data from CSV file."""
        voltage_values = []
        sample_rate = None
        time_values = []
        
        with open(csv_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)
            
            if first_line.startswith('Rate'):
                rate_line = f.readline().strip()
                sample_rate = float(rate_line.split('=')[1].split('//')[0].strip())
                
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('//'):
                        voltage_values.append(float(line))
                        
            else:
                try:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) == 2:
                            time_values.append(float(row[0]))
                            voltage_values.append(float(row[1]))
                        elif len(row) == 1:
                            voltage_values.append(float(row[0]))
                except:
                    f.seek(0)
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('//'):
                            voltage_values.append(float(line))
                            
        if not sample_rate:
            if time_values:
                time_diffs = np.diff(time_values)
                avg_time_diff = np.mean(time_diffs)
                sample_rate = 1 / avg_time_diff
            else:
                sample_rate = 100000.0
                
        return float(sample_rate), voltage_values

    def configure_arbitrary_waveform(self, settings: Union[Dict[str, Any], ArbitraryWaveformSettings]) -> None:
        """Configure arbitrary waveform generator."""
        if isinstance(settings, dict):
            settings = ArbitraryWaveformSettings(**settings)
            
        # Load waveform data
        sample_rate, voltage_values = self.load_arbitrary_waveform(settings.csv_file)
        if settings.sample_rate:  # Override sample rate if specified
            sample_rate = settings.sample_rate
            
        # Create temporary file
        temp_file = "temp_arb_waveform.csv"
        with open(temp_file, 'w') as f:
            f.write(f'Rate = {sample_rate}  // Sample rate for the ARB file\n')
            for voltage in voltage_values:
                f.write(f'{voltage}\n')
        
        try:
            # Transfer file to instrument
            self.instrument.send_file_from_pc_to_instrument(temp_file, settings.inst_file_path)
            
            # Configure generator
            self.write('WGENerator1:SOURce FUNCgen')
            self.write('WGENerator1:FUNCtion:SELect ARBitrary')
            self.write('WGENerator1:SOURce ARBGenerator')
            self.write(f"WGENerator1:ARBGen:NAME '{settings.inst_file_path}'")
            self.write('WGENerator1:ARBGen:OPEN')
            self.write(f'WGENerator1:ARBGen:SRATe {sample_rate}')
            self.write(f'WGENerator1:ARBGen:RUNMode {settings.run_mode}')
            self.write('WGENerator1:ENABle ON')
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def configure_acquisition(self, settings: Union[Dict[str, Any], DataAcquisitionSettings]) -> None:
        """Configure acquisition settings.
        
        Args:
            settings: Acquisition settings
        """
        if isinstance(settings, dict):
            settings = DataAcquisitionSettings(**settings)
            
        self.data_settings = settings
        
        # Set acquisition type and number of averages
        self.write(f'ACQuire:TYPE {settings.acquisition_type}')
        if settings.acquisition_type == "AVERAGE":
            self.write(f'ACQuire:COUNt {settings.num_averages}')
            
        # Set record length (number of points)
        self.write(f'ACQuire:POINts {settings.record_length}')
        
        # Set sampling rate
        self.write(f'ACQuire:SRATe {settings.sample_rate}')
        
        # Configure data format
        self.write(f'FORMat:DATA {settings.format}')
        self.write(f'FORMat:BORDer {settings.byte_order}')
        
        # Verify settings
        actual_rate = self.query_float('ACQuire:SRATe?')
        actual_points = self.query_float('ACQuire:POINts?')
        print(f"Configured acquisition settings:")
        print(f"Sample rate: {actual_rate/1e6:.2f} MSa/s")
        print(f"Record length: {actual_points} points")
        print(f"Acquisition type: {self.query('ACQuire:TYPE?')}")
        if settings.acquisition_type == "AVERAGE":
            print(f"Number of averages: {self.query_float('ACQuire:COUNt?')}")

    def capture_waveform(self, channel: int) -> Dict[str, Any]:
        """Capture waveform data from specified channel.
        
        Args:
            channel (int): Channel number (1-4)
            
        Returns:
            dict: Dictionary containing waveform data and metadata
        """
        if not 1 <= channel <= 4:
            raise ValueError("Channel must be between 1 and 4")
            
        # Keep display on while under remote control
        self.write('SYSTem:DISPlay:UPDate ON')
        
        # Perform single acquisition
        self.instrument.write_str_with_opc("RUNsingle")
        print('MXO triggered, capturing data ...')
        
        # Get number of sample points
        points = self.instrument.query_float("ACQ:POIN?")
        print(f'Number of sample points: {points}')
        
        # Configure waveform data format for binary transfer
        self.instrument.write_str("FORMat:DATA REAL,32;:FORMat:BORDer LSBFirst")
        self.instrument.bin_float_numbers_format = BinFloatFormat.Single_4bytes
        self.instrument.data_chunk_size = 100000  # Transfer in blocks of 100k bytes
        
        # Get waveform data
        print('Now start to transfer binary waveform data. Please wait...')
        voltage_data = self.instrument.query_bin_or_ascii_float_list("CHAN:DATA?")
        
        # Get waveform parameters
        x_increment = self.query_float('TIM:SCAL?') / 10  # Time per division divided by 10
        x_origin = -5 * x_increment  # Center the waveform
        y_increment = self.query_float(f'CHAN{channel}:RANG?') / 10  # Volts per division divided by 10
        y_origin = self.query_float(f'CHAN{channel}:OFFS?')
        
        # Generate time values
        time_data = [x_origin + i * x_increment for i in range(len(voltage_data))]
        
        return {
            "time": time_data,
            "voltage": voltage_data,
            "metadata": {
                "x_increment": x_increment,
                "x_origin": x_origin,
                "y_increment": y_increment,
                "y_origin": y_origin,
                "points": len(voltage_data)
            }
        }
        
    def save_waveform_data(self, channel: int, filename: str) -> None:
        """Save waveform data to CSV file."""
        data = self.capture_waveform(channel)
        
        with open(filename, 'w') as f:
            f.write(f"# Channel: {channel}\n")
            for key, value in data["metadata"].items():
                f.write(f"# {key}: {value}\n")
            
            f.write("Time (s),Voltage (V)\n")
            for t, v in zip(data["time"], data["voltage"]):
                f.write(f"{t},{v}\n")
                
    def plot_waveform(self, channel: int, filename: Optional[str] = None) -> None:
        """Plot waveform data from specified channel."""
        data = self.capture_waveform(channel)
        
        plt.figure(figsize=self.plot_settings.figure_size)
        plt.plot(data["time"], data["voltage"], linewidth=1.5)
        
        if self.plot_settings.show_grid:
            plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        plt.title(f'Channel {channel} Waveform')
        
        if self.plot_settings.show_info:
            metadata = data["metadata"]
            info_text = (
                f"Points: {metadata['points']}\n"
                f"Time/div: {metadata['x_increment']*10:.3e} s\n"
                f"Volts/div: {metadata['y_increment']*10:.3f} V"
            )
            plt.annotate(info_text, xy=(0.02, 0.98), xycoords='axes fraction',
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        if filename:
            plt.savefig(filename, dpi=self.plot_settings.dpi, bbox_inches='tight')
            print(f"Plot saved to {filename}")
        
        plt.show()

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 