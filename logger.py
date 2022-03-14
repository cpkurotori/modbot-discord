import logging
import json
import os

_default_log_factory = logging.getLogRecordFactory()


def _log_factory(
    name, level, fn, lno, msg, args, exc_info, func=None, sinfo=None, **kwargs
):
    msg = json.dumps(msg)
    return _default_log_factory(
        name, level, fn, lno, msg, args, exc_info, func=func, sinfo=sinfo, **kwargs
    )

logging.setLogRecordFactory(_log_factory)

_log_level = os.getenv("LOGLEVEL", "INFO")
LOGGER = logging.getLogger("modbot")
LOGGER.setLevel(_log_level)

ch = logging.StreamHandler()
ch.setLevel(_log_level)

formatter = logging.Formatter(
    """{"ts": "%(asctime)s", "level": "%(levelname)s", "caller": "%(name)s.%(funcName)s:%(lineno)d", "log": %(message)s}"""
)
formatter.converter
ch.setFormatter(formatter)

LOGGER.handlers.clear()
LOGGER.addHandler(ch)
LOGGER.propagate = False

