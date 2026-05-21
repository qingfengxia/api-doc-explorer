/**
 * 代表一个用户的实体接口。
 * @public
 */
export interface User {
  /** 用户的唯一标识符 */
  id: string;
  /** 用户的显示名称 */
  name: string;
  /** 用户年龄，如果不提供则为 undefined */
  age?: number;
  /** 用户邮箱地址 */
  email?: string;
}

/**
 * 用户查询过滤条件。
 * @public
 */
export interface UserFilter {
  /** 按名称模糊搜索 */
  nameContains?: string;
  /** 按最小年龄筛选 */
  minAge?: number;
}

/**
 * 用户服务类，负责处理用户的增删改查。
 *
 * @remarks
 * 这是一个单例服务，通常不需要实例化。
 *
 * @example
 * ```ts
 * const user = await UserService.getInstance().findUser("123");
 * console.log(user.name);
 * ```
 */
export class UserService {
  private static instance: UserService;
  private users: Map<string, User> = new Map();

  /**
   * 私有构造函数，防止外部直接 new。
   */
  private constructor() {}

  /**
   * 获取服务实例（单例模式）。
   * @returns {UserService} 单例实例
   */
  static getInstance(): UserService {
    if (!UserService.instance) {
      UserService.instance = new UserService();
    }
    return UserService.instance;
  }

  /**
   * 根据 ID 查找用户。
   *
   * @param id - 要查找的用户 ID
   * @returns 返回用户对象，如果未找到则返回 null
   * @throws {Error} 当 ID 格式不正确时抛出错误
   */
  async findUser(id: string): Promise<User | null> {
    if (!id) throw new Error("ID is required");
    return this.users.get(id) ?? null;
  }

  /**
   * 根据过滤条件查询用户列表。
   *
   * @param filter - 查询过滤条件
   * @returns 匹配的用户列表
   */
  async listUsers(filter?: UserFilter): Promise<User[]> {
    let results = Array.from(this.users.values());
    if (filter?.nameContains) {
      results = results.filter(u =>
        u.name.toLowerCase().includes(filter.nameContains!.toLowerCase())
      );
    }
    if (filter?.minAge !== undefined) {
      results = results.filter(u => u.age !== undefined && u.age >= filter.minAge!);
    }
    return results;
  }

  /**
   * 创建新用户。
   *
   * @param userData - 不含 id 的用户数据
   * @returns 创建完成的用户对象（含自动生成的 id）
   */
  createUser(userData: Omit<User, "id">): User {
    const user: User = { ...userData, id: Date.now().toString() };
    this.users.set(user.id, user);
    return user;
  }

  /**
   * 删除指定用户。
   *
   * @param id - 要删除的用户 ID
   * @returns 是否删除成功
   */
  deleteUser(id: string): boolean {
    return this.users.delete(id);
  }
}
