import {Component, onMounted, onWillUnmount, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {standardActionServiceProps} from "@web/webclient/actions/action_service";

function loadBinaryFrames(arrayBuffer) {
  const view = new DataView(arrayBuffer);
  const width = view.getUint16(0);
  const height = view.getUint16(2);
  const frameCount = view.getUint16(4);

  const frameSize = height * Math.ceil(width / 8);
  const frames = [];

  for (let i = 0; i < frameCount; i++) {
    const offset = 6 + i * frameSize;
    const frameBytes = new Uint8Array(arrayBuffer, offset, frameSize);
    const frame = [];

    for (let y = 0; y < height; y++) {
      const row = [];
      for (let xByte = 0; xByte < Math.ceil(width / 8); xByte++) {
        const byte = frameBytes[y * Math.ceil(width / 8) + xByte];
        for (let bit = 7; bit >= 0; bit--) {
          const pixel = (byte >> bit) & 1;
          if (row.length < width) row.push(pixel);
        }
      }
      frame.push(row);
    }

    frames.push(frame);
  }

  return {width, height, frames};
}

export class BadOdoo extends Component {
  static template = "BadOdoo.Template";
  static props = {...standardActionServiceProps};

  setup() {
    this.state = useState({
      frameIndex: -1,
      frames: [],
      frame: undefined,
      playing: false,
      duration: 0,
      width: 0,
      height: 0,
      loaded: false,
    });
    this.audio = undefined;

    onMounted(async () => {
      await fetch("/bad_odoo/static/bad_apple.bin")
        .then((res) => {
          return res.arrayBuffer();
        })
        .then(loadBinaryFrames)
        .then(({width, height, frames}) => {
          this.state = Object.assign(
            this.state,
            {},
            {frames, frameIndex: 0, width, height}
          );
        })
        .then(() => {
          this.audio = new Audio("/bad_odoo/static/bad_apple.ogg");
          this.audio.addEventListener("loadedmetadata", () => {
            this.state.duration = this.audio.duration;
            this.state.loaded = true;
          });
        });
    });

    onWillUnmount(this.onWillUnmount);
  }

  onWillUnmount() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }

    this.state.playing = false;
  }

  play() {
    this.audio.play();
    this.state.playing = true;

    requestAnimationFrame(() => {
      this.animation();
    });
  }

  pause() {
    if (this.state.playing) {
      this.state.playing = false;

      if (this.audio) {
        this.audio.pause();
      }

      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
      }
    }
  }

  onScrubberInput() {
    this.pause();
  }

  onScrubberChange(ev) {
    const time = parseFloat(ev.target.value);
    this.audio.currentTime = time;
    this.play();
  }

  animation() {
    // Use audio currentTime for accurate sync
    if (this.audio) {
      const currentTimeMs = this.audio.currentTime * 1000;
      // 24 fps
      const currentFrameIndex = Math.floor(currentTimeMs / (1000 / 24));

      if (currentFrameIndex <= this.state.frames.length) {
        this.state.frameIndex = currentFrameIndex;
        requestAnimationFrame(() => {
          this.animation();
        });
      } else {
        // End playback gracefully
        this.pause();
        return;
      }
    }
  }
}

registry.category("actions").add("bad_odoo", BadOdoo);
