package com.example.product;

/**
 * 商品实体类。
 *
 * <p>包含商品的基本信息，如 ID、名称、描述、价格、类目、库存和上架状态。</p>
 *
 * @author example
 * @see ProductCategory
 * @see ProductService
 */
public class Product {

    /** 商品唯一标识符 */
    private final String id;

    /** 商品名称 */
    private String name;

    /** 商品描述 */
    private String description;

    /** 商品价格，单位为分 */
    private long price;

    /** 商品类目 */
    private ProductCategory category;

    /** 库存数量 */
    private int stock;

    /** 商品是否上架 */
    private boolean active;

    /**
     * 创建商品实例。
     *
     * @param id          商品唯一标识符
     * @param name        商品名称
     * @param description 商品描述
     * @param price       商品价格（单位：分）
     * @param category    商品类目
     * @param stock       初始库存数量
     */
    public Product(String id, String name, String description, long price,
                   ProductCategory category, int stock) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.price = price;
        this.category = category;
        this.stock = stock;
        this.active = true;
    }

    /**
     * 获取商品 ID。
     *
     * @return 商品 ID
     */
    public String getId() { return id; }

    /**
     * 获取商品名称。
     *
     * @return 商品名称
     */
    public String getName() { return name; }

    /**
     * 获取商品描述。
     *
     * @return 商品描述
     */
    public String getDescription() { return description; }

    /**
     * 获取商品价格。
     *
     * @return 价格，单位为分
     */
    public long getPrice() { return price; }

    /**
     * 获取商品类目。
     *
     * @return 商品类目
     */
    public ProductCategory getCategory() { return category; }

    /**
     * 获取库存数量。
     *
     * @return 当前库存
     */
    public int getStock() { return stock; }

    /**
     * 判断商品是否上架。
     *
     * @return {@code true} 如果商品已上架
     */
    public boolean isActive() { return active; }

    /**
     * 设置商品是否上架。
     *
     * @param active {@code true} 上架，{@code false} 下架
     */
    public void setActive(boolean active) { this.active = active; }

    /**
     * 设置商品名称。
     *
     * @param name 新名称
     */
    public void setName(String name) { this.name = name; }

    /**
     * 设置商品价格。
     *
     * @param price 新价格（单位：分）
     */
    public void setPrice(long price) { this.price = price; }

    /**
     * 调整库存数量。
     *
     * @param delta 变化量（正数增加，负数减少）
     * @throws IllegalArgumentException 如果调整后库存为负数
     */
    public void adjustStock(int delta) {
        int newStock = this.stock + delta;
        if (newStock < 0) {
            throw new IllegalArgumentException("Stock cannot be negative");
        }
        this.stock = newStock;
    }
}
