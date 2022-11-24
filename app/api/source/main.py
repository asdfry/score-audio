import shutil
import time
import uuid

from demucs_broker import DemucsBroker
from fastapi import FastAPI, File, Query, UploadFile, status
from fastapi.responses import JSONResponse
from util import ready, input_spice, create_result

app = FastAPI()
demucs = DemucsBroker()


@app.post("/score", status_code=200)
def get_score(use_demucs: bool = Query(False), upload_file: UploadFile = File(...)):
    begin_time = time.time()
    id = str(uuid.uuid4())
    result_audio_path, result_image_path, accom_audio_path, accom_image_path = ready(id)

    with open(result_audio_path, "wb") as buffer:  # 마운트된 볼륨으로 파일 복사
        shutil.copyfileobj(upload_file.file, buffer)

    if use_demucs:  # 음원분리 사용 시
        separate_result = demucs.separate(result_audio_path, result_audio_path, accom_audio_path)
        if not separate_result:  # 음원분리 실패
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "demucs fail"},
            )
        score, duration = input_spice(result_audio_path, result_image_path)  # vocal
        input_spice(accom_audio_path, accom_image_path, accom=True)  # accompaniment
    else:  # 음원분리 미사용 시
        score, duration = input_spice(result_audio_path, result_image_path)

    # 결과 딕셔너리 저장
    dict_result = create_result(id, upload_file.filename, duration, use_demucs, score, begin_time)

    print(dict_result)

    return dict_result
