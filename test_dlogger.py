import logging
import dlogger

stylesheet = {
    "default": [],
    "critical": [1, 31],  # bold red
    "error": [31],  # red
    "warning": [33],  # yellow
    "info": [],  # default
    "debug": [2],  # faint
    "argument": [34],  # blue
    "ignored_tb": [2],  # faint
    "tb_path": [34],  # blue
    "tb_lineno": [34],  # blue
    "tb_exc_name": [31],  # red
}

def setup_logging():
    logger = logging.getLogger("test_dlogger")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setFormatter(dlogger.DifferentFormatter())
    logger.addHandler(handler)

    return logger


def main():
    logger = setup_logging()

    levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]
    for i in levels:
        logger.log(getattr(logging, i), "This is a %s message.", i)

    for i in levels:
        try:
            raise RuntimeError("This is a description of the exception.")
        except RuntimeError:
            logger.log(getattr(logging, i), "This is a %s exception message", i, exc_info=True)

    logger.fatal("Goodbye!")


if __name__ == "__main__":
    main()
