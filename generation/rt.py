import numpy as np
import csv
import matplotlib.pyplot as plt
import pyfar as pf
import pyrato as ra
from glob import glob


def save_rt60s(filename, rt60s):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Frequency (Hz)", "RT60 (s)"])
        for freq, rt60 in rt60s.items():
            writer.writerow([freq, rt60])


def main():
    # rooms are all subdirs of the data directory
    rooms = glob("data/*/")
    for room in rooms:
        current_path = room

        try:
            ir_orig = pf.io.read_audio(f"{current_path}/ir.wav")
        except Exception as e:
            print(f"Impulse response file not found in {current_path}. Skipping...")
            continue

        bands = [50, 63, 80, 100, 125, 250, 500, 1000, 2000, 4000, 8000]
        band_rt60s = {}

        ir_orig = pf.dsp.time_window(
            ir_orig,
            [0, 0.01, ir_orig.signal_length - 0.1, ir_orig.signal_length],
            unit="s",
            crop="window",
        )

        for center_freq in bands:
            ir = pf.dsp.filter.butterworth(
                ir_orig,
                4,
                [center_freq / np.sqrt(2), center_freq * np.sqrt(2)],
                "bandpass",
            )
            try:
                edc = ra.energy_decay_curve_chu_lundeby(
                    ir,
                    is_energy=False,
                    freq=center_freq,
                    plot=False,
                    time_shift=True,
                    normalize=True,
                )
                band_rt60s[center_freq] = ra.reverberation_time_energy_decay_curve(
                    edc, T="T60"
                )[0]
            except Exception as e:
                print(f"Error processing {current_path}: {e}")
                pf.plot.time_freq(ir, dB_time=True)
                plt.show()
                band_rt60s[center_freq] = 9999999
                continue

        rt60_filename = f"{current_path}/rt60.csv"
        save_rt60s(rt60_filename, band_rt60s)
        print(f"RT60 data saved as '{rt60_filename}'")


if __name__ == "__main__":
    main()
