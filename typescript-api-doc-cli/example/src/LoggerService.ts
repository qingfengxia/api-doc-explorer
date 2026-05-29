/**
 * 日志级别的枚举定义。
 * @public
 */
export enum LogLevel {
  /** 调试级别 */
  Debug = 0,
  /** 信息级别 */
  Info = 1,
  /** 警告级别 */
  Warn = 2,
  /** 错误级别 */
  Error = 3,
}

/**
 * 日志条目的结构。
 * @public
 */
export interface LogEntry {
  /** 日志时间戳 */
  timestamp: number;
  /** 日志级别 */
  level: LogLevel;
  /** 日志消息 */
  message: string;
  /** 附加上下文数据 */
  context?: Record<string, unknown>;
}

/**
 * 日志服务，提供分级日志记录功能。
 *
 * @remarks
 * 支持设定最低输出级别，低于该级别的日志将被忽略。同时提供格式化和上下文附加能力。
 *
 * @example
 * ```ts
 * const logger = new LoggerService(LogLevel.Info);
 * logger.info("Server started", { port: 3000 });
 * logger.debug("This will be ignored");
 * ```
 */
export class LoggerService {
  private minLevel: LogLevel;
  private entries: LogEntry[] = [];

  /**
   * 创建 LoggerService 实例。
   *
   * @param minLevel - 最低输出日志级别，默认为 Info
   */
  constructor(minLevel: LogLevel = LogLevel.Info) {
    this.minLevel = minLevel;
  }

  /**
   * 设置最低输出日志级别。
   *
   * @param level - 新的最低日志级别
   */
  setMinLevel(level: LogLevel): void {
    this.minLevel = level;
  }

  /**
   * 记录一条调试级别日志。
   *
   * @param message - 日志消息
   * @param context - 附加上下文
   */
  debug(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.Debug, message, context);
  }

  /**
   * 记录一条信息级别日志。
   *
   * @param message - 日志消息
   * @param context - 附加上下文
   */
  info(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.Info, message, context);
  }

  /**
   * 记录一条警告级别日志。
   *
   * @param message - 日志消息
   * @param context - 附加上下文
   */
  warn(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.Warn, message, context);
  }

  /**
   * 记录一条错误级别日志。
   *
   * @param message - 日志消息
   * @param context - 附加上下文
   */
  error(message: string, context?: Record<string, unknown>): void {
    this.log(LogLevel.Error, message, context);
  }

  /**
   * 获取所有已记录的日志条目。
   *
   * @returns 日志条目列表
   */
  getEntries(): LogEntry[] {
    return [...this.entries];
  }

  /**
   * 清空所有日志条目。
   */
  clear(): void {
    this.entries = [];
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    if (level < this.minLevel) return;
    const entry: LogEntry = { timestamp: Date.now(), level, message, context };
    this.entries.push(entry);
    const prefix = LogLevel[level];
    const output = context
      ? `[${prefix}] ${message} ${JSON.stringify(context)}`
      : `[${prefix}] ${message}`;
    console.log(output);
  }
}
