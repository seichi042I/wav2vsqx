from pitch_extract import Dio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import librosa


def test_dummy(test: int = 0):
    print(test)
    dio = Dio(fs=16000, n_fft=256, hop_length=128,
              use_token_averaged_f0=False, use_log_f0=False)
    cur_dir = Path(__file__).parent
    data, sr = librosa.load(
        str(cur_dir / "ROHAN4600_4432_16kHz.wav"), dtype=np.double)
    pitch = dio.forward(data)
    plt.plot(pitch)

    plt.savefig(cur_dir / "test.png")


test_dummy()
