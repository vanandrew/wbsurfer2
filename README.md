# wbsurfer2
CLI tool for making CIFTI-related movies

A refactor and refresh of the original [wbsurfer](https://gitlab.com/vanandrew/wbsurfer) tool.
This version aims to support >= Connectome Workbench 2.0.

Very much a work in progress, features are minimal and bugs are expected.

## Installation

To install, clone this repo and pip install it:
```bash
git clone https://github.com/vanandrew/wbsurfer2.git
cd wbsurfer2
pip install .
```

You will also need `ffmpeg` and `wb_command` installed on your system and on your `PATH`.
`wb_command` is part of the Connectome Workbench suite, which can be downloaded
[here](https://www.humanconnectome.org/software/get-connectome-workbench). `ffmpeg` can be downloaded in many ways,
but I recommend using a package manager like `apt` or `brew`.

## Usage

> [!TIP]
> Row indices passed into `wb_surfer2` are 0-indexed. This means that the first row is row 0,
> the second row is row 1, and so on. This is -1 from the row indices given in the UI of Connectome Workbench.

Once it's installed, you can run the `wb_surfer2` command. The following is the help message:

```bash
usage: wb_surfer2 [-h] -s SCENE_PATH -n SCENE_NAME -o OUTPUT [--width WIDTH] [--height HEIGHT] [-r FRAMERATE] [--num-cpus NUM_CPUS]
                  row_indices [row_indices ...]

Generate a movie from a list of row indices.

positional arguments:
  row_indices           The list of row indices to generate the movie from.

options:
  -h, --help            show this help message and exit
  -s SCENE_PATH, --scene-path SCENE_PATH
                        The scene file to use.
  -n SCENE_NAME, --scene-name SCENE_NAME
                        The name of the scene in the scene file.
  -o OUTPUT, --output OUTPUT
                        The output file path.
  --width WIDTH         The width of the output movie.
  --height HEIGHT       The height of the output movie.
  -r FRAMERATE, --framerate FRAMERATE
                        The framerate of the output movie.
  --num-cpus NUM_CPUS   The number of CPUs to use for processing.
  ```
