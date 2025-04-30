import numpy as np
import sounddevice as sd
import scipy.signal as signal
import matplotlib.pyplot as plt
import pyroomacoustics as pra
from scipy.io import wavfile
import csv
from datetime import datetime
import os

def print_device_names():    
    input_device = sd.query_devices(sd.default.device[1])['name']
    output_device = sd.query_devices(sd.default.device[1])['name']
    
    print(f"\nSelected Microphone: {input_device}")
    print(f"Selected Speaker: {output_device}\n")

def generate_sweep(duration=5, fs=48000, f_start=20, f_end=20000):
    t = np.linspace(0, duration, int(fs * duration))
    sweep = signal.chirp(t, f0=f_start, f1=f_end, t1=duration, method='logarithmic')
    sweep *= np.hanning(len(sweep))
    return sweep

def record_rir(fs=48000, sweep_duration=5, silence_duration=1):
    sweep = generate_sweep(duration=sweep_duration, fs=fs)
    sweep = np.concatenate([np.zeros(int(fs * silence_duration)), sweep, np.zeros(int(fs * silence_duration))])

    print("Starting playback and recording...")
    recording = sd.playrec(sweep, samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Recording finished.")
    
    return sweep, recording[:,0]

def deconvolve(recorded, original):
    # Cross-correlate the original sweep with the recorded signal
    correlation = signal.correlate(recorded, original, mode='full')
    
    # Find the index of the maximum correlation
    delay = correlation.argmax() - (len(original) - 1)
    
    # The impulse response is the portion of the correlation that starts at the peak
    ir = correlation[delay:]
    
    # Normalize the impulse response
    ir = ir / np.max(np.abs(ir))  # Normalize to avoid clipping
    return ir

def save_wav(filename, data, fs):
    data_normalized = data / np.max(np.abs(data))
    wavfile.write(filename, fs, (data_normalized * 32767).astype(np.int16))

def save_rt60s(filename, rt60s):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Frequency (Hz)', 'RT60 (s)'])
        for freq, rt60 in rt60s.items():
            writer.writerow([freq, rt60])

def main():
    fs = 48000
    sweep_duration = 5
    silence_duration = 2

    print_device_names()

    room_name = input("Enter the room name: ")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"recordings/{room_name}/{timestamp}"
    os.makedirs(folder, exist_ok=True)

    sweep, recorded = record_rir(fs, sweep_duration, silence_duration)
    ir = deconvolve(recorded, sweep)
    ir = ir / np.max(np.abs(ir))
    ir = ir[int(0.1 * fs):]

    # t_ir = np.arange(len(ir)) / fs
    # plt.figure(figsize=(10, 4))
    # plt.plot(t_ir, ir)
    # plt.title("Measured Room Impulse Response")
    # plt.xlabel("Time [s]")
    # plt.ylabel("Amplitude")
    # plt.grid()
    # plt.show()

    recorded_filename = os.path.join(folder, f"recorded_{timestamp}.wav")
    save_wav(recorded_filename, recorded, fs)
    ir_filename = os.path.join(folder, f"impulse_response_{timestamp}.wav")
    save_wav(ir_filename, ir, fs)
    print(f"Impulse response saved as '{ir_filename}'")

    bands = [125, 250, 500, 1000, 2000, 4000, 8000]
    band_rt60s = {}

    for center_freq in bands:
        sos = signal.butter(4, [center_freq/np.sqrt(2), center_freq*np.sqrt(2)], btype='band', fs=fs, output='sos')
        filtered_ir = signal.sosfilt(sos, ir)
        rt60_band = pra.experimental.measure_rt60(filtered_ir, fs, plot=True)
        band_rt60s[center_freq] = rt60_band
        
        plot_filename = os.path.join(folder, f"energy_decay_{center_freq}Hz_{timestamp}.svg")
        plt.title(f"Energy Decay - {center_freq} Hz")
        plt.savefig(plot_filename, format="svg")
        plt.close()

    rt60_filename = os.path.join(folder, f"rt60_data_{timestamp}.csv")
    save_rt60s(rt60_filename, band_rt60s)
    print(f"RT60 data saved as '{rt60_filename}'")

    print("RT60s per band:")
    for cf, rt in band_rt60s.items():
        print(f"{cf} Hz: {rt:.2f} s")

if __name__ == "__main__":
    main()
