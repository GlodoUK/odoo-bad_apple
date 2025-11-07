import base64
import glob
import io
import os
import struct
import subprocess
import tempfile

from PIL import Image

from odoo import fields, models

THRESHOLD = 128

# XXX: If this changes, make sure you also update the aspect ratio in
# static/scss/bad_odoo.scss
WIDTH = 128
HEIGHT = 80


def load_frame_bytes(image_path, width, height):
    img = Image.open(image_path).convert("L").resize((width, height))
    bits = [
        1 if img.getpixel((x, y)) >= THRESHOLD else 0
        for y in range(height)
        for x in range(width)
    ]
    # Pack into bytes
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i : i + 8]:
            byte = (byte << 1) | b
        if len(bits[i : i + 8]) < 8:
            byte <<= 8 - len(bits[i : i + 8])
        data.append(byte)
    return data


def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:02}:{mins:02}:{secs:06.3f}"


class Track(models.Model):
    _name = "bad_odoo.track"
    _description = "Bad Odoo Track"

    name = fields.Char(required=True)
    thumbnail = fields.Image(max_width=128, max_height=128)
    frames = fields.Binary(attachment=True)
    audio = fields.Binary(attachment=True)

    def _import_thumbnail(self, input_path):
        self.ensure_one()
        with tempfile.TemporaryDirectory() as td:
            thumbnail = os.path.join(td, "thumbnail.png")

            cmd = [
                "ffmpeg",
                "-i",
                input_path,
                "-ss",
                "00:00:1.000",
                "-vframes",
                "1",
                "-vf",
                "scale=128:128:force_original_aspect_ratio=decrease,format=rgba,pad=128:128:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
                thumbnail,
            ]

            subprocess.run(cmd, check=True)
            with open(thumbnail, "rb+") as f:
                self.thumbnail = base64.b64encode(f.read())

    def _import_frames(self, input_path):
        self.ensure_one()
        with tempfile.TemporaryDirectory() as td:
            frames = os.path.join(td, "frames")
            os.mkdir(frames)
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-vf",
                    f"scale={WIDTH}:{HEIGHT},format=gray",
                    "-r",
                    "24",
                    os.path.join(frames, "frame_%04d.pgm"),
                ]
            )

            frames = sorted(glob.glob(os.path.join(frames, "*.pgm")))
            num_frames = len(frames)

            if num_frames < 1:
                raise Exception("Something went wrong with ffmpeg. Check logs. Cry.")

            f = io.BytesIO()
            f.write(struct.pack(">HHH", WIDTH, HEIGHT, num_frames))
            for frame_path in frames:
                data = load_frame_bytes(frame_path, WIDTH, HEIGHT)
                f.write(data)

            self.frames = base64.b64encode(f.getvalue())

    def _import_audio(self, input_path):
        self.ensure_one()
        with tempfile.TemporaryDirectory() as td:
            output_path = os.path.join(td, "output.ogg")
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-c:a",
                    "libvorbis",
                    "-q:v",
                    "7",
                    output_path,
                ],
                check=True,
            )
            with open(output_path, "rb+") as f:
                self.audio = base64.b64encode(f.read())

    def action_play(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "bad_odoo.actions_client_bad_odoo"
        )
        action["params"] = {"active_id": self.id}
        return action

    def create_document_from_attachment(self, attachment_ids):
        records = self.env[self._name]

        for attachment in attachment_ids:
            attachment_id = self.env["ir.attachment"].browse(attachment)
            input_path = attachment_id._full_path(attachment_id.store_fname)

            record = self.create(
                {
                    "name": attachment_id.name,
                }
            )
            record._import_thumbnail(input_path)
            record._import_audio(input_path)
            record._import_frames(input_path)

            records |= record

            attachment_id.unlink()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "bad_odoo.actions_bad_odoo_tracks_act_window"
        )
        action["domain"] = [("id", "in", records.ids)]
        return action
