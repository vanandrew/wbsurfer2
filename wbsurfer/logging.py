import logging
import sys
from pathlib import Path
from subprocess import DEVNULL, PIPE, STDOUT, Popen

logger = logging.getLogger(__name__)


def run_process(cmd: list[str], env: dict[str, str] | None = None, suppress_output: bool = False) -> int:
    """Run a shell command and capture stdout and stderr as it runs, logging in real-time.

    Parameters
    ----------
    cmd : list[str]
        Command and arguments as a list (e.g., ['ls', '-l']).
    env : dict[str, str], optional
        Environment variables to set for the process.
    suppress_output : bool, optional
        Suppress output from the process, by default False

    Returns
    -------
    int
        Return code of the process.
    """
    # Start the process
    with Popen(
        cmd,
        stdout=PIPE if not suppress_output else DEVNULL,
        stderr=STDOUT,
        bufsize=1,
        universal_newlines=True,
        env=env,
    ) as process:
        if not suppress_output:
            # Log stdout and stderr in real time
            if process.stdout is None:
                raise ValueError("Failed to open stdout")
            for stdout_line in process.stdout:
                logger.info(stdout_line.strip())  # Log stdout as it's produced

        # Wait for process to complete
        return_code = process.wait()

    # Return the return code
    return return_code


def setup_logging(log_file: str | None = None) -> None:
    """Sets up logging output.

    Parameters
    ----------
    log_file: str | None
        Setup path to log file.
    """
    # create handlers list
    handlers = []

    # create file write handler if log file specified
    if log_file:
        # get log file path
        log_file_path = Path(log_file).resolve()

        # create path to log if needed
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # append to handlers
        handlers.append(logging.FileHandler(str(log_file_path), mode="w"))  # will overwrite logs if they exist at path

    # add stdout streaming to handlers
    handlers.append(logging.StreamHandler(sys.stdout))

    # setup log output config
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", handlers=handlers)
