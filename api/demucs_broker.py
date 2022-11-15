import argparse
import torch as th

from demucs.separate import load_track
from demucs.pretrained import get_model_from_args, ModelLoadingError
from demucs.apply import apply_model, BagOfModels
from demucs.audio import save_audio


class DemucsBroker:
    def __init__(self):
        th.hub.set_dir("/hub")
        self.args = argparse.Namespace(
            name="mdx_extra_q",
            repo=None,
            device=f"cuda:0",
            segment=None,
            stem="vocals",
            int24=True,
            float32=True,
            clip_mode="rescale",
            mp3_bitrate=320,
        )

        try:
            self.model = get_model_from_args(self.args)
        except ModelLoadingError as error:
            msg = "failed to load model to device: err = {}".format(error)
            raise Exception(msg)

        if isinstance(self.model, BagOfModels):
            if self.args.segment is not None:
                for sub in self.model.models:
                    sub.segment = self.args.segment
        else:
            if self.args.segment is not None:
                self.model.segment = self.args.segment

        self.model.to(self.args.device)
        self.model.eval()

    def separate(self, source_path, vocal_path, accom_path):
        # load source
        try:
            wav = load_track(source_path, self.model.audio_channels, self.model.samplerate)
        except Exception:
            return False

        # separate
        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()

        try:
            sources = apply_model(self.model, wav[None], device=self.args.device)[0]
        except Exception:
            return False

        sources = sources * ref.std() + ref.mean()
        sources = list(sources)

        kwargs = {
            "samplerate": self.model.samplerate,
            "bitrate": self.args.mp3_bitrate,
            "clip": self.args.clip_mode,
            "as_float": self.args.float32,
            "bits_per_sample": 24 if self.args.int24 else 16,
        }

        # save vocal
        vocal_stem = sources.pop(self.model.sources.index(self.args.stem))
        try:
            save_audio(vocal_stem, vocal_path, **kwargs)
        except Exception:
            return False
        
        # save accompaniment
        other_stem = th.zeros_like(sources[0])
        for i in sources:
            other_stem += i
        try:
            save_audio(other_stem, accom_path, **kwargs)
        except Exception:
            return False

        return True
