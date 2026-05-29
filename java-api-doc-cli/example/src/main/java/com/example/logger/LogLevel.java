package com.example.logger;

/**
 * 日志级别的枚举定义。
 *
 * <p>级别从低到高：DEBUG → INFO → WARN → ERROR。日志服务会过滤掉低于设定级别的日志。</p>
 *
 * @author example
 */
public enum LogLevel {

    /** 调试级别，记录最详细的信息 */
    DEBUG(0),

    /** 信息级别，记录常规运行信息 */
    INFO(1),

    /** 警告级别，记录潜在问题 */
    WARN(2),

    /** 错误级别，记录已发生的错误 */
    ERROR(3);

    private final int level;

    LogLevel(int level) {
        this.level = level;
    }

    /**
     * 获取级别的整数值。
     *
     * @return 级别数值，数值越大优先级越高
     */
    public int getLevel() {
        return level;
    }
}
