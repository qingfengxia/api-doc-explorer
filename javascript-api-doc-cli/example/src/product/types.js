/**
 * 商品类别的枚举定义。
 * @readonly
 * @enum {string}
 * @public
 */
const ProductCategory = {
  /** 电子产品 */
  Electronics: 'electronics',
  /** 服装 */
  Clothing: 'clothing',
  /** 食品 */
  Food: 'food',
  /** 书籍 */
  Books: 'books',
};

/**
 * 创建商品的输入参数。
 * @typedef {Object} CreateProductInput
 * @property {string} name - 商品名称
 * @property {string} description - 商品描述
 * @property {number} price - 商品价格，单位为分
 * @property {string} category - 商品类目（使用 ProductCategory 枚举值）
 * @property {number} [stock=0] - 库存数量，默认为 0
 */

export { ProductCategory };
