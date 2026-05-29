import { ProductCategory } from './types.js';

/**
 * @typedef {Object} Product
 * @property {string} id - 商品唯一标识符
 * @property {string} name - 商品名称
 * @property {string} description - 商品描述
 * @property {number} price - 商品价格，单位为分
 * @property {string} category - 商品类目
 * @property {number} stock - 库存数量
 * @property {boolean} active - 商品是否上架
 */

/**
 * 商品服务类，负责商品的增删改查和库存管理。
 *
 * @class
 * @public
 *
 * @example
 * ```js
 * const service = ProductService.getInstance();
 * const product = service.createProduct({
 *   name: 'Node.js 实战',
 *   description: '一本关于 Node.js 的书',
 *   price: 8900,
 *   category: ProductCategory.Books,
 * });
 * console.log(product);
 * ```
 */
class ProductService {
  constructor() {
    /** @private */
    this._products = new Map();
  }

  /** @private */
  static _instance = null;

  /**
   * 获取服务实例（单例模式）。
   *
   * @static
   * @returns {ProductService} 单例实例
   */
  static getInstance() {
    if (!ProductService._instance) {
      ProductService._instance = new ProductService();
    }
    return ProductService._instance;
  }

  /**
   * 创建一个新商品。
   *
   * @param {CreateProductInput} input - 创建商品的输入参数
   * @returns {Product} 新创建的商品对象
   * @throws {Error} 当价格为负数时抛出错误
   */
  createProduct(input) {
    if (input.price < 0) throw new Error('Price cannot be negative');
    const product = {
      id: `prod_${Date.now()}`,
      name: input.name,
      description: input.description,
      price: input.price,
      category: input.category,
      stock: input.stock ?? 0,
      active: true,
    };
    this._products.set(product.id, product);
    return product;
  }

  /**
   * 根据 ID 查找商品。
   *
   * @param {string} id - 商品 ID
   * @returns {Product|null} 商品对象，未找到返回 null
   */
  findProduct(id) {
    return this._products.get(id) ?? null;
  }

  /**
   * 按类目查询所有上架商品。
   *
   * @param {string} category - 商品类目（使用 ProductCategory 枚举值）
   * @returns {Array<Product>} 该类目下的上架商品列表
   */
  listByCategory(category) {
    return Array.from(this._products.values()).filter(
      p => p.category === category && p.active
    );
  }

  /**
   * 调整商品库存数量。
   *
   * @param {string} id - 商品 ID
   * @param {number} delta - 库存变化量（正数加库存，负数减库存）
   * @returns {Product|null} 更新后的商品对象，未找到返回 null
   * @throws {Error} 当库存调整后为负数时抛出错误
   */
  adjustStock(id, delta) {
    const product = this._products.get(id);
    if (!product) return null;
    const newStock = product.stock + delta;
    if (newStock < 0) throw new Error('Stock cannot be negative');
    product.stock = newStock;
    return product;
  }

  /**
   * 上架或下架商品。
   *
   * @param {string} id - 商品 ID
   * @param {boolean} active - 是否上架
   * @returns {Product|null} 更新后的商品，未找到返回 null
   */
  setActive(id, active) {
    const product = this._products.get(id);
    if (!product) return null;
    product.active = active;
    return product;
  }
}

export { ProductService };
