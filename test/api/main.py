# import logging
import shutil
import time

from fastapi import FastAPI, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from scipy.io import wavfile

from hybrid_demucs import Demucs
from spice import Spice

# logging.getLogger("uvicorn").handlers.clear()

app = FastAPI()
spice = Spice()
demucs = Demucs()

@app.get("/compute", status_code=200)
def compute(use_demucs: bool = Query(False), use_gpu: bool = Query(False), upload_file: UploadFile = File(...)):
    begin_time = time.time()

    if use_demucs:  # 음원분리 사용 시
        with open("input_audio", "wb") as f:  # 오디오 파일 복사
            shutil.copyfileobj(upload_file.file, f)
        print("Start separate audio")
        audio_path = demucs.separate_audio("input_audio", use_gpu)  # 음원 분리
        if not audio_path:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": 500, "message": "demucs fail"}
            )
        audio_path = spice.convert_audio_for_model(audio_path)  # spice에 넣기 위해 준비 (프레임레이트: 16000, 채널: 1, 형식: wav)
    else:
        audio_path = spice.convert_audio_for_model(upload_file.file)  # spice에 넣기 위해 준비 (프레임레이트: 16000, 채널: 1, 형식: wav)

    sample_rate, audio_samples = wavfile.read(audio_path, "rb")
    
    audio_inform = spice.get_information(sample_rate, audio_samples)
    score = spice.get_confidence_score(audio_samples)

    dict_result = {"filename": upload_file.filename, "use_demucs": use_demucs}
    dict_result["audio_information"] = {"sample_rate": audio_inform[0], "duration": audio_inform[1]}
    dict_result["score"] = score
    dict_result["elapsed"] = time.time() - begin_time
    print(dict_result)

    return dict_result
