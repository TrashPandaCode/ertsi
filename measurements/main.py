
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import pyfar as pf
import time
import pyroomacoustics as pra

def measure_rt60(sample_rate=48000, duration=3):

    print("Preparing measurement...")
    
    # Create exponential sine sweep
    f_start = 20  # Hz
    f_stop = 20000  # Hz
    sweep_samples = int(duration * sample_rate)
    
    # Using pyfar to generate the sweep
    sweep = pf.signals.exponential_sweep_freq(
        n_samples=sweep_samples,
        frequency_range=[f_start, f_stop],
        sampling_rate=sample_rate,
        start_margin=5000,
        stop_margin=1000,
    )
    
    # # Apply fade-in and fade-out to avoid clicks
    # fade_samples = int(0.01 * sample_rate)  # 10 ms fade
    # fade_in = np.linspace(0, 1, fade_samples)
    # fade_out = np.linspace(1, 0, fade_samples)
    
    # sweep_signal = sweep.time.copy()
    # sweep_signal[:fade_samples] *= fade_in
    # sweep_signal[-fade_samples:] *= fade_out
    
    # Normalize to avoid clipping
    # sweep_signal = 0.9 * sweep / np.max(np.abs(sweep))
    
    silence = pf.Signal(
        np.zeros(int(sample_rate * 2)),  # 2 seconds of silence
        sampling_rate=sample_rate,
    )
    playback_signal = np.append(sweep.time, silence.time)
    playback_signal = pf.Signal(
        playback_signal,
        sampling_rate=sample_rate,
    )

    # Add silence at the end to capture full reverb tail
    # silence_duration = 2  # seconds
    # silence_samples = int(silence_duration * sample_rate)
    # playback_signal = np.concatenate([sweep, np.zeros(silence_samples)])

    
    # Prepare for playback and recording
    print("Starting measurement. Please ensure the room is quiet...")
    time.sleep(1)
    
    # Perform the measurement
    recorded_signal = sd.playrec(
        playback_signal.time.T,
        sample_rate,
        channels=1,
        blocking=True
    ).flatten()
    
    print("Measurement completed. Processing data...")
    
    #remove the first 3 seconds of the recorded signal to avoid the initial transient
    recorded_signal = recorded_signal[3 * sample_rate:]

    # Calculate RT60 using Schroeder integration method
    rt60_values = pra.experimental.rt60.measure_rt60(
        recorded_signal,
        sample_rate,
        plot=True,
    )
    
    return recorded_signal, rt60_values


sample_rate = 48000
duration = 3
print("Preparing to measure RT60 with sample rate", sample_rate, "Hz and duration", duration, "s.")

# Run the measurement
ir, rt60_values = measure_rt60(sample_rate, duration)


pf.plot.time(ir)


print(rt60_values)
ir = pf.Signal(ir, sampling_rate=sample_rate)
pf.plot.time(ir)


