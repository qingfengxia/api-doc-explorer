import { User } from './User.js';

/**
 * 用户服务类，负责处理用户的增删改查。
 *
 * @class
 * @public
 *
 * @example
 * ```js
 * const service = UserService.getInstance();
 * const user = await service.findUser("123");
 * console.log(user.name);
 * ```
 */
class UserService {
  constructor() {
    /** @private */
    this._users = new Map();
  }

  /** @private */
  static _instance = null;

  /**
   * 获取服务实例（单例模式）。
   *
   * @static
   * @returns {UserService} 单例实例
   */
  static getInstance() {
    if (!UserService._instance) {
      UserService._instance = new UserService();
    }
    return UserService._instance;
  }

  /**
   * 根据 ID 查找用户。
   *
   * @param {string} id - 要查找的用户 ID
   * @returns {Promise<User|null>} 返回用户对象，如果未找到则返回 null
   * @throws {Error} 当 ID 格式不正确时抛出错误
   */
  async findUser(id) {
    if (!id) throw new Error('ID is required');
    return this._users.get(id) ?? null;
  }

  /**
   * 根据过滤条件查询用户列表。
   *
   * @param {UserFilter} [filter] - 查询过滤条件
   * @returns {Array<User>} 匹配的用户列表
   */
  listUsers(filter) {
    let results = Array.from(this._users.values());
    if (filter) {
      if (filter.nameContains) {
        results = results.filter(u =>
          u.name.toLowerCase().includes(filter.nameContains.toLowerCase())
        );
      }
      if (filter.minAge !== undefined) {
        results = results.filter(u => u.age !== undefined && u.age >= filter.minAge);
      }
    }
    return results;
  }

  /**
   * 创建新用户。
   *
   * @param {Object} userData - 不含 id 的用户数据
   * @param {string} userData.name - 用户名称
   * @param {number} [userData.age] - 用户年龄
   * @param {string} [userData.email] - 用户邮箱
   * @returns {User} 创建完成的用户对象（含自动生成的 id）
   */
  createUser(userData) {
    const user = new User(
      Date.now().toString(),
      userData.name,
      userData.age,
      userData.email
    );
    this._users.set(user.id, user);
    return user;
  }

  /**
   * 删除指定用户。
   *
   * @param {string} id - 要删除的用户 ID
   * @returns {boolean} 是否删除成功
   */
  deleteUser(id) {
    return this._users.delete(id);
  }
}

export { UserService };
