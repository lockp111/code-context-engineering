package com.example.demo

import kotlin.collections.List
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.Dispatchers
import java.util.Optional as JavaOptional

// 接口
interface UserService {
    fun findById(id: Long): User?
    fun findAll(): List<User>
    suspend fun fetchRemote(): User
}

// Fun interface (SAM)
fun interface Callback {
    fun invoke(result: String)
}

// Sealed interface
sealed interface State {
    object Idle : State
    data class Loading(val progress: Int) : State
}

// 抽象类
abstract class BaseEntity {
    abstract val id: Long
    open fun validate(): Boolean = true
}

/* 多行注释测试
   这里的 class FakeClass 不应被识别
*/

// 普通类
open class User(
    override val id: Long,
    val username: String,
    val email: String
) : BaseEntity(), Comparable<User> {
    
    companion object {
        const val MAX_NAME_LENGTH = 50
        fun create(username: String): User = User(0, username, "")
    }
    
    override fun compareTo(other: User): Int {
        return username.compareTo(other.username)
    }
}

// Data class
data class UserDTO(
    val id: Long,
    val username: String,
    val email: String
)

// Sealed class
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Value class (内联类)
@JvmInline
value class UserId(val value: Long)

// Enum class
enum class UserStatus {
    ACTIVE,
    INACTIVE,
    SUSPENDED
}

// Annotation class
@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Validated(val message: String = "")

// Object (单例)
object UserRepository {
    private val users = mutableListOf<User>()
    
    fun save(user: User) {
        users.add(user)
    }
    
    fun findAll(): List<User> = users.toList()
}

// 扩展函数
fun String.isValidEmail(): Boolean {
    return contains("@") && contains(".")
}

// 泛型函数
fun <T> List<T>.findFirst(): T? {
    return if (isEmpty()) null else this[0]
}

// suspend 函数
suspend fun fetchData(url: String): String {
    return "data"
}

// inline 函数
inline fun <reified T> parseJson(json: String): T {
    throw NotImplementedError()
}

// infix 函数
infix fun Int.times(str: String): String {
    return str.repeat(this)
}

// 高阶函数
fun processUsers(users: List<User>, action: (User) -> Unit) {
    users.forEach(action)
}

// 类型别名
typealias UserList = List<User>
typealias CompletionHandler = (Result<String>) -> Unit

// 顶层属性
val VERSION = "1.0.0"
var debugMode = false

// 测试字符串中的 // 不被当作注释
val url = "https://example.com/path"
val regex = "pattern//test"

// 带命名的 companion object
class Config {
    companion object Factory {
        fun default(): Config = Config()
    }
}

// 内部类
class Outer {
    inner class Inner {
        fun getOuterReference() = this@Outer
    }
}

// 泛型类
class Box<T>(val value: T) {
    fun <R> map(transform: (T) -> R): Box<R> = Box(transform(value))
}
