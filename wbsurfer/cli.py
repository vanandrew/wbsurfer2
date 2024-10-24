from argparse import ArgumentParser
from multiprocessing import freeze_support

from ._version import __version__
from .logging import setup_logging
from .movie import generate_movie

# needed for pyinstaller
freeze_support()


def main():
    """Main function for wbsurfer CLI."""

    # create the argument parser
    parser = ArgumentParser(description="Generate a movie from a list of row indices.")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-s", "--scene-path", required=True, type=str, help="The scene file to use.")
    parser.add_argument("-n", "--scene-name", required=True, type=str, help="The name of the scene in the scene file.")
    parser.add_argument("-o", "--output", required=True, type=str, help="The output file path. Should end in .mp4.")
    parser.add_argument(
        "--width", type=int, default=1920, help="The width of the output movie. By default, 1920 pixels."
    )
    parser.add_argument(
        "--height", type=int, default=1080, help="The height of the output movie. By default, 1080 pixels."
    )
    parser.add_argument(
        "-r", "--framerate", type=int, default=10, help="The framerate of the output movie. By default, 10 FPS."
    )
    path_mods = parser.add_mutually_exclusive_group()
    path_mods.add_argument(
        "--closed",
        action="store_true",
        help="If enabled, a closed loop will be generated. This appends the first row index to the end of the row index"
        " traversal list. Mutually exclusive with --reverse.",
    )
    path_mods.add_argument(
        "--reverse",
        action="store_true",
        help="If enabled, a reverse of the traversal list will be appended to the row index traversal list. Mutually "
        "exclusive with --closed.",
    )
    parser.add_argument(
        "-l", "--loops", type=int, default=1, help="How many times to loop the movie. By default, 1 loop."
    )
    parser.add_argument("--num-cpus", type=int, default=1, help="The number of CPUs to use for processing.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--vertex-mode",
        action="store_true",
        help="If enabled, row_indices are treated as vertex indices. The first argument should be the surface that the "
        "vertices are on. Mutually exclusive with --border-file (e.g. CORTEX_LEFT 0 1 2 3...)",
    )
    mode.add_argument(
        "--border-file",
        action="store_true",
        help="If enabled, the border file will be used to generate the movie. The row_indices argument should be the "
        "border file. Mutually exclusive with --vertex-mode.",
    )
    parser.add_argument("row_indices", nargs="+", help="The list of row indices to generate the movie from.")
    args = parser.parse_args()

    # check that at least 2 row indices are provided
    if len(args.row_indices) < 2 and not args.border_file:
        parser.error("At least 2 row indices are required.")
    elif args.border_file and len(args.row_indices) < 1:
        parser.error("Border file must be specified.")

    # setup logging
    setup_logging()

    # generate the movie
    generate_movie(**vars(args))


if __name__ == "__main__":
    main()
