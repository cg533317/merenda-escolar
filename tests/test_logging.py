import logging
from backend.core.logging import setup_logging, get_logger


def test_setup_logging_creates_logger():
    logger = setup_logging("TestLogger")
    
    assert logger.name == "TestLogger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_get_logger_returns_existing_logger():
    logger1 = get_logger("ExistingLogger")
    logger2 = get_logger("ExistingLogger")
    
    assert logger1 is logger2


def test_get_logger_creates_logger_if_not_exists():
    logger = get_logger("NewLogger")
    
    assert logger.name == "NewLogger"
    assert len(logger.handlers) > 0


def test_logger_levels():
    logger = setup_logging("LevelTest", level=logging.DEBUG)
    
    assert logger.level == logging.DEBUG


if __name__ == "__main__":
    test_setup_logging_creates_logger()
    test_get_logger_returns_existing_logger()
    test_get_logger_creates_logger_if_not_exists()
    test_logger_levels()
    print("Logging tests passed")