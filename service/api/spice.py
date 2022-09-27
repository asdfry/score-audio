import os

import librosa
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from librosa import display as librosadisplay
from pydub import AudioSegment

tf.get_logger().setLevel("ERROR")

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class Spice:
    def __init__(self) -> None:
        self.EXPECTED_SAMPLE_RATE = 16000
        self.MAX_ABS_INT16 = 32768.0
        self.MAX_ABS_INT24 = 8388608.0
        self.model = hub.load("https://tfhub.dev/google/spice/2")

    def convert_audio_for_model(self, input_path):
        output_path = "converted_audio_file.wav"
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(self.EXPECTED_SAMPLE_RATE).set_channels(1)
        audio.export(output_path, format="wav")
        return os.path.abspath(output_path)

    def plot_stft(self, x, sample_rate, show_black_and_white=False):
        x_stft = np.abs(librosa.stft(x, n_fft=2048))
        fig, ax = plt.subplots()
        fig.set_size_inches(20, 10)
        x_stft_db = librosa.amplitude_to_db(x_stft, ref=np.max)
        if show_black_and_white:
            librosadisplay.specshow(data=x_stft_db, y_axis="log", sr=sample_rate, cmap="gray_r")
        else:
            librosadisplay.specshow(data=x_stft_db, y_axis="log", sr=sample_rate)
        plt.colorbar(format="%+2.0f dB")

    def output2hz(self, pitch_output):
        PT_OFFSET = 25.58
        PT_SLOPE = 63.07
        FMIN = 10.0
        BINS_PER_OCTAVE = 12.0
        cqt_bin = pitch_output * PT_SLOPE + PT_OFFSET
        return FMIN * 2.0 ** (1.0 * cqt_bin / BINS_PER_OCTAVE)

    def get_information(self, sample_rate, audio_samples):
        duration = len(audio_samples) / sample_rate
        return sample_rate, duration

    def get_confidence_score(self, audio_samples):

        # 점수 계산
        audio_samples = audio_samples / self.MAX_ABS_INT16  # 부동 소수점(-1~1)으로 정규화
        model_output = self.model.signatures["serving_default"](tf.constant(audio_samples, tf.float32))
        uncertainty_outputs = model_output["uncertainty"]
        confidence_outputs = 1.0 - uncertainty_outputs
        # score = sum([i for i in confidence_outputs]) / len(confidence_outputs)
        # score = len([i for i in confidence_outputs if i >= 0.5]) / len(confidence_outputs)
        confidence_outputs_ = [i for i in confidence_outputs if i >= 0.2]
        score = sum(confidence_outputs_) / len(confidence_outputs_)

        # 이미지 저장
        pitch_outputs = model_output["pitch"]
        indices = range(len(pitch_outputs))
        confident_pitch_outputs = [(i, p) for i, p, c in zip(indices, pitch_outputs, confidence_outputs) if c >= 0.9]
        confident_pitch_outputs_x, confident_pitch_outputs_y = zip(*confident_pitch_outputs)

        confident_pitch_values_hz = [self.output2hz(p) for p in confident_pitch_outputs_y]
        self.plot_stft(audio_samples / self.MAX_ABS_INT16, sample_rate=self.EXPECTED_SAMPLE_RATE)
        plt.scatter(confident_pitch_outputs_x, confident_pitch_values_hz, c="cyan")
        plt.savefig("image/result.png")

        return float(score)
