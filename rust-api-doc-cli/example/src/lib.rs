//! `example` — Rust API 示例库。
//!
//! 这个 crate 演示了如何在 Rust 中使用文档注释（doc comments），
//! 以及如何通过 `rustdoc --output-format json` 导出为 JSON 格式，
//! 供 `rust-api-explorer` 查询。

/// 日志级别枚举。
///
/// 级别从低到高：`Debug` → `Info` → `Warn` → `Error`。
///
/// # Examples
///
/// ```rust
/// let level = LogLevel::Info;
/// assert!(level as u8 == 1);
/// ```
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
    /// 调试级别，记录最详细的信息。
    Debug = 0,
    /// 信息级别，记录常规运行信息。
    Info = 1,
    /// 警告级别，记录潜在问题。
    Warn = 2,
    /// 错误级别，记录已发生的错误。
    Error = 3,
}

/// 日志条目，记录单条日志的内容。
pub struct LogEntry {
    /// 日志消息内容。
    pub message: String,
    /// 日志级别。
    pub level: LogLevel,
    /// 可选的附加上下文（JSON 字符串）。
    pub context: Option<String>,
}

impl LogEntry {
    /// 创建一个新的日志条目。
    ///
    /// # Arguments
    ///
    /// * `message` - 日志消息
    /// * `level` - 日志级别
    /// * `context` - 可选的上下文字符串
    pub fn new(message: String, level: LogLevel, context: Option<String>) -> Self {
        Self { message, level, context }
    }

    /// 格式化日志条目为可读字符串。
    pub fn format(&self) -> String {
        let ctx = self.context.as_deref().unwrap_or("");
        format!("[{:?}] {} {}", self.level, self.message, ctx)
    }
}

/// 日志服务，提供分级日志记录功能。
///
/// 支持设定最低输出级别，低于该级别的日志将被忽略。
///
/// # Example
///
/// ```rust
/// let mut logger = LoggerService::new(LogLevel::Info);
/// logger.info("Server started");
/// ```
pub struct LoggerService {
    min_level: LogLevel,
    entries: Vec<LogEntry>,
}

impl LoggerService {
    /// 创建一个新的日志服务实例。
    ///
    /// # Arguments
    ///
    /// * `min_level` - 最低输出日志级别
    pub fn new(min_level: LogLevel) -> Self {
        Self { min_level, entries: Vec::new() }
    }

    /// 设置最低输出日志级别。
    pub fn set_min_level(&mut self, level: LogLevel) {
        self.min_level = level;
    }

    /// 记录一条信息级别日志。
    pub fn info(&mut self, message: &str) {
        self.log(LogLevel::Info, message, None);
    }

    /// 记录一条信息级别日志（带上下文）。
    pub fn info_with_context(&mut self, message: &str, context: &str) {
        self.log(LogLevel::Info, message, Some(context));
    }

    /// 记录一条错误级别日志。
    pub fn error(&mut self, message: &str) {
        self.log(LogLevel::Error, message, None);
    }

    /// 获取所有已记录的日志条目。
    pub fn get_entries(&self) -> &[LogEntry] {
        &self.entries
    }

    /// 清空所有日志条目。
    pub fn clear(&mut self) {
        self.entries.clear();
    }

    fn log(&mut self, level: LogLevel, message: &str, context: Option<&str>) {
        if (level as u8) < (self.min_level as u8) {
            return;
        }
        let entry = LogEntry::new(
            message.to_string(),
            level,
            context.map(|s| s.to_string()),
        );
        self.entries.push(entry);
    }
}

/// 用户信息的结构体。
///
/// 包含用户的基本资料，如 ID、姓名和邮箱。
///
/// # Fields
///
/// - `id` - 用户唯一标识
/// - `name` - 用户显示名称
/// - `email` - 用户邮箱地址
pub struct User {
    /// 用户唯一标识符。
    pub id: String,
    /// 用户显示名称。
    pub name: String,
    /// 用户邮箱地址。
    pub email: String,
}

