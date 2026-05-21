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
export class ProductService {
  private static instance: ProductService;
  private products: Map<string, Product> = new Map();

  private constructor() {}

  /**
   * 获取服务实例（单例模式）。
   * @returns {ProductService} 单例实例
   */
  static getInstance(): ProductService {
    if (!ProductService.instance) {
      ProductService.instance = new ProductService();
    }
    return ProductService.instance;
  }

  /**
   * 创建一个新商品。
   *
   * @param input - 创建商品的输入参数
   * @returns 新创建的商品对象
   * @throws {Error} 当价格为负数时抛出错误
   */
  createProduct(input: CreateProductInput): Product {
    if (input.price < 0) throw new Error("Price cannot be negative");
    const product: Product = {
      id: `prod_${Date.now()}`,
      ...input,
      stock: input.stock ?? 0,
      active: true,
    };
    this.products.set(product.id, product);
    return product;
  }

  /**
   * 根据 ID 查找商品。
   *
   * @param id - 商品 ID
   * @returns 商品对象，未找到返回 null
   */
  findProduct(id: string): Product | null {
    return this.products.get(id) ?? null;
  }

  /**
   * 按类目查询所有上架商品。
   *
   * @param category - 商品类目
   * @returns 该类目下的上架商品列表
   */
  listByCategory(category: ProductCategory): Product[] {
    return Array.from(this.products.values()).filter(
      p => p.category === category && p.active
    );
  }

  /**
   * 调整商品库存数量。
   *
   * @param id - 商品 ID
   * @param delta - 库存变化量（正数加库存，负数减库存）
   * @returns 更新后的商品对象，未找到返回 null
   * @throws {Error} 当库存调整后为负数时抛出错误
   */
  adjustStock(id: string, delta: number): Product | null {
    const product = this.products.get(id);
    if (!product) return null;
    const newStock = product.stock + delta;
    if (newStock < 0) throw new Error("Stock cannot be negative");
    product.stock = newStock;
    return product;
  }

  /**
   * 上架或下架商品。
   *
   * @param id - 商品 ID
   * @param active - 是否上架
   * @returns 更新后的商品，未找到返回 null
   */
  setActive(id: string, active: boolean): Product | null {
    const product = this.products.get(id);
    if (!product) return null;
    product.active = active;
    return product;
  }
}
