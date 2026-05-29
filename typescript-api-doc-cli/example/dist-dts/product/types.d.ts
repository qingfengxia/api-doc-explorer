/**
 * 商品类别的枚举定义。
 * @public
 */
export declare enum ProductCategory {
    /** 电子产品 */
    Electronics = "electronics",
    /** 服装 */
    Clothing = "clothing",
    /** 食品 */
    Food = "food",
    /** 书籍 */
    Books = "books"
}
/**
 * 商品实体的接口定义。
 * @public
 */
export interface Product {
    /** 商品唯一标识符 */
    id: string;
    /** 商品名称 */
    name: string;
    /** 商品描述 */
    description: string;
    /** 商品价格，单位为分 */
    price: number;
    /** 商品类目 */
    category: ProductCategory;
    /** 库存数量 */
    stock: number;
    /** 商品是否上架 */
    active: boolean;
}
/**
 * 创建商品的输入参数，不含 id 和 active 字段。
 * @public
 */
export interface CreateProductInput {
    /** 商品名称 */
    name: string;
    /** 商品描述 */
    description: string;
    /** 商品价格，单位为分 */
    price: number;
    /** 商品类目 */
    category: ProductCategory;
    /** 库存数量，默认为 0 */
    stock?: number;
}
//# sourceMappingURL=types.d.ts.map