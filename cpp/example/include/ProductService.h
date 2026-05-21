#ifndef PRODUCT_SERVICE_H
#define PRODUCT_SERVICE_H

#include <string>
#include <vector>
#include <unordered_map>
#include <optional>

namespace example {

/**
 * @brief 商品类别的枚举定义。
 */
enum class ProductCategory {
    Electronics, ///< 电子产品
    Clothing,    ///< 服装
    Food,        ///< 食品
    Books        ///< 书籍
};

/**
 * @brief 商品实体的结构定义。
 */
struct Product {
    std::string id;             ///< 商品唯一标识符
    std::string name;           ///< 商品名称
    std::string description;    ///< 商品描述
    int price;                  ///< 商品价格，单位为分
    ProductCategory category;   ///< 商品类目
    int stock;                  ///< 库存数量
    bool active;                ///< 商品是否上架
};

/**
 * @brief 创建商品的输入参数，不含 id 和 active 字段。
 */
struct CreateProductInput {
    std::string name;           ///< 商品名称
    std::string description;    ///< 商品描述
    int price;                  ///< 商品价格，单位为分
    ProductCategory category;   ///< 商品类目
    std::optional<int> stock;   ///< 库存数量，默认为 0
};

/**
 * @brief 商品服务类，负责商品的增删改查和库存管理。
 *
 * 提供了完整的商品生命周期管理功能，包括创建、查询、上下架和库存调整。
 *
 * @example
 * auto& svc = ProductService::getInstance();
 * auto product = svc.createProduct({"TypeScript 实战", "一本关于 TypeScript 的书",
 *                                   8900, ProductCategory::Books});
 */
class ProductService {
public:
    /**
     * @brief 获取服务实例（单例模式）。
     * @return ProductService& 单例实例引用
     */
    static ProductService& getInstance();

    /**
     * @brief 创建一个新商品。
     *
     * @param input 创建商品的输入参数
     * @return 新创建的商品对象
     * @throws std::invalid_argument 当价格为负数时抛出错误
     */
    Product createProduct(const CreateProductInput& input);

    /**
     * @brief 根据 ID 查找商品。
     *
     * @param id 商品 ID
     * @return 商品指针，未找到返回 nullptr
     */
    const Product* findProduct(const std::string& id) const;

    /**
     * @brief 按类目查询所有上架商品。
     *
     * @param category 商品类目
     * @return 该类目下的上架商品列表
     */
    std::vector<Product> listByCategory(ProductCategory category) const;

    /**
     * @brief 调整商品库存数量。
     *
     * @param id 商品 ID
     * @param delta 库存变化量（正数加库存，负数减库存）
     * @return 更新后的商品指针，未找到返回 nullptr
     * @throws std::invalid_argument 当库存调整后为负数时抛出错误
     */
    const Product* adjustStock(const std::string& id, int delta);

    /**
     * @brief 上架或下架商品。
     *
     * @param id 商品 ID
     * @param active 是否上架
     * @return 更新后的商品指针，未找到返回 nullptr
     */
    const Product* setActive(const std::string& id, bool active);

private:
    ProductService() = default;
    static ProductService* instance_;
    std::unordered_map<std::string, Product> products_;
};

} // namespace example

#endif // PRODUCT_SERVICE_H
