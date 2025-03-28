import os
import logging as logging_base
from db.db import init, close
from autotests.youtube_download import run_test as youtube_download
from config import logging_config

async def run():
    logging = logging_config.setup_logging(__name__)

    error_count = 0
    warning_count = 0
    passed_count = 0

    class TestLoggingHandler(logging_base.Handler):
        def emit(self, record):
            nonlocal error_count, warning_count, passed_count
            log_message = self.format(record)
            if 'Test passed!' in log_message:
                passed_count += 1
            elif 'Test failed' in log_message or 'An error occurred' in log_message:
                error_count += 1
            elif 'Warning' in log_message:
                warning_count += 1

    test_logging_handler = TestLoggingHandler()
    logging_base.getLogger().addHandler(test_logging_handler)

    try:
        await init()
        logging.info(f'Start tests...')
        await youtube_download()
        await close()
    except Exception as e:
        logging.error(f"An error occurred during test execution: {e}")
    finally:
        logging.info(f'All tests completed! [Errors: {error_count}, Warnings: {warning_count}, Passed: {passed_count}]')
        if error_count > 0:
            os._exit(1)
        else:
            os._exit(0)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
