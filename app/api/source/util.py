import os


def ready(id):
    os.mkdir(os.path.join(os.environ.get("STORAGE_DIR"), id))
    result_audio_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "result.wav")
    result_image_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "result.png")
    accom_audio_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.wav")
    accom_image_path = os.path.join(os.environ.get("STORAGE_DIR"), id, "accom.png")
    return result_audio_path, result_image_path, accom_audio_path, accom_image_path
