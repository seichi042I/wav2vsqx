# Copyright 2020 Nagoya University (Tomoki Hayashi)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""F0 extractor using DIO + Stonemask algorithm."""

import logging
from typing import Any, Dict, Tuple, Union

import numpy as np
import pyworld
from scipy.interpolate import interp1d


class Dio:
    """F0 estimation with dio + stonemask algorithm.

    This is f0 extractor based on dio + stonmask algorithm introduced in `WORLD:
    a vocoder-based high-quality speech synthesis system for real-time applications`_.

    .. _`WORLD: a vocoder-based high-quality speech synthesis system for real-time
        applications`: https://doi.org/10.1587/transinf.2015EDP7457

    Note:
        This module is based on NumPy implementation. Therefore, the computational graph
        is not connected.

    Todo:
        Replace this module with PyTorch-based implementation.

    """

    def __init__(
        self,
        fs: int = 22050,
        n_fft: int = 1024,
        hop_length: int = 256,
        f0min: int = 80,
        f0max: int = 400,
        use_token_averaged_f0: bool = True,
        use_continuous_f0: bool = True,
        use_log_f0: bool = True,
        reduction_factor: int = None,
    ):
        self.fs = fs
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.frame_period = 1000 * hop_length / fs
        self.f0min = f0min
        self.f0max = f0max
        self.use_token_averaged_f0 = use_token_averaged_f0
        self.use_continuous_f0 = use_continuous_f0
        self.use_log_f0 = use_log_f0
        if use_token_averaged_f0:
            assert reduction_factor >= 1
        self.reduction_factor = reduction_factor

    def output_size(self) -> int:
        return 1

    def get_parameters(self) -> Dict[str, Any]:
        return dict(
            fs=self.fs,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            f0min=self.f0min,
            f0max=self.f0max,
            use_token_averaged_f0=self.use_token_averaged_f0,
            use_continuous_f0=self.use_continuous_f0,
            use_log_f0=self.use_log_f0,
            reduction_factor=self.reduction_factor,
        )

    def forward(
        self,
        input: np.ndarray,
        feats_lengths: np.ndarray = None,
        durations: np.ndarray = None,
        durations_lengths: np.ndarray = None,
    ) -> Tuple[np.ndarray, np.ndarray]:

        # F0 extraction
        pitch = self._calculate_f0(input)

        # (Optional): Average by duration to calculate token-wise f0
        if self.use_token_averaged_f0:
            durations = durations * self.reduction_factor
            pitch = [
                self._average_by_duration(p, d).view(-1)
                for p, d in zip(pitch, durations)
            ]
            pitch_lengths = durations_lengths
        else:
            pitch_lengths = np.array(
                [len(pitch)], dtype=np.int32)

        # Return with the shape (B, T, 1)
        return pitch

    def _calculate_f0(self, input: np.ndarray) -> np.ndarray:
        x = input
        f0, timeaxis = pyworld.dio(
            x,
            self.fs,
            f0_floor=self.f0min,
            f0_ceil=self.f0max,
            frame_period=self.frame_period,
        )
        f0 = pyworld.stonemask(x, f0, timeaxis, self.fs)
        if self.use_continuous_f0:
            f0 = self._convert_to_continuous_f0(f0)
        if self.use_log_f0:
            nonzero_idxs = np.where(f0 != 0)[0]
            f0[nonzero_idxs] = np.log(f0[nonzero_idxs])
        return np.array(f0.reshape(-1), dtype=np.float32)

    @staticmethod
    def _adjust_num_frames(x: np.ndarray, num_frames: np.ndarray) -> np.ndarray:
        if num_frames > len(x):
            x = np.pad(x, (0, num_frames - len(x)))
        elif num_frames < len(x):
            x = x[:num_frames]
        return x

    @staticmethod
    def _convert_to_continuous_f0(f0: np.ndarray) -> np.ndarray:
        if (f0 == 0).all():
            logging.warn("All frames seems to be unvoiced.")
            return f0

        # padding start and end of f0 sequence
        start_f0 = f0[f0 != 0][0]
        end_f0 = f0[f0 != 0][-1]
        start_idx = np.where(f0 == start_f0)[0][0]
        end_idx = np.where(f0 == end_f0)[0][-1]
        f0[:start_idx] = start_f0
        f0[end_idx:] = end_f0

        # get non-zero frame index
        nonzero_idxs = np.where(f0 != 0)[0]

        # perform linear interpolation
        interp_fn = interp1d(nonzero_idxs, f0[nonzero_idxs])
        f0 = interp_fn(np.arange(0, f0.shape[0]))

        return f0

    def _average_by_duration(self, x: np.ndarray, d: np.ndarray) -> np.ndarray:
        assert 0 <= len(x) - d.sum() < self.reduction_factor
        d_cumsum = np.pad(d.cumsum(dim=0), (1, 0))
        x_avg = [
            x[start:end].masked_select(x[start:end].gt(0.0)).mean(dim=0)
            if len(x[start:end].masked_select(x[start:end].gt(0.0))) != 0
            else np.array(0.0)
            for start, end in zip(d_cumsum[:-1], d_cumsum[1:])
        ]
        return np.stack(x_avg)


