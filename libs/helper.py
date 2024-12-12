# -*- coding: utf-8 -*-

import time
import datetime
import hashlib
import random
import logging
import sys
from typing import Dict, Optional

loggers: Dict[str, logging.Logger] = {}


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获得一个logger 实例，用来打印日志
    Args:
        name: logger的名称
    Return:
        返回一个logger实例
    """
    global loggers

    if not name:
        name = __name__

    has = loggers.get(name)
    if has:
        return has

    logger = logging.getLogger(name=name)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)

    loggers[name] = logger

    return logger


def get_current_time() -> int:
    return int(time.time() * 1000)

    

def get_unix_time_tuple(date=datetime.datetime.now(), millisecond: bool = False) -> str:
    """get time tuple

    get unix time tuple, default `date` is current time

    Args:
        date: datetime, default is datetime.datetime.now()
        millisecond: if True, Use random three digits instead of milliseconds, \
            default id False

    Return:
        a str type value, return unix time of incoming time
    """
    time_tuple = time.mktime(date.timetuple())
    time_tuple = round(time_tuple * 1000) if millisecond else time_tuple
    second = str(int(time_tuple))
    return second


def get_date_from_time_tuple(
    unix_time: str = get_unix_time_tuple(), formatter: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """translate unix time tuple to time

    get time from unix time

    Args:
        unix_time: unix time tuple
        formatter: str time formatter

    Return:
        a time type value, return time of incoming unix_time
    """
    if len(unix_time) == 13:
        unix_time = str(float(unix_time) / 1000)
    t = int(unix_time)
    time_locol = time.localtime(t)
    return time.strftime(formatter, time_locol)


def getmd5(code: str) -> Optional[str]:
    """return md5 value of incoming code

    get md5 from code

    Args:
        code: str value

    Return:
        return md5 value of code
    """
    if code:
        md5string = hashlib.md5(code.encode("utf-8"))
        return md5string.hexdigest()
    return None


def get_uuid_str() -> str:
    """get uuid

    get uuid

    Return:
        return uuid
    """
    import uuid

    return uuid.uuid4().hex


def get_random_num(digit: int = 6) -> str:
    """get a random num

    get random num

    Args:
        digit: digit of the random num, limit (1, 32)

    Return:
        return Generated random num
    """
    if digit is None:
        digit = 1
    digit = min(max(digit, 1), 32)  # 最大支持32位
    result = ""
    while len(result) < digit:
        append = str(random.randint(1, 9))
        result = result + append
    return result