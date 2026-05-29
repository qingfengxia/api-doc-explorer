package com.example.service;

import com.example.model.User;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 用户服务类，负责处理用户的增删改查。
 *
 * <p>这是一个单例服务，使用 {@code getInstance()} 获取实例。</p>
 *
 * @author example
 * @see User
 */
public class UserService {

    private static UserService instance;
    private final Map<String, User> users = new HashMap<>();

    /** 私有构造函数，防止外部直接实例化。 */
    private UserService() {}

    /**
     * 获取服务实例（单例模式）。
     *
     * @return UserService 单例实例
     */
    public static synchronized UserService getInstance() {
        if (instance == null) {
            instance = new UserService();
        }
        return instance;
    }

    /**
     * 根据 ID 查找用户。
     *
     * @param id 要查找的用户 ID，不能为 null 或空
     * @return 用户对象，如果未找到则返回 null
     * @throws IllegalArgumentException 如果 id 为 null 或空字符串
     */
    public User findUser(String id) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("ID is required");
        }
        return users.get(id);
    }

    /**
     * 查询所有用户。
     *
     * @return 用户列表，不会为 null
     */
    public List<User> listUsers() {
        return new ArrayList<>(users.values());
    }

    /**
     * 根据名称模糊搜索用户。
     *
     * @param name 搜索关键字（匹配名称中包含的字符串）
     * @return 匹配的用户列表
     */
    public List<User> searchByName(String name) {
        if (name == null || name.isEmpty()) {
            return listUsers();
        }
        return users.values().stream()
                .filter(u -> u.getName() != null && u.getName().toLowerCase().contains(name.toLowerCase()))
                .collect(Collectors.toList());
    }

    /**
     * 创建新用户。
     *
     * @param name  用户名称
     * @param age   用户年龄（可以为 null）
     * @param email 用户邮箱（可以为 null）
     * @return 创建完成的用户对象（含自动生成的 ID）
     */
    public User createUser(String name, Integer age, String email) {
        String id = UUID.randomUUID().toString();
        User user = new User(id, name, age, email);
        users.put(id, user);
        return user;
    }

    /**
     * 删除指定用户。
     *
     * @param id 要删除的用户 ID
     * @return {@code true} 如果删除成功，{@code false} 如果用户不存在
     */
    public boolean deleteUser(String id) {
        return users.remove(id) != null;
    }
}
