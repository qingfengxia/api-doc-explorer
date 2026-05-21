package com.example.model;

/**
 * 代表一个用户的实体类。
 *
 * <p>包含用户的基本信息如 ID、姓名、年龄、邮箱。</p>
 *
 * @author example
 */
public class User {

    /** 用户的唯一标识符 */
    private String id;

    /** 用户的显示名称 */
    private String name;

    /** 用户年龄，可选 */
    private Integer age;

    /** 用户邮箱地址，可选 */
    private String email;

    /**
     * 创建一个用户实例。
     *
     * @param id    用户的唯一标识符
     * @param name  用户的显示名称
     * @param age   用户年龄（可以为 null）
     * @param email 用户邮箱（可以为 null）
     */
    public User(String id, String name, Integer age, String email) {
        this.id = id;
        this.name = name;
        this.age = age;
        this.email = email;
    }

    /**
     * 获取用户 ID。
     *
     * @return 用户 ID
     */
    public String getId() { return id; }

    /**
     * 获取用户姓名。
     *
     * @return 用户姓名
     */
    public String getName() { return name; }

    /**
     * 获取用户年龄。
     *
     * @return 用户年龄，可能为 null
     */
    public Integer getAge() { return age; }

    /**
     * 获取用户邮箱。
     *
     * @return 用户邮箱，可能为 null
     */
    public String getEmail() { return email; }
}