impl User {
    /// 创建一个新用户。
    ///
    /// # Arguments
    ///
    /// * `id` - 用户 ID
    /// * `name` - 用户名称
    /// * `email` - 用户邮箱
    pub fn new(id: String, name: String, email: String) -> Self {
        Self { id, name, email }
    }

    /// 返回用户的显示名称。
    pub fn display_name(&self) -> &str {
        &self.name
    }

    /// 更新用户邮箱地址。
    ///
    /// # Arguments
    ///
    /// * `email` - 新的邮箱地址
    pub fn update_email(&mut self, email: String) {
        self.email = email;
    }
}

/// 商品类别的枚举。
///
/// 用于划分商品所属的分类。
pub enum ProductCategory {
    /// 电子产品（手机、电脑等）。
    Electronics,
    /// 服装（上衣、裤子等）。
    Clothing,
    /// 食品（零食、饮料等）。
    Food,
    /// 书籍。
    Books,
}

/// 商品实体。
///
/// 包含商品的基本信息，支持库存调整和上下架操作。
pub struct Product {
    /// 商品唯一标识符。
    pub id: String,
    /// 商品名称。
    pub name: String,
    /// 商品描述。
    pub description: String,
    /// 商品价格，单位为分。
    pub price: u64,
    /// 商品类目。
    pub category: ProductCategory,
    /// 库存数量。
    pub stock: i32,
    /// 商品是否上架。
    pub active: bool,
}

impl Product {
    /// 创建一个新商品。
    ///
    /// # Arguments
    ///
    /// * `id` - 商品 ID
    /// * `name` - 商品名称
    /// * `description` - 商品描述
    /// * `price` - 商品价格（单位：分）
    /// * `category` - 商品类目
    /// * `stock` - 初始库存
    pub fn new(
        id: String,
        name: String,
        description: String,
        price: u64,
        category: ProductCategory,
        stock: i32,
    ) -> Self {
        Self { id, name, description, price, category, stock, active: true }
    }

    /// 调整库存数量。
    ///
    /// # Arguments
    ///
    /// * `delta` - 变化量（正数增加，负数减少）
    ///
    /// # Panics
    ///
    /// 如果调整后库存为负数，会 panic。
    pub fn adjust_stock(&mut self, delta: i32) {
        let new_stock = self.stock + delta;
        assert!(new_stock >= 0, "Stock cannot be negative");
        self.stock = new_stock;
    }

    /// 设置商品是否上架。
    ///
    /// # Arguments
    ///
    /// * `active` - `true` 表示上架，`false` 表示下架
    pub fn set_active(&mut self, active: bool) {
        self.active = active;
    }
}

/// 可序列化的 trait，将对象转换为 JSON 字符串。
///
/// 任何实现了该 trait 的类型都可以调用 `to_json()` 方法输出 JSON。
pub trait ToJson {
    /// 将对象转换为 JSON 字符串。
    fn to_json(&self) -> String;
}

impl ToJson for LogLevel {
    fn to_json(&self) -> String {
        format!("\"{:?}\"", self)
    }
}

/// 计算两个数字的和。
///
/// # Arguments
///
/// * `a` - 第一个加数
/// * `b` - 第二个加数
///
/// # Returns
///
/// 返回 `a + b` 的结果。
///
/// # Example
///
/// ```rust
/// assert_eq!(add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// 根据名称查找用户。
///
/// 在用户列表中遍历查找名称匹配的用户。
/// 匹配是大小写不敏感的。
///
/// # Arguments
///
/// * `users` - 用户列表切片
/// * `name` - 要查找的用户名
///
/// # Returns
///
/// 返回第一个匹配的用户引用，如果没有找到则返回 `None`。
pub fn find_user_by_name<'a>(users: &'a [User], name: &str) -> Option<&'a User> {
    users.iter().find(|u| u.name.to_lowercase() == name.to_lowercase())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_create_user() {
        let user = User::new("u1".into(), "Alice".into(), "alice@example.com".into());
        assert_eq!(user.display_name(), "Alice");
    }

    #[test]
    fn test_logger() {
        let mut logger = LoggerService::new(LogLevel::Warn);
        logger.info("should be ignored");
        logger.error("should be logged");
        assert_eq!(logger.get_entries().len(), 1);
    }
}
