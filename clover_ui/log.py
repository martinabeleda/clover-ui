import logging
import logging.config
from typing import Dict, List


def configure_parent_logger(
    name: str = "clover",
    level: int = logging.DEBUG,
    root_level: int = logging.WARNING,
    format_string: str = None,
    fname: str = None,
    header: str = None,
    blacklist: Dict[int, List[str]] = None,
) -> logging.Logger:
    """Add a stream handler to of the given name and level to the logging module.

    Configure a named logger which outputs to `sys.stdout` and
    optionally to a file if `fname` is given. The user may also
    specify the level of the named logger and configure the
    level of the root logger. If `blacklist` is specified, each
    of the modules in the values list will be assigned the level
    of the key.

    Args:
        name: Name of the logger. Defaults to "clover".
        level: Logging level of the named logger.
            Defaults to logging.DEBUG.
        root_level: Logging level for the root logger.
            Defaults to logging.WARNING.
        format_string: Log message format. Defaults to
            None.
        fname: Output file name. Defaults to None.
        header: Header to prepend to each log.
            Defaults to None.
        blacklist: a Dict[logging.LEVEL, List[str]].
            For each named logger in the list, set to
            the specified level. Defaults to None.

    Returns:
        `logging.Logger`: The named logger

    Examples:
        >>> import logging
        >>> from clover_ui.log import configure_parent_logger

        >>> logger = configure_parent_logger(fname="/tmp/example.log", level=logging.INFO)
    """

    if format_string is None:
        format_string = "%(asctime)s - [%(levelname)s] - %(name)s - %(filename)s:%(funcName)s:%(lineno)d"
        if header is not None:
            format_string += f" | {header}"
        format_string += " | %(message)s\n"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "basic": {"class": "logging.Formatter", "format": format_string,},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.getLevelName(level),
                "formatter": "basic",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            name: {
                "handlers": ["console"],
                "level": logging.getLevelName(level),
                "propagate": False,
            },
        },
        "root": {"handlers": ["console"], "level": logging.getLevelName(root_level),},
    }
    if fname is not None:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": logging.getLevelName(level),
            "formatter": "basic",
            "filename": fname,
            "mode": "a",
            "encoding": "utf-8",
        }
        config["loggers"][name]["handlers"].append("file")
        config["root"]["handlers"].append("file")

    logging.config.dictConfig(config)
    # disable loggers from other libraries
    if blacklist is not None:
        for log_level, loggers in blacklist.items():
            for l in loggers:
                logging.getLogger(l).setLevel(log_level)

    return logging.getLogger(name)
