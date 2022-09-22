import os
from glob import glob


class Demucs:
    def __init__(self) -> None:
        pass

    def separate_audio(self, input_path, use_gpu):
        if use_gpu:
            os.environ["CUDA_VISIBLE_DEVICES"] = "3"
            os.system(f"cd demucs && python3.8 -m demucs.separate --two-stems=vocals '../{input_path}'")
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        else:
            os.system(f"cd demucs && python3.8 -m demucs.separate --two-stems=vocals -d cpu '../{input_path}'")
        output_files = glob(f"/demucs/separated/mdx_extra_q/{input_path}/*")
        if output_files:
            output_path = output_files[0]  # 0 = vocal, 1 = no_vocal
            return output_path
        else:
            return None
