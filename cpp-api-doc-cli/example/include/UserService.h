#ifndef USER_SERVICE_H
#define USER_SERVICE_H

#include <string>
#include <vector>
#include <unordered_map>
#include <optional>

namespace example {

/**
 * @brief 代表一个用户的实体结构。
 */
struct User {
    std::string id;          ///< 用户的唯一标识符
    std::string name;        ///< 用户的显示名称
    std::optional<int> age;  ///< 用户年龄，如果不提供则为空
    std::optional<std::string> email; ///< 用户邮箱地址
};

/**
 * @brief 用户查询过滤条件。
 */
struct UserFilter {
    std::optional<std::string> nameContains; ///< 按名称模糊搜索
    std::optional<int> minAge;                ///< 按最小年龄筛选
};

/**
 * @brief 用户服务类，负责处理用户的增删改查。
 *
 * 这是一个单例服务，通常不需要实例化。
 *
 * @example
 * auto& svc = UserService::getInstance();
 * auto user = svc.findUser("123");
 */
class UserService {
public:
    /**
     * @brief 获取服务实例（单例模式）。
     * @return UserService& 单例实例引用
     */
    static UserService& getInstance();

    /**
     * @brief 根据 ID 查找用户。
     *
     * @param id 要查找的用户 ID
     * @return 找到的用户指针，如果未找到则返回 nullptr
     * @throws std::invalid_argument 当 ID 为空时抛出错误
     */
    const User* findUser(const std::string& id) const;

    /**
     * @brief 根据过滤条件查询用户列表。
     *
     * @param filter 查询过滤条件
     * @return 匹配的用户列表
     */
    std::vector<User> listUsers(const std::optional<UserFilter>& filter = std::nullopt) const;

    /**
     * @brief 创建新用户。
     *
     * @param name 用户名称
     * @param age 用户年龄（可选）
     * @param email 用户邮箱（可选）
     * @return 创建完成的用户对象（含自动生成的 id）
     */
    User createUser(const std::string& name,
                    const std::optional<int>& age = std::nullopt,
                    const std::optional<std::string>& email = std::nullopt);

    /**
     * @brief 删除指定用户。
     *
     * @param id 要删除的用户 ID
     * @return 是否删除成功
     */
    bool deleteUser(const std::string& id);

private:
    UserService() = default;
    static UserService* instance_;
    std::unordered_map<std::string, User> users_;
};

} // namespace example

#endif // USER_SERVICE_H
