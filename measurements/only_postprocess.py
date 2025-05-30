import numpy as np
import csv
import os
import pyfar as pf
import pyrato as ra
import matplotlib.pyplot as plt


def save_rt60s(filename, rt60s):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Frequency (Hz)', 'RT60 (s)'])
        for freq, rt60 in rt60s.items():
            writer.writerow([freq, rt60])


def main():
    fs = 48000
    sweep_duration = 5

    sweep = pf.signals.exponential_sweep_time(
        n_samples=int(sweep_duration * fs),
        frequency_range=(20, 20000),
        sampling_rate=fs,
    )
    sweep = pf.dsp.pad_zeros(sweep, pad_width=1 * sweep.sampling_rate)

    # iterate over all folders in recordings and then over all subfolders
    for root, dirs, files in os.walk("recordings"):
        for room in dirs:
            # use only last measurement of each room
            room_path = os.path.join(root, room)
            subdirs = [d for d in os.listdir(
                room_path) if os.path.isdir(os.path.join(room_path, d))]
            if not subdirs:
                continue
            measurement = sorted(subdirs)[-1]
            current_path = os.path.join(root, room, measurement)

            for file in os.listdir(current_path):
                if file.startswith("energy_decay_") and file.endswith(".svg"):
                    os.remove(os.path.join(current_path, file))
                if file.startswith("impulse_response_processed_") and file.endswith(".wav"):
                    os.remove(os.path.join(current_path, file))

            ir_orig = pf.io.read_audio(
                f"{current_path}/impulse_response_{measurement}.wav")
            ir_window = pf.dsp.time_window(
                ir_orig, [0, .01, 3, 3.1], unit='s', crop='window')

            bands = [50, 63, 80, 100, 125, 250, 500,
                     1000, 2000, 4000, 8000, 12000, 16000]
            band_rt60s = {}

            try:
                for center_freq in bands:
                    ir = pf.dsp.filter.butterworth(
                        ir_window, 4, [center_freq/np.sqrt(2), center_freq*np.sqrt(2)], 'bandpass')
                    edc = ra.energy_decay_curve_chu_lundeby(
                        ir, is_energy=False, freq=center_freq, plot=False, time_shift=True, normalize=True)

                    band_rt60s[center_freq] = ra.reverberation_time_energy_decay_curve(
                        edc, T="T60")[0]

                rt60_filename = f"{current_path}/rt60_data_new_{measurement}.csv"
                save_rt60s(rt60_filename, band_rt60s)
                print(f"RT60 data saved as '{rt60_filename}'")
            except Exception as e:
                print(f"Error processing {current_path}: {e}")
                pf.plot.time_freq(ir_window, dB_time=True)
                plt.savefig(os.path.join(
                    current_path, f"impulse_response_{measurement}.svg"), format="svg")
                plt.close()
                continue


if __name__ == "__main__":
    main()
