/// 程序的入口点。
///
/// 演示了如何创建和使用各个模块的 API。
fn main() {
    // 创建日志服务
    let mut logger = example::LoggerService::new(example::LogLevel::Info);
    logger.info("Application started");

    // 创建用户
    let user = example::User::new("u1".into(), "Alice".into(), "alice@example.com".into());
    println!("User: {}", user.display_name());

    // 创建商品
    let product = example::Product::new(
        "p1".into(),
        "Rust Book".into(),
        "Learn Rust".into(),
        5900,
        example::ProductCategory::Books,
        10,
    );
    println!("Product: {} (${:.2})", product.name, product.price as f64 / 100.0);
}
