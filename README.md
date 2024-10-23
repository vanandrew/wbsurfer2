# wbsurfer2
CLI tool for making CIFTI-related movies

A refactor and refresh of the original [wbsurfer](https://gitlab.com/vanandrew/wbsurfer) tool.
This version aims to support >= Connectome Workbench 2.0.

Very much a work in progress, bugs are expected.

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
usage: wb_surfer2 [-h] -s SCENE_PATH -n SCENE_NAME -o OUTPUT [--width WIDTH]
                  [--height HEIGHT] [-r FRAMERATE] [--closed | --reverse] [-l LOOPS]
                  [--num-cpus NUM_CPUS] [--vertex-mode | --border-file]
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
                        The output file path. Should end in .mp4.
  --width WIDTH         The width of the output movie. By default, 1920 pixels.
  --height HEIGHT       The height of the output movie. By default, 1080 pixels.
  -r FRAMERATE, --framerate FRAMERATE
                        The framerate of the output movie. By default, 10 FPS.
  --closed              If enabled, a closed loop will be generated. This appends the
                        first row index to the end of the row index traversal list.
                        Mutually exclusive with --reverse.
  --reverse             If enabled, a reverse of the traversal list will be appended to
                        the row index traversal list. Mutually exclusive with --closed.
  -l LOOPS, --loops LOOPS
                        How many times to loop the movie. By default, 1 loop.
  --num-cpus NUM_CPUS   The number of CPUs to use for processing.
  --vertex-mode         If enabled, row_indices are treated as vertex indices. The first
                        argument should be the surface that the vertices are on.
                        Mutually exclusive with --border-file (e.g. CORTEX_LEFT 0 1 2
                        3...)
  --border-file         If enabled, the border file will be used to generate the movie.
                        The row_indices argument should be the border file. Mutually
                        exclusive with --vertex-mode.
  ```

`wb_surfer2` requires a scene file to generate the movie. This scene file can be created in Connectome Workbench.

Unlike version 1, `wb_surfer2` can handle multiple scenes being defined in a file (though only one active scene can be
used at a time). The active scene is defined by the `--scene-name` argument.

When making your scene, at least one vertex must be placed on the surface for `wb_surfer2` to control. In the case of
multiple vertices, only the first vertex will be manipulated. 
