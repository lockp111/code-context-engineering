package com.example.demo;

import java.util.List;
import java.util.Optional;
import static java.util.Collections.emptyList;

// 接口（含 default 方法）
public interface UserService {
    User findById(Long id);
    List<User> findAll();
    default void init() { /* 默认初始化 */ }
}

// 抽象类
abstract class BaseEntity {
    protected Long id;
    public abstract Long getId();
}

/* 多行注释测试
   这里的 class FakeClass 不应被识别
*/
// 普通类
public class User extends BaseEntity implements Comparable<User> {
    public static final int MAX_NAME_LENGTH = 50;  // 常量
    private String username;
    private String email;
    
    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
    
    @Override
    public Long getId() {
        return id;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    @Override
    public int compareTo(User other) {
        return this.username.compareTo(other.username);
    }
}

// 修饰符顺序变化
final public class ImmutableConfig {
    public static final String VERSION = "1.0.0";
}

// 静态内部类
class Outer {
    static final class Inner {}
}

// 枚举
public enum UserStatus {
    ACTIVE,
    INACTIVE,
    SUSPENDED
}

// Record (Java 14+)
public record UserDTO(Long id, String username, String email) {}

// 注解
public @interface Validated {
    String message() default "";
}

// 泛型方法
public class Utils {
    public static <T> Optional<T> findFirst(List<T> list) {
        return list.isEmpty() ? Optional.empty() : Optional.of(list.get(0));
    }
    
    /* 行内注释 */ public void helper() {}
}
