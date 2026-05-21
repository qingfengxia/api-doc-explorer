/**
 * 日志级别的枚举定义。
 * @enum {number}
 * @readonly
 * @public
 */
const LogLevel = {
  /** 调试级别 */
  Debug: 0,
  /** 信息级别 */
  Info: 1,
  /** 警告级别 */
  Warn: 2,
  /** 错误级别 */
  Error: 3,
};

/**
 * 日志服务，提供分级日志记录功能。
 *
 * @class
 * @public
 *
 * @example
 * ```js
 * const logger = new LoggerService(LogLevel.Info);
 * logger.info('Server started', { port: 3000 });
 * ```
 */
class LoggerService {
  /**
   * 创建 LoggerService 实例。
   *
   * @param {number} [minLevel=LogLevel.Info] - 最低输出日志级别
   */
  constructor(minLevel = LogLevel.Info) {
    /** @private */
    this._minLevel = minLevel;
    /** @private */
    this._entries = [];
  }

  /**
   * 设置最低输出日志级别。
   *
   * @param {number} level - 新的最低日志级别（使用 LogLevel 枚举值）
   */
  setMinLevel(level) {
    this._minLevel = level;
  }

  /**
   * 记录一条调试级别日志。
   *
   * @param {string} message - 日志消息
   * @param {Object} [context] - 附加上下文数据
   */
  debug(message, context) {
    this._log(LogLevel.Debug, message, context);
  }

  /**
   * 记录一条信息级别日志。
   *
   * @param {string} message - 日志消息
   * @param {Object} [context] - 附加上下文数据
   */
  info(message, context) {
    this._log(LogLevel.Info, message, context);
  }

  /**
   * 记录一条警告级别日志。
   *
   * @param {string} message - 日志消息
   * @param {Object} [context] - 附加上下文数据
   */
  warn(message, context) {
    this._log(LogLevel.Warn, message, context);
  }

  /**
   * 记录一条错误级别日志。
   *
   * @param {string} message - 日志消息
   * @param {Object} [context] - 附加上下文数据
   */
  error(message, context) {
    this._log(LogLevel.Error, message, context);
  }

  /**
   * 获取所有已记录的日志条目。
   *
   * @returns {Array<Object>} 日志条目列表
   */
  getEntries() {
    return [...this._entries];
  }

  /**
   * 清空所有日志条目。
   */
  clear() {
    this._entries = [];
  }

  /**
   * @private
   * @param {number} level
   * @param {string} message
   * @param {Object} [context]
   */
  _log(level, message, context) {
    if (level < this._minLevel) return;
    const entry = { timestamp: Date.now(), level, message, context };
    this._entries.push(entry);
    const levelNames = ['Debug', 'Info', 'Warn', 'Error'];
    const prefix = levelNames[level] || 'Unknown';
    const output = context
      ? `[${prefix}] ${message} ${JSON.stringify(context)}`
      : `[${prefix}] ${message}`;
    console.log(output);
  }
}

export { LogLevel, LoggerService };
