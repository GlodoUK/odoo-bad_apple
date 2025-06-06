# Bad Odoo

- Find mp4 of your choice.
- Using ffmpeg convert all frames to grey-scale pgm into a folder called `frames/`:
  `ffmpeg -i bad-apple.mp4 -vf scale=80:50,format=gray -r 24 frames/frame_%04d.pgm`
- Extract audio into ogg file so that most browsers can handle the audio:
  `ffmpeg -i bad-apple.mp4 -c:a libvorbis -b:a 128k -ar 44100 -ac 1 bad_apple.ogg`
- Run `./scripts/combine-pgm.py` to generate a binpacked version of the pgm files. If a
  pixel in a frame is more than 50% grey then it's "on". Otherwise it's "off". We pack
  these into a single file.
- Plonk files into `static/`
- Adjust `bad_apple.esm.js` if necessary

## TODO

- Make an importer and idea of a track so that anyone can load any old mp4

## Why

The original plan was to use the cohort view, but it was too slow and restricted to the
number of columns and rows.

Other options like Kanban might be abuse-able.
