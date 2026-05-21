package com.example.logger;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * 日志服务，提供分级日志记录功能。
 *
 * <p>支持设定最低输出级别，低于该级别的日志将被忽略。同时支持格式化输出和日志条目查询。</p>
 *
 * @author example
 * @see LogLevel
 */
public class LoggerService {

    private final LogLevel minLevel;
    private final List<LogEntry> entries = new ArrayList<>();

    /**
     * 创建 LoggerService 实例。
     *
     * @param minLevel 最低输出日志级别，低于此级别的日志会被忽略
     */
    public LoggerService(LogLevel minLevel) {
        this.minLevel = minLevel;
    }

    /**
     * 记录一条信息级别日志。
     *
     * @param message 日志消息
     */
    public void info(String message) {
        log(LogLevel.INFO, message, null);
    }

    /**
     * 记录一条信息级别日志（带上下文）。
     *
     * @param message 日志消息
     * @param context 附加上下文对象
     */
    public void info(String message, Object context) {
        log(LogLevel.INFO, message, context);
    }

    /**
     * 记录一条警告级别日志。
     *
     * @param message 日志消息
     */
    public void warn(String message) {
        log(LogLevel.WARN, message, null);
    }

    /**
     * 记录一条错误级别日志。
     *
     * @param message 日志消息
     */
    public void error(String message) {
        log(LogLevel.ERROR, message, null);
    }

    /**
     * 记录一条错误级别日志（带异常）。
     *
     * @param message 日志消息
     * @param cause   相关的异常
     */
    public void error(String message, Throwable cause) {
        log(LogLevel.ERROR, message + ": " + cause.getMessage(), cause);
    }

    /**
     * 获取所有已记录的日志条目。
     *
     * @return 只读的日志条目列表
     */
    public List<LogEntry> getEntries() {
        return new ArrayList<>(entries);
    }

    /**
     * 清空所有日志条目。
     */
    public void clear() {
        entries.clear();
    }

    private void log(LogLevel level, String message, Object context) {
        if (level.getLevel() < minLevel.getLevel()) return;
        LogEntry entry = new LogEntry(LocalDateTime.now(), level, message, context);
        entries.add(entry);
        System.out.println(entry.format());
    }

    /**
     * 表示一条日志条目的内部记录类。
     */
    public static class LogEntry {
        private final LocalDateTime timestamp;
        private final LogLevel level;
        private final String message;
        private final Object context;

        LogEntry(LocalDateTime timestamp, LogLevel level, String message, Object context) {
            this.timestamp = timestamp;
            this.level = level;
            this.message = message;
            this.context = context;
        }

        /**
         * 获取日志时间戳。
         *
         * @return 日志记录的时间
         */
        public LocalDateTime getTimestamp() { return timestamp; }

        /**
         * 获取日志级别。
         *
         * @return 日志级别
         */
        public LogLevel getLevel() { return level; }

        /**
         * 获取日志消息。
         *
         * @return 日志消息内容
         */
        public String getMessage() { return message; }

        /**
         * 获取附加上下文。
         *
         * @return 上下文对象，可能为 null
         */
        public Object getContext() { return context; }

        String format() {
            String time = timestamp.format(DateTimeFormatter.ISO_LOCAL_TIME);
            return String.format("[%s] [%s] %s", time, level.name(), message);
        }
    }
}
