import os
from glob import glob


class Demucs:
    def __init__(self) -> None:
        pass

    def separate_audio(self, input_path):
        os.system(f"python3 -m demucs.separate --two-stems=vocals '{input_path}'")
        output_files = glob(f"/separated/mdx_extra_q/{input_path}/*")
        if output_files:
            output_path = output_files[0]  # 0 = vocal, 1 = no_vocal
            return output_path
        else:
            return None
