"""Generate arbitrary waveforms from MNIST dataset for the MXO44 oscilloscope.

This script loads a subset of the MNIST dataset, converts images to
pulse waveforms, and saves them in a format that can be loaded by
the MXO44 oscilloscope's arbitrary waveform generator.
"""
import os
import numpy as np
import torch
import random
from torchvision import datasets, transforms
from torch.utils.data import Subset
import matplotlib.pyplot as plt
import h5py
import csv

# Set random seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# Define constants
DATA_DIR = "mnist_data"
WAVEFORM_DIR = "waveform_data/mnist"
NUM_SAMPLES = 100  # Number of MNIST samples to convert
BALANCED = True  # If True, select an equal number of samples from each digit

# Define transformation for MNIST
transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Lambda(lambda x: (x > 0.35).float()),  # Threshold to create binary image
])

# Pulse parameters
PULSE_PARAMS = {
    "pixel_time": 5.0,    # Duration for each pixel (in microseconds)
    "gap_time": 1.0,      # Gap between pixels (in microseconds)
    "pulse_amplitude": 1.0,  # Amplitude of the pulse
    "dt": 1.0,            # Time step (in microseconds)
    "mode": "row"         # Read image pixels by row
}


def load_mnist_dataset():
    """Load the MNIST dataset."""
    print(f"Loading MNIST dataset from {DATA_DIR}...")
    os.makedirs(DATA_DIR, exist_ok=True)
    train_set = datasets.MNIST(root=DATA_DIR, train=True, download=True, transform=transform)
    return train_set


def get_balanced_subset(dataset, num_samples):
    """Select a balanced subset of the dataset with equal samples per class."""
    targets = np.array(dataset.targets)
    indices = []
    samples_per_class = num_samples // 10  # 10 digits in MNIST
    
    for cls in range(10):
        class_indices = np.where(targets == cls)[0]
        selected = np.random.choice(class_indices, samples_per_class, replace=False)
        indices.extend(selected)
    
    print(f"Selected {len(indices)} samples ({samples_per_class} per digit)")
    return Subset(dataset, indices)


def get_random_subset(dataset, num_samples):
    """Select a random subset of the dataset."""
    indices = np.random.choice(len(dataset), num_samples, replace=False)
    print(f"Selected {len(indices)} random samples")
    return Subset(dataset, indices)


def image_to_pulse(image_tensor, **kwargs):
    """Convert an image tensor to a pulse waveform.
    
    Args:
        image_tensor: A 2D tensor representing the image
        **kwargs: Pulse parameters:
            - pixel_time: Duration for each pixel (µs)
            - gap_time: Gap between pixels (µs)
            - pulse_amplitude: Amplitude of the pulse
            - dt: Time step (µs)
            - mode: 'row' or 'col' for reading image pixels
            
    Returns:
        Tuple of (pulse_array, time_array)
    """
    # Extract parameters
    pixel_time = kwargs.get("pixel_time", 5.0)  # µs
    gap_time = kwargs.get("gap_time", 1.0)      # µs
    pulse_amplitude = kwargs.get("pulse_amplitude", 1.0)
    dt = kwargs.get("dt", 1.0)                  # µs
    mode = kwargs.get("mode", "row")
    
    # Flatten the image (either row-wise or column-wise)
    if mode == "col":
        image_flat = image_tensor.numpy().flatten(order="F")
    else:
        image_flat = image_tensor.flatten().numpy()
    
    # Calculate steps
    num_pixels = image_flat.shape[0]
    steps_on = int(pixel_time / dt)
    steps_gap = int(gap_time / dt)
    steps_per_pixel = steps_on + steps_gap
    total_steps = num_pixels * steps_per_pixel
    
    # Create pulse array
    pulse_array = np.zeros(total_steps, dtype=np.float64)
    for i, intensity in enumerate(image_flat):
        start = i * steps_per_pixel
        pulse_array[start : start + steps_on] = intensity * pulse_amplitude
    
    # Create time array (in microseconds)
    time_array = np.arange(0, total_steps * dt, dt)
    
    return pulse_array, time_array


