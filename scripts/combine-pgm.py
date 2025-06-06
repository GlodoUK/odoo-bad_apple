#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pillow",
# ]
# ///


# bin output file format
# [Header]
# - uint16 width
# - uint16 height
# - uint16 num_frames
#
# [Frame data]
# - Each frame = height × ceil(width / 8) bytes
# - Frame data is frame after frame (no separators)

import struct
from pathlib import Path

from PIL import Image

FRAME_DIR = Path("frames/")
OUTPUT_FILE = "bad_apple.bin"
THRESHOLD = 128


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


def main():
    width, height = 80, 50
    frames = sorted(FRAME_DIR.glob("*.pgm"))
    num_frames = len(frames)

    with open(OUTPUT_FILE, "wb") as f:
        f.write(struct.pack(">HHH", width, height, num_frames))
        for frame_path in frames:
            data = load_frame_bytes(frame_path, width, height)
            f.write(data)

    print(f"Written {num_frames} frames to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
