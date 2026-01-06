import logging
from pathlib import Path

from pytest import fixture

from wbsurfer.logging import run_process, setup_logging


@fixture(autouse=True)
def reset_logging_for_each_test():
    """Reset logging before each test in this module."""
    # Save pytest handlers
    root_logger = logging.getLogger()
    pytest_handlers = [
        h for h in root_logger.handlers if "pytest" in type(h).__module__
    ]

    # Clear all handlers except pytest's
    for handler in root_logger.handlers[:]:
        if handler not in pytest_handlers:
            handler.close()
            root_logger.removeHandler(handler)

    # Reset level
    root_logger.setLevel(logging.WARNING)

    yield

    # Clean up after test
    for handler in root_logger.handlers[:]:
        if handler not in pytest_handlers:
            handler.close()
            root_logger.removeHandler(handler)


def test_run_process_success():
    """Test running a successful command."""
    result = run_process(["echo", "test"], suppress_output=True)
    assert result == 0


def test_run_process_failure():
    """Test running a failed command."""
    result = run_process(["false"], suppress_output=True)
    assert result != 0


def test_run_process_with_output(caplog):
    """Test that run_process logs output correctly."""
    with caplog.at_level(logging.INFO):
        result = run_process(["echo", "test output"], suppress_output=False)
    assert result == 0
    assert "test output" in caplog.text


def test_run_process_suppress_output(caplog):
    """Test that run_process can suppress output."""
    with caplog.at_level(logging.INFO):
        result = run_process(["echo", "test output"], suppress_output=True)
    assert result == 0
    # Output should not be logged
    assert "test output" not in caplog.text


def test_run_process_with_env():
    """Test running a command with environment variables."""
    result = run_process(
        ["sh", "-c", "echo $TEST_VAR"],
        env={"TEST_VAR": "test_value"},
        suppress_output=True,
    )
    assert result == 0


def test_setup_logging_stdout(capsys):
    """Test setting up logging to stdout."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Test log message")

    # Capture stdout
    captured = capsys.readouterr()
    assert "Test log message" in captured.out


def test_setup_logging_with_file(tmpdir):
    """Test setting up logging with a file handler."""
    log_file = Path(tmpdir) / "test.log"
    setup_logging(log_file=str(log_file))

    # Log a message using root logger
    logging.info("Test file log message")

    # Flush handlers
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Check that log file was created and contains the message
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Test file log message" in log_content


def test_setup_logging_creates_directory(tmpdir):
    """Test that setup_logging creates parent directories if needed."""
    log_file = Path(tmpdir) / "subdir" / "test.log"
    setup_logging(log_file=str(log_file))

    # Check that parent directory was created
    assert log_file.parent.exists()
    assert log_file.exists()


def test_setup_logging_overwrites_existing_file(tmpdir):
    """Test that setup_logging overwrites existing log files."""
    log_file = Path(tmpdir) / "test.log"

    # Create initial log file with content
    log_file.write_text("Old log content\n")

    # Setup logging (should overwrite)
    setup_logging(log_file=str(log_file))
    logging.info("New log message")

    # Flush handlers
    for handler in logging.getLogger().handlers:
        handler.flush()

    # Check that old content is gone
    log_content = log_file.read_text()
    assert "Old log content" not in log_content
    assert "New log message" in log_content
