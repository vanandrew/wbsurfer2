# wbsurfer2
CLI tool for making CIFTI-related movies

https://github.com/user-attachments/assets/e40315fb-f528-4cc7-ae91-8827bfef242c

This is a refactor and refresh of the original [wbsurfer](https://gitlab.com/vanandrew/wbsurfer) tool.
This version aims to support >= Connectome Workbench 2.0.

## Setup

There are two ways to use `wbsurfer2`. The first and recommended way is to
download compiled binaries from the [releases page](https://github.com/vanandrew/wbsurfer2/releases).
Simply download the version meant for your OS and extract it.

If you are more comfortable with Python, you can also install `wbsurfer2` from `pip`.

```bash
# install wbsurfer2 from PyPI
pip install wbsurfer2

# or if you want to install it for development
git clone git@github.com:vanandrew/wbsurfer2.git
cd wbsurfer2
pip install -e .
```

You will also need `ffmpeg` and `wb_command` installed on your system and on your `PATH`.

`wb_command` is part of the Connectome Workbench suite, which can be downloaded
[here](https://www.humanconnectome.org/software/get-connectome-workbench). The `bin` directory
contains the `wb_command` binary and should be added to your `PATH`.

> [!TIP]
> On macOS, the `wb_command` binary is located in the `Contents/usr/bin` directory of the
> Connectome Workbench installation. This is usually `/Applications/wb_view.app/Contents/usr/bin`.

```bash
# If you installed workbench in /opt/workbench
export PATH=$PATH:/opt/workbench/bin

# on macOS
export PATH=$PATH:/Applications/wb_view.app/Contents/usr/bin
```

`ffmpeg` can be downloaded in many ways, but I recommend using a package manager like `apt` or
 [`brew`](https://brew.sh/):

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Usage

> [!IMPORTANT]  
> `ffmpeg` and `wb_command` must be installed and on your `PATH` for `wbsurfer2` to work.
> Alternatively, you can specify the path to both programs using the `FFMPEG_BINARY_PATH` and `WBCOMMAND_BINARY_PATH`
> environment variables, if for some reason you are unable to add them to your `PATH`.
>
> `export FFMPEG_BINARY_PATH=/path/to/ffmpeg`
>
> `export WBCOMMAND_BINARY_PATH=/path/to/wb_command`

> [!TIP]
> If you are encountering an error with the scene rendering step, set `EXTERNAL_COMMAND_LOG=1` in your
> environment for more verbose details on what is happening to the `wb_command`.

Once it's installed, you can run the `wb_surfer2` command. The following is the help message:

```bash
usage: wb_surfer2 [-h] [-v] -s SCENE_PATH -n SCENE_NAME -o OUTPUT [--width WIDTH] [--height HEIGHT]
                  [-r FRAMERATE] [--closed | --reverse] [-l LOOPS] [--num-cpus NUM_CPUS]
                  [--vertex-mode | --border-file]
                  row_indices [row_indices ...]

Generate a movie from a list of row indices.

positional arguments:
  row_indices           The list of row indices to generate the movie from.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
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
  --closed              If enabled, a closed loop will be generated. This appends the first row index to
                        the end of the row index traversal list. Mutually exclusive with --reverse.
  --reverse             If enabled, a reverse of the traversal list will be appended to the row index
                        traversal list. Mutually exclusive with --closed.
  -l LOOPS, --loops LOOPS
                        How many times to loop the movie. By default, 1 loop.
  --num-cpus NUM_CPUS   The number of CPUs to use for processing.
  --vertex-mode         If enabled, row_indices are treated as vertex indices. The first argument should
                        be the surface that the vertices are on. Mutually exclusive with --border-file
                        (e.g. CORTEX_LEFT 0 1 2 3...)
  --border-file         If enabled, the border file will be used to generate the movie. The row_indices
                        argument should be the border file. Mutually exclusive with --vertex-mode.
  ```

> [!TIP]
> Row indices passed into `wb_surfer2` are 0-indexed. This means that the first row is row 0,
> the second row is row 1, and so on. This is -1 from the row indices given in the UI of Connectome Workbench.

`wb_surfer2` requires a scene file to generate the movie. This scene file can be created in Connectome Workbench's
`wb_view` tool.

Unlike in version 1 of `wb_surfer`, `wb_surfer2` can handle multiple scenes being defined in a file (though only one
active scene can be used at a time). The active scene is set by using the `--scene-name` argument.

When making your scene, at least one vertex must be placed on the surface for `wb_surfer2` to control. In the case of
multiple vertices, the first vertex that was placed will be manipulated.

> [!IMPORTANT]  
> Make sure you place the active vertex on the surface you want to manipulate. Placing the active vertex on the wrong
> surface will result in inaccurate movies.
>
> In practice, it's a good idea to have scenes called "left" and "right" so you can switch between hemispheres easily.
