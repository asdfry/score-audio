import json
import os
import time

from datetime import datetime
from scipy.io import wavfile
from spice import Spice

spice = Spice()


def input_spice(audio_path, image_path, accom=False):
    cvt_audio = spice.convert_audio(audio_path)  # 오디오 변환 (프레임레이트: 16000, 채널: 1, 형식: wav)
    sample_rate, audio_samples = wavfile.read(cvt_audio, "rb")
    if accom:
        spice.save_spectrogram(audio_samples, image_path)  # 스펙트로그램 이미지 저장
    else:
        duration = spice.get_duration(sample_rate, audio_samples)  # 오디오 길이 추출
        score = spice.get_confidence_score(audio_samples, image_path)
        return score, duration


def ready(id):
    os.mkdir(os.path.join(os.environ.get("STORAGE_DIR"), id))
    result_audio_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav")
    result_image_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png")
    accom_audio_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.wav")
    accom_image_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.png")
    return result_audio_path, result_image_path, accom_audio_path, accom_image_path


def create_result(id, filename, duration, use_demucs, score, begin_time):
    with open(os.path.join(os.environ.get("STORAGE_DIR"), id, "result.json"), "w") as f:
        dict_result = {
            "id": id,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio": {"filename": filename, "duration": duration},
            "use_demucs": use_demucs,
            "score": score,
            "elapsed": round(time.time() - begin_time, 3),
        }
        json.dump(dict_result, f, indent=4)

    return dict_result
