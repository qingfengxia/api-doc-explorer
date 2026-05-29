package com.example.product;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 商品服务类，负责商品的增删改查和库存管理。
 *
 * <p>提供了完整的商品生命周期管理功能，包括创建、查询、上下架和库存调整。
 * 使用 {@link UUID} 生成唯一商品 ID。</p>
 *
 * @author example
 * @see Product
 * @see ProductCategory
 */
public class ProductService {

    private static ProductService instance;
    private final Map<String, Product> products = new HashMap<>();

    /** 私有构造函数，防止外部直接实例化。 */
    private ProductService() {}

    /**
     * 获取服务实例（单例模式）。
     *
     * @return ProductService 单例实例
     */
    public static synchronized ProductService getInstance() {
        if (instance == null) {
            instance = new ProductService();
        }
        return instance;
    }

    /**
     * 创建一个新商品。
     *
     * @param name        商品名称
     * @param description 商品描述
     * @param price       商品价格（单位：分）
     * @param category    商品类目
     * @param stock       库存数量
     * @return 新创建的商品对象
     * @throws IllegalArgumentException 如果价格为负数
     */
    public Product createProduct(String name, String description,
                                  long price, ProductCategory category, int stock) {
        if (price < 0) {
            throw new IllegalArgumentException("Price cannot be negative");
        }
        String id = "prod_" + UUID.randomUUID().toString();
        Product product = new Product(id, name, description, price, category, stock);
        products.put(id, product);
        return product;
    }

    /**
     * 根据 ID 查找商品。
     *
     * @param id 商品 ID
     * @return 商品对象，未找到返回 null
     */
    public Product findProduct(String id) {
        return products.get(id);
    }

    /**
     * 按类目查询所有上架商品。
     *
     * @param category 商品类目
     * @return 该类目下的上架商品列表
     */
    public List<Product> listByCategory(ProductCategory category) {
        return products.values().stream()
                .filter(p -> p.getCategory() == category && p.isActive())
                .collect(Collectors.toList());
    }

    /**
     * 按关键字搜索商品名称或描述。
     *
     * @param keyword 搜索关键字
     * @return 匹配的商品列表
     */
    public List<Product> search(String keyword) {
        if (keyword == null || keyword.isEmpty()) {
            return new ArrayList<>(products.values());
        }
        String lower = keyword.toLowerCase();
        return products.values().stream()
                .filter(p -> (p.getName() != null && p.getName().toLowerCase().contains(lower))
                          || (p.getDescription() != null && p.getDescription().toLowerCase().contains(lower)))
                .collect(Collectors.toList());
    }

    /**
     * 调整商品库存数量。
     *
     * @param id    商品 ID
     * @param delta 库存变化量（正数加库存，负数减库存）
     * @return 更新后的商品对象，未找到返回 null
     * @throws IllegalArgumentException 如果库存调整后为负数
     */
    public Product adjustStock(String id, int delta) {
        Product product = products.get(id);
        if (product == null) return null;
        product.adjustStock(delta);
        return product;
    }

    /**
     * 上架或下架商品。
     *
     * @param id     商品 ID
     * @param active {@code true} 上架，{@code false} 下架
     * @return 更新后的商品，未找到返回 null
     */
    public Product setActive(String id, boolean active) {
        Product product = products.get(id);
        if (product == null) return null;
        product.setActive(active);
        return product;
    }

    /**
     * 删除指定商品。
     *
     * @param id 商品 ID
     * @return {@code true} 如果删除成功，{@code false} 如果商品不存在
     */
    public boolean deleteProduct(String id) {
        return products.remove(id) != null;
    }

    /**
     * 获取所有商品数量。
     *
     * @return 商品总数
     */
    public int count() {
        return products.size();
    }
}
