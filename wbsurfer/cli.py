from argparse import ArgumentParser

from wbsurfer.logging import setup_logging
from wbsurfer.movie import generate_movie


def main():
    """Main function for wbsurfer CLI."""

    # create the argument parser
    parser = ArgumentParser(description="Generate a movie from a list of row indices.")
    parser.add_argument("-s", "--scene-path", required=True, type=str, help="The scene file to use.")
    parser.add_argument("-n", "--scene-name", required=True, type=str, help="The name of the scene in the scene file.")
    parser.add_argument("-o", "--output", required=True, type=str, help="The output file path.")
    parser.add_argument("--width", type=int, default=1920, help="The width of the output movie.")
    parser.add_argument("--height", type=int, default=1080, help="The height of the output movie.")
    parser.add_argument("--num-cpus", type=int, default=1, help="The number of CPUs to use for processing.")
    parser.add_argument("row_indices", type=int, nargs="+", help="The list of row indices to generate the movie from.")
    args = parser.parse_args()

    # check that at least 2 row indices are provided
    if len(args.row_indices) < 2:
        parser.error("At least 2 row indices are required.")

    # setup logging
    setup_logging()

    # generate the movie
    generate_movie(
        args.row_indices, args.scene_path, args.scene_name, args.output, args.width, args.height, args.num_cpus
    )


if __name__ == "__main__":
    main()
