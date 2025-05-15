import time
import json

import numpy as np
import matplotlib.pyplot as plt
import pyroomacoustics as pra
import pyfar as pf
import pyrato as ra


def get_rir(polygons, height=3):
    pol = np.array(polygons).T

    # initial acoustic coeffs
    m = pra.make_materials(
        east="hard_surface",
        west="hard_surface",
        north="hard_surface",
        south="glass_window",
        floor="linoleum_on_concrete",
        ceiling="ceiling_perforated_gypsum_board",
    )

    """
    We can observe that the order 17 is not sufficient when using only the ISM.
    RT is able to simulate the whole tail.
    Also, the RT60 of ISM is not completely consistent with the Hybrid method as it
    doesn't include scattering. Scattering reduces the length of the reverberent tail.
    """
    room = pra.ShoeBox(
        # pol,
        [4, 6, 3],
        fs=48000,
        max_order=30,  # 3 is suggested for ray tracing
        materials=m,
        # ray_tracing=True,
        air_absorption=True,
    )

    # # extruding the 2D room
    # me = pra.make_materials(
    #     floor="linoleum_on_concrete", ceiling="ceiling_perforated_gypsum_board"
    # )
    # room.extrude(height, materials=me)

    room.add_source([0.5, 3, 1])
    room.add_microphone([3.5, 5, 0.75])

    # room.set_ray_tracing()

    s = time.perf_counter()
    room.compute_rir()
    print("Computation time:", time.perf_counter() - s)

    return room.rir[0][0], room


if __name__ == "__main__":
    data = json.load(open("data.json"))
    rir, room = get_rir(
        data["room_verts"],
        height=3,
    )

    rir_signal = pf.Signal(rir, 48000)
    bands = [100, 125, 250, 500, 1000, 2000, 4000, 8000, 12000, 16000]
    band_rt60s = {}
    for center_freq in bands:
        try:
            ir = pf.dsp.filter.butterworth(
                rir_signal,
                4,
                [center_freq / np.sqrt(2), center_freq * np.sqrt(2)],
                "bandpass",
            )
            edc = ra.energy_decay_curve_chu_lundeby(
                ir,
                is_energy=False,
                freq=center_freq,
                plot=False,
                time_shift=True,
                normalize=True,
            )
            # plt.show()

            band_rt60s[center_freq] = ra.reverberation_time_energy_decay_curve(
                edc, T="T60"
            )[0]
        except Exception as e:
            print(f"Error processing band {center_freq}: {e}")
            continue

    print("Band RT60s: ", band_rt60s)

    room.plot(img_order=0)
    plt.title("The room we have simulated")

    room.plot_rir()
    plt.show()
