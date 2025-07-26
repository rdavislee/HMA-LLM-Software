import logging
from backend.src.utils.logger import get_logger

def test_get_logger():
    logger = get_logger('test_logger_instance')
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'test_logger_instance'
    assert logger.level == logging.INFO  # Default from config

def test_logger_is_singleton_for_same_name():
    logger1 = get_logger('singleton_test')
    logger2 = get_logger('singleton_test')
    assert logger1 is logger2
