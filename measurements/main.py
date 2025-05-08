import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import wavfile
import csv
from datetime import datetime
import os
import pyfar as pf
import pyrato as ra


def print_device_names():
    input_device = sd.query_devices(sd.default.device[1])['name']
    output_device = sd.query_devices(sd.default.device[1])['name']

    print(f"\nSelected Microphone: {input_device}")
    print(f"Selected Speaker: {output_device}\n")


def record_rir(fs=48000, sweep_duration=5, silence_duration=1):
    sweep = pf.signals.exponential_sweep_time(
        n_samples=int(sweep_duration * fs),
        frequency_range=(20, 20000),
        sampling_rate=fs,
    )
    sweep = pf.dsp.pad_zeros(sweep, pad_width=1 * sweep.sampling_rate)

    print("Starting playback and recording...")
    recording = sd.playrec(sweep.time.T, samplerate=fs,
                           channels=1, blocking=True)
    print(recording.shape)
    print("Recording finished.")

    return recording, sweep


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

    recording, sweep = record_rir(fs, sweep_duration, silence_duration)

    rec_signal = pf.Signal(recording[:, 0].T, fs)
    save_wav(os.path.join(
        folder, f"recording_{timestamp}.wav"), rec_signal.time.T, fs)

    print(rec_signal)

    ax = pf.plot.time_freq(rec_signal)
    ax[0].set_title("Recorded Signal Response")
    plt.savefig(os.path.join(
        folder, f"recorded_signal_{timestamp}.svg"), format="svg")

    reference = sweep
    inverted = pf.dsp.regularized_spectrum_inversion(reference, (20, 20000))
    ir = rec_signal * inverted

    ir_processed = pf.dsp.filter.butterworth(ir, 8, 40, 'highpass')

    ax = pf.plot.time_freq(ir, dB_time=True, color=[.6, .6, .6], label='raw')
    pf.plot.time_freq(ir_processed, dB_time=True, label='post-processed')
    ax[0].set_xlim(0, 1.5)  # adjust if needed
    ax[1].legend(loc='lower left')
    ax[0].set_title("Impulse Response")
    plt.savefig(os.path.join(
        folder, f"impulse_response_{timestamp}.svg"), format="svg")
    plt.close()

    save_wav(os.path.join(
        folder, f"impulse_response_{timestamp}.wav"), ir.time.T, fs)

    # bands = [50, 63, 80, 100, 125, 250, 500,
    #          1000, 2000, 4000, 8000, 12000, 16000]
    # band_rt60s = {}

    # for center_freq in bands:
    #     ir_filtered = pf.dsp.filter.butterworth(
    #         ir_processed, 4, [center_freq/np.sqrt(2), center_freq*np.sqrt(2)], 'bandpass')
    #     edc = ra.energy_decay_curve_chu_lundeby(
    #         ir_filtered, is_energy=False, freq=center_freq, plot=False, time_shift=True, normalize=True)

    #     band_rt60s[center_freq] = ra.reverberation_time_energy_decay_curve(
    #         edc, T="T60")[0]

    # rt60_filename = os.path.join(folder, f"rt60_data_{timestamp}.csv")
    # save_rt60s(rt60_filename, band_rt60s)
    # print(f"RT60 data saved as '{rt60_filename}'")

    # print("RT60s per band:")
    # for cf, rt in band_rt60s.items():
    #     print(f"{cf} Hz: {rt:.2f} s")


if __name__ == "__main__":
    main()
