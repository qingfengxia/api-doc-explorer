"""
日志服务模块，提供分级日志记录功能。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
import time


class LogLevel(Enum):
    """日志级别的枚举定义。"""
    DEBUG = 0  #: 调试级别
    INFO = 1   #: 信息级别
    WARN = 2   #: 警告级别
    ERROR = 3  #: 错误级别


@dataclass
class LogEntry:
    """日志条目的结构。

    Attributes:
        timestamp: 日志时间戳
        level: 日志级别
        message: 日志消息
        context: 附加上下文数据
    """
    timestamp: float
    level: LogLevel
    message: str
    context: Optional[Dict[str, Any]] = None


class LoggerService:
    """日志服务，提供分级日志记录功能。

    支持设定最低输出级别，低于该级别的日志将被忽略。
    同时提供格式化和上下文附加能力。

    Example::

        logger = LoggerService(LogLevel.INFO)
        logger.info("Server started", {"port": 3000})
        logger.debug("This will be ignored")
    """

    def __init__(self, min_level: LogLevel = LogLevel.INFO) -> None:
        """创建 LoggerService 实例。

        Args:
            min_level: 最低输出日志级别，默认为 INFO
        """
        self._min_level = min_level
        self._entries: List[LogEntry] = []

    def set_min_level(self, level: LogLevel) -> None:
        """设置最低输出日志级别。

        Args:
            level: 新的最低日志级别
        """
        self._min_level = level

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录一条调试级别日志。

        Args:
            message: 日志消息
            context: 附加上下文（可选）
        """
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录一条信息级别日志。

        Args:
            message: 日志消息
            context: 附加上下文（可选）
        """
        self._log(LogLevel.INFO, message, context)

    def warn(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录一条警告级别日志。

        Args:
            message: 日志消息
            context: 附加上下文（可选）
        """
        self._log(LogLevel.WARN, message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录一条错误级别日志。

        Args:
            message: 日志消息
            context: 附加上下文（可选）
        """
        self._log(LogLevel.ERROR, message, context)

    def get_entries(self) -> List[LogEntry]:
        """获取所有已记录的日志条目。

        Returns:
            日志条目列表
        """
        return list(self._entries)

    def clear(self) -> None:
        """清空所有日志条目。"""
        self._entries.clear()

    def _log(self, level: LogLevel, message: str,
             context: Optional[Dict[str, Any]] = None) -> None:
        if level.value < self._min_level.value:
            return
        entry = LogEntry(timestamp=time.time(), level=level, message=message, context=context)
        self._entries.append(entry)
        prefix = level.name
        output = f"[{prefix}] {message}"
        if context:
            output += f" {context}"
        print(output)
