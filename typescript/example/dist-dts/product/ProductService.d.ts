import { Product, CreateProductInput, ProductCategory } from "./types";
/**
 * 商品服务类，负责商品的增删改查和库存管理。
 *
 * @remarks
 * 提供了完整的商品生命周期管理功能，包括创建、查询、上下架和库存调整。
 *
 * @example
 * ```ts
 * const service = ProductService.getInstance();
 * const product = service.createProduct({
 *   name: "TypeScript 实战",
 *   description: "一本关于 TypeScript 的书",
 *   price: 8900,
 *   category: ProductCategory.Books,
 * });
 * ```
 */
export declare class ProductService {
    private static instance;
    private products;
    private constructor();
    /**
     * 获取服务实例（单例模式）。
     * @returns {ProductService} 单例实例
     */
    static getInstance(): ProductService;
    /**
     * 创建一个新商品。
     *
     * @param input - 创建商品的输入参数
     * @returns 新创建的商品对象
     * @throws {Error} 当价格为负数时抛出错误
     */
    createProduct(input: CreateProductInput): Product;
    /**
     * 根据 ID 查找商品。
     *
     * @param id - 商品 ID
     * @returns 商品对象，未找到返回 null
     */
    findProduct(id: string): Product | null;
    /**
     * 按类目查询所有上架商品。
     *
     * @param category - 商品类目
     * @returns 该类目下的上架商品列表
     */
    listByCategory(category: ProductCategory): Product[];
    /**
     * 调整商品库存数量。
     *
     * @param id - 商品 ID
     * @param delta - 库存变化量（正数加库存，负数减库存）
     * @returns 更新后的商品对象，未找到返回 null
     * @throws {Error} 当库存调整后为负数时抛出错误
     */
    adjustStock(id: string, delta: number): Product | null;
    /**
     * 上架或下架商品。
     *
     * @param id - 商品 ID
     * @param active - 是否上架
     * @returns 更新后的商品，未找到返回 null
     */
    setActive(id: string, active: boolean): Product | null;
}
//# sourceMappingURL=ProductService.d.ts.map