def save_waveform_csv(pulse_array, time_array, filename, sample_rate=None):
    """Save waveform data to CSV in a format the oscilloscope can read.
    
    Args:
        pulse_array: Array of voltage values
        time_array: Array of time values
        filename: Output filename
        sample_rate: Sample rate in Hz (computed from time_array if None)
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Calculate sample rate if not provided
    if sample_rate is None:
        # Get time step in seconds (convert from microseconds)
        dt_sec = (time_array[1] - time_array[0]) / 1e6
        sample_rate = 1.0 / dt_sec  # Hz
    
    with open(filename, 'w', newline='') as f:
        f.write(f"Rate = {sample_rate}  // Sample rate for the ARB file in Hz\n")
        for voltage in pulse_array:
            f.write(f"{voltage}\n")
    
    print(f"Saved waveform to {filename}")


def save_waveform_h5(pulse_list, time_array, label_list, filename, params):
    """Save multiple waveforms to an HDF5 file.
    
    Args:
        pulse_list: List of pulse arrays
        time_array: Time array (same for all pulses)
        label_list: List of labels for each pulse
        filename: Output filename
        params: Parameters used to generate the pulses
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with h5py.File(filename, "w") as f:
        f.create_dataset("pulses", data=np.stack(pulse_list), compression="gzip")
        f.create_dataset("time", data=time_array.astype(np.float32))
        f.create_dataset("label", data=np.array(label_list, dtype=np.int64))
        
        # Store parameters as attributes
        for k, v in params.items():
            f.attrs[k] = v
    
    print(f"Saved {len(pulse_list)} waveforms to {filename}")


def plot_example_waveforms(pulse_arrays, time_array, labels, filename=None):
    """Plot example waveforms for visualization.
    
    Args:
        pulse_arrays: List of pulse arrays
        time_array: Time array (same for all pulses)
        labels: List of labels for each pulse
        filename: If provided, save the plot to this file
    """
    num_examples = min(5, len(pulse_arrays))
    fig, axes = plt.subplots(num_examples, 1, figsize=(10, 2*num_examples))
    
    for i in range(num_examples):
        ax = axes[i] if num_examples > 1 else axes
        ax.plot(time_array, pulse_arrays[i])
        ax.set_title(f"Digit: {labels[i]}")
        ax.set_xlabel("Time (µs)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
    
    plt.tight_layout()
    
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename, dpi=300)
        print(f"Saved example plot to {filename}")
    else:
        plt.show()


def main():
    """Main function to generate MNIST waveforms."""
    # Create output directories
    os.makedirs(WAVEFORM_DIR, exist_ok=True)
    
    # Load MNIST dataset
    mnist_dataset = load_mnist_dataset()
    
    # Get subset of samples
    if BALANCED:
        subset = get_balanced_subset(mnist_dataset, NUM_SAMPLES)
    else:
        subset = get_random_subset(mnist_dataset, NUM_SAMPLES)
    
    # Convert images to pulses
    pulse_arrays = []
    label_list = []
    time_array = None
    
    print(f"Converting {len(subset)} images to waveforms...")
    for i, (image, label) in enumerate(subset):
        pulse_array, time_arr = image_to_pulse(image, **PULSE_PARAMS)
        
        if time_array is None:
            time_array = time_arr
        
        pulse_arrays.append(pulse_array)
        label_list.append(label)
        
        # Save individual CSV file for each waveform
        csv_filename = os.path.join(WAVEFORM_DIR, f"mnist_digit_{label}_{i}.csv")
        save_waveform_csv(pulse_array, time_array, csv_filename)
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(subset)} images")
    
    # Save all waveforms to a single HDF5 file
    h5_filename = os.path.join(WAVEFORM_DIR, "mnist_waveforms.h5")
    save_waveform_h5(pulse_arrays, time_array, label_list, h5_filename, PULSE_PARAMS)
    
    # Plot example waveforms
    plot_filename = os.path.join(WAVEFORM_DIR, "mnist_examples.png")
    plot_example_waveforms(pulse_arrays, time_array, label_list, plot_filename)
    
    print("Done generating MNIST waveforms!")
    print(f"Generated {len(pulse_arrays)} waveforms in '{WAVEFORM_DIR}'")
    print(f"CSV files can be loaded directly into the oscilloscope's arbitrary waveform generator")


if __name__ == "__main__":
    main() 