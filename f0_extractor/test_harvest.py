from pitch_extract import Harvest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import librosa


def test_dummy(test: int = 0):
    print(test)
    harvest = Harvest(fs=16000, n_fft=256, hop_length=128,
                      use_token_averaged_f0=False, use_log_f0=False)
    cur_dir = Path(__file__).parent
    data, sr = librosa.load(
        str(cur_dir / "ROHAN4600_0001.wav"), dtype=np.double)
    pitch = harvest.forward(data)
    print(len(pitch))
    print(len(data)/sr)
    print(len(data)/128)
    print(128/16000)
    plt.plot(pitch)

    plt.savefig(cur_dir / "test_h.png")


test_dummy()