class Harvest:
    """F0 estimation with dio + stonemask algorithm.

    This is f0 extractor based on dio + stonmask algorithm introduced in `WORLD:
    a vocoder-based high-quality speech synthesis system for real-time applications`_.

    .. _`WORLD: a vocoder-based high-quality speech synthesis system for real-time
        applications`: https://doi.org/10.1587/transinf.2015EDP7457

    Note:
        This module is based on NumPy implementation. Therefore, the computational graph
        is not connected.

    Todo:
        Replace this module with PyTorch-based implementation.

    """

    def __init__(
        self,
        fs: int = 22050,
        n_fft: int = 1024,
        hop_length: int = 256,
        f0min: int = 80,
        f0max: int = 400,
        use_token_averaged_f0: bool = True,
        use_continuous_f0: bool = True,
        use_log_f0: bool = True,
        reduction_factor: int = None,
    ):
        self.fs = fs
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.frame_period = 1000 * hop_length / fs
        self.f0min = f0min
        self.f0max = f0max
        self.use_token_averaged_f0 = use_token_averaged_f0
        self.use_continuous_f0 = use_continuous_f0
        self.use_log_f0 = use_log_f0
        if use_token_averaged_f0:
            assert reduction_factor >= 1
        self.reduction_factor = reduction_factor

    def output_size(self) -> int:
        return 1

    def get_parameters(self) -> Dict[str, Any]:
        return dict(
            fs=self.fs,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            f0min=self.f0min,
            f0max=self.f0max,
            use_token_averaged_f0=self.use_token_averaged_f0,
            use_continuous_f0=self.use_continuous_f0,
            use_log_f0=self.use_log_f0,
            reduction_factor=self.reduction_factor,
        )

    def forward(
        self,
        input: np.ndarray,
        durations: np.ndarray = None,
        durations_lengths: np.ndarray = None,
    ) -> Tuple[np.ndarray, np.ndarray]:

        # F0 extraction
        pitch = self._calculate_f0(input)

        # (Optional): Average by duration to calculate token-wise f0
        if self.use_token_averaged_f0:
            durations = durations * self.reduction_factor
            pitch = [
                self._average_by_duration(p, d).view(-1)
                for p, d in zip(pitch, durations)
            ]
            pitch_lengths = durations_lengths
        else:
            pitch_lengths = np.array(
                [len(pitch)], dtype=np.int32)

        # Return with the shape (B, T, 1)
        return pitch

    def _calculate_f0(self, input: np.ndarray) -> np.ndarray:
        x = input
        f0, timeaxis = pyworld.harvest(
            x,
            self.fs,
            f0_floor=self.f0min,
            f0_ceil=self.f0max,
            frame_period=self.frame_period,
        )
        if self.use_continuous_f0:
            f0 = self._convert_to_continuous_f0(f0)
        if self.use_log_f0:
            nonzero_idxs = np.where(f0 != 0)[0]
            f0[nonzero_idxs] = np.log(f0[nonzero_idxs])
        return np.array(f0.reshape(-1), dtype=np.float32)

    @staticmethod
    def _adjust_num_frames(x: np.ndarray, num_frames: np.ndarray) -> np.ndarray:
        if num_frames > len(x):
            x = np.pad(x, (0, num_frames - len(x)))
        elif num_frames < len(x):
            x = x[:num_frames]
        return x

    @staticmethod
    def _convert_to_continuous_f0(f0: np.ndarray) -> np.ndarray:
        if (f0 == 0).all():
            logging.warn("All frames seems to be unvoiced.")
            return f0

        # padding start and end of f0 sequence
        start_f0 = f0[f0 != 0][0]
        end_f0 = f0[f0 != 0][-1]
        start_idx = np.where(f0 == start_f0)[0][0]
        end_idx = np.where(f0 == end_f0)[0][-1]
        f0[:start_idx] = start_f0
        f0[end_idx:] = end_f0

        # get non-zero frame index
        nonzero_idxs = np.where(f0 != 0)[0]

        # perform linear interpolation
        interp_fn = interp1d(nonzero_idxs, f0[nonzero_idxs])
        f0 = interp_fn(np.arange(0, f0.shape[0]))

        return f0

    def _average_by_duration(self, x: np.ndarray, d: np.ndarray) -> np.ndarray:
        assert 0 <= len(x) - d.sum() < self.reduction_factor
        d_cumsum = np.pad(d.cumsum(dim=0), (1, 0))
        x_avg = [
            x[start:end].masked_select(x[start:end].gt(0.0)).mean(dim=0)
            if len(x[start:end].masked_select(x[start:end].gt(0.0))) != 0
            else np.array(0.0)
            for start, end in zip(d_cumsum[:-1], d_cumsum[1:])
        ]
        return np.stack(x_avg)
