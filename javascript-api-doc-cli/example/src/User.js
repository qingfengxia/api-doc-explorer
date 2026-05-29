/**
 * 代表一个用户的实体类。
 * @public
 */
class User {
  /**
   * @param {string} id - 用户的唯一标识符
   * @param {string} name - 用户的显示名称
   * @param {number} [age] - 用户年龄，可选
   * @param {string} [email] - 用户邮箱地址，可选
   */
  constructor(id, name, age, email) {
    /** 用户的唯一标识符 */
    this.id = id;
    /** 用户的显示名称 */
    this.name = name;
    /** 用户年龄，如果不提供则为 undefined */
    this.age = age;
    /** 用户邮箱地址 */
    this.email = email;
  }
}

/**
 * 用户查询过滤条件。
 * @typedef {Object} UserFilter
 * @property {string} [nameContains] - 按名称模糊搜索
 * @property {number} [minAge] - 按最小年龄筛选
 */

export { User };
