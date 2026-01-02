import ffmpeg
from pathlib import Path

class VideoConverter:
    @classmethod
    def validate_input(cls, path: str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return p

    @classmethod
    def output_path(cls, input_path: str, fmt: str) -> str:
        return f"{Path(input_path).stem}.{fmt.lower()}"

    @classmethod
    async def convert(cls, input_path: str, format: str, ffmpeg_path: str = "ffmpeg") -> str:
        cls.validate_input(input_path)
        out = cls.output_path(input_path, format)

        stream = ffmpeg.input(input_path)

        if format.lower() == "gif":
            stream = stream.filter("fps", 15).filter("scale", "640:-1").output(out, format="gif", loop=0)
        else:
            stream = stream.output(out, vcodec="libx264", preset="medium", crf=23, acodec="aac")

        # THIS IS THE ONLY LINE THAT WORKS
        await ffmpeg.run_async(stream, cmd=ffmpeg_path, overwrite_output=True, quiet=True)

        output_file = Path(VideoConverter.output_path(input_path, format))
        full_path = output_file.resolve()

        return f"Done! Your {format.lower()} file is ready!\n\nLocation:\n{full_path}"