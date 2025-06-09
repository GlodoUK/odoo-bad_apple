import struct
import io
import glob
import base64
import os
import tempfile
import subprocess
from odoo import models, fields, _, api

from PIL import Image

from odoo.addons.queue_job.delay import group, chain

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
    thumbnail = fields.Image()
    raw = fields.Binary(attachment=True, required=True)
    frames = fields.Binary(attachment=True)
    audio = fields.Binary(attachment=True)
    state = fields.Selection([
        ('draft', 'Pending'),
        ('import', 'Importing'),
        ('ready', 'Ready')
    ], default="draft")

    def action_import(self):
        self.ensure_one()
        group_a = group(
            self.delayable()._import_thumbnail(),
            self.delayable()._import_frames(),
            self.delayable()._import_audio(),
        )
        chain(group_a, self.delayable()._action_ready()).delay()
        self.state = "import"

    def _import_thumbnail(self):
        with tempfile.TemporaryDirectory() as td:
            raw = os.path.join(td, "raw")
            with open(raw, "wb+") as f:
                f.write(base64.b64decode(self.raw))

            thumbnail = os.path.join(td, "thumbnail.png")

            cmd = [
                'ffmpeg',
                '-i',
                raw,
                '-ss',
                "00:00:10.000",
                '-vframes',
                '1',
                "-vf",
                "scale=128:128:force_original_aspect_ratio=decrease,format=rgba,pad=128:128:(ow-iw)/2:(oh-ih)/2:color=0x00000000",
                thumbnail,
            ]

            subprocess.run(cmd, check=True)
            with open(thumbnail, "rb+") as f:
                self.thumbnail = base64.b64encode(f.read())

    def _import_frames(self):
        with tempfile.TemporaryDirectory() as td:
            frames = os.path.join(td, "frames")
            raw = os.path.join(td, "raw")
            with open(raw, "wb+") as f:
                f.write(base64.b64decode(self.raw))
            os.mkdir(frames)
            subprocess.run([
                'ffmpeg',
                '-i',
                raw,
                '-vf',
                f'scale={WIDTH}:{HEIGHT},format=gray',
                '-r', '24',
                os.path.join(frames, 'frame_%04d.pgm'),
            ])

            frames = sorted(glob.glob(os.path.join(frames, "*.pgm")))
            num_frames = len(frames)

            if num_frames < 1:
                raise Exception("Fuck")

            f = io.BytesIO()
            f.write(struct.pack(">HHH", WIDTH, HEIGHT, num_frames))
            for frame_path in frames:
                data = load_frame_bytes(frame_path, WIDTH, HEIGHT)
                f.write(data)

            self.frames = base64.b64encode(f.getvalue())

    def _import_audio(self):
        with tempfile.TemporaryDirectory() as td:
            input = os.path.join(td, "raw")
            output = os.path.join(td, "output.ogg")
            with open(input, "wb+") as f:
                f.write(base64.b64decode(self.raw))
            subprocess.run([
                'ffmpeg',
                '-i',
                input,
                '-c:a',
                'libvorbis',
                '-b:a',
                '128k',
                '-ar',
                '44100',
                '-ac',
                '1',
                output,
            ], check=True)
            with open(output, "rb+") as f:
                self.audio = base64.b64encode(f.read())

    def _action_ready(self):
        self.state = 'ready'

    def action_play(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("bad_odoo.actions_client_bad_odoo")
        action['params'] = {'active_id': self.id}
        return action

    def create_document_from_attachment(self, attachment_ids):
        records = self.env[self._name]

        for attachment in attachment_ids:
            attachment_id = self.env['ir.attachment'].browse(attachment)

            record = self.create({
                'name': attachment_id.name,
            })
            attachment_id.write({
                'res_model': self._name,
                'res_id': record.id,
                'res_field': 'raw',
            })
            records |= record

        for record in records:
            record.with_delay(eta=2).action_import()

        action = self.env["ir.actions.actions"]._for_xml_id("bad_odoo.actions_bad_odoo_tracks_act_window")
        action['domain'] = [('id', 'in', records.ids)]
        return action
