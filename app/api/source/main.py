import json
import logging
import os
import shutil
import time
import uuid
from datetime import datetime

from demucs_broker import DemucsBroker
from fastapi import FastAPI, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from scipy.io import wavfile
from spice import Spice
from util import ready

app = FastAPI()
spice = Spice()
demucs = DemucsBroker()


def input_spice(audio_path, image_path, accom=False):
    cvt_audio = spice.convert_audio(audio_path)  # 오디오 변환 (프레임레이트: 16000, 채널: 1, 형식: wav)
    sample_rate, audio_samples = wavfile.read(cvt_audio, "rb")
    if accom:
        spice.save_spectrogram(audio_samples, image_path)  # 스펙트로그램 이미지 저장
    else:
        duration = spice.get_duration(sample_rate, audio_samples)  # 오디오 길이 추출
        score = spice.get_confidence_score(audio_samples, image_path)
        return score, duration


@app.post("/compute", status_code=200)
def compute(use_demucs: bool = Query(False), upload_file: UploadFile = File(...)):
    begin_time = time.time()
    id = str(uuid.uuid4())
    result_audio_path, result_image_path, accom_audio_path, accom_image_path = ready(id)

    if use_demucs:  # 음원분리 사용 시
        with open("input_audio", "wb") as f:  # 파일 복사
            shutil.copyfileobj(upload_file.file, f)
        separate_result = demucs.separate("input_audio", result_audio_path, accom_audio_path)  # 음원 분리
        if separate_result:
            score, duration = input_spice(result_audio_path, result_image_path)  # vocal
            input_spice(accom_audio_path, accom_image_path, accom=True)  # accompaniment
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "demucs fail"},
            )
    else:
        with open(result_audio_path, "wb") as buffer:  # 마운트된 볼륨으로 파일 복사
            shutil.copyfileobj(upload_file.file, buffer)
        score, duration = input_spice(result_audio_path, result_image_path)

    with open(os.path.join(os.environ.get("STORAGE_DIR"), id, "result.json"), "w") as f:
        dict_result = {
            "id": id,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "audio": {"filename": upload_file.filename, "duration": duration},
            "use_demucs": use_demucs,
            "score": score,
            "elapsed": round(time.time() - begin_time, 3),
        }
        json.dump(dict_result, f, indent=4)

    print(dict_result)

    return dict_result
 