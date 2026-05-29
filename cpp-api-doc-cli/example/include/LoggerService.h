#ifndef LOGGER_SERVICE_H
#define LOGGER_SERVICE_H

#include <string>
#include <vector>
#include <unordered_map>
#include <variant>
#include <chrono>

namespace example {

/**
 * @brief 日志级别的枚举定义。
 */
enum class LogLevel {
    Debug = 0, ///< 调试级别
    Info  = 1, ///< 信息级别
    Warn  = 2, ///< 警告级别
    Error = 3  ///< 错误级别
};

/**
 * @brief 日志条目的结构。
 */
struct LogEntry {
    std::chrono::system_clock::time_point timestamp; ///< 日志时间戳
    LogLevel level;                                  ///< 日志级别
    std::string message;                             ///< 日志消息
    std::optional<std::unordered_map<std::string, std::string>> context; ///< 附加上下文数据
};

/**
 * @brief 日志服务，提供分级日志记录功能。
 *
 * 支持设定最低输出级别，低于该级别的日志将被忽略。
 * 同时提供格式化和上下文附加能力。
 *
 * @example
 * LoggerService logger(LogLevel::Info);
 * logger.info("Server started", {{"port", "3000"}});
 * logger.debug("This will be ignored");
 */
class LoggerService {
public:
    /**
     * @brief 创建 LoggerService 实例。
     *
     * @param minLevel 最低输出日志级别，默认为 Info
     */
    explicit LoggerService(LogLevel minLevel = LogLevel::Info);

    /**
     * @brief 设置最低输出日志级别。
     *
     * @param level 新的最低日志级别
     */
    void setMinLevel(LogLevel level);

    /**
     * @brief 记录一条调试级别日志。
     *
     * @param message 日志消息
     * @param context 附加上下文（可选）
     */
    void debug(const std::string& message,
               const std::optional<std::unordered_map<std::string, std::string>>& context = std::nullopt);

    /**
     * @brief 记录一条信息级别日志。
     *
     * @param message 日志消息
     * @param context 附加上下文（可选）
     */
    void info(const std::string& message,
              const std::optional<std::unordered_map<std::string, std::string>>& context = std::nullopt);

    /**
     * @brief 记录一条警告级别日志。
     *
     * @param message 日志消息
     * @param context 附加上下文（可选）
     */
    void warn(const std::string& message,
              const std::optional<std::unordered_map<std::string, std::string>>& context = std::nullopt);

    /**
     * @brief 记录一条错误级别日志。
     *
     * @param message 日志消息
     * @param context 附加上下文（可选）
     */
    void error(const std::string& message,
               const std::optional<std::unordered_map<std::string, std::string>>& context = std::nullopt);

    /**
     * @brief 获取所有已记录的日志条目。
     *
     * @return 日志条目列表
     */
    const std::vector<LogEntry>& getEntries() const;

    /**
     * @brief 清空所有日志条目。
     */
    void clear();

private:
    LogLevel minLevel_;
    std::vector<LogEntry> entries_;

    void log(LogLevel level, const std::string& message,
             const std::optional<std::unordered_map<std::string, std::string>>& context);
};

} // namespace example

#endif // LOGGER_SERVICE_H
