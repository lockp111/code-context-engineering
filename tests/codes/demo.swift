import Foundation
import UIKit

// MARK: - Protocol
public protocol Drawable {
    func draw()
    var description: String { get }
}

protocol DataSource: AnyObject {
    associatedtype Item
    func numberOfItems() -> Int
}

// MARK: - Enum
enum Direction {
    case north, south, east, west
    
    func opposite() -> Direction {
        switch self {
        case .north: return .south
        case .south: return .north
        case .east: return .west
        case .west: return .east
        }
    }
}

public enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

// MARK: - Struct
struct Point {
    var x: Double
    var y: Double
    
    init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
    
    mutating func moveBy(dx: Double, dy: Double) {
        x += dx
        y += dy
    }
}

/* 多行注释测试
   struct FakeStruct 不应被识别
*/

// MARK: - Class
open class Shape: Drawable {
    private var name: String
    
    public init(name: String) {
        self.name = name
    }
    
    public func draw() {
        print("Drawing \(name)")
    }
    
    var description: String {
        return name
    }
}

final class Circle: Shape {
    let radius: Double
    
    init(radius: Double) {
        self.radius = radius
        super.init(name: "Circle")
    }
    
    override func draw() {
        print("Drawing circle with radius \(radius)")
    }
}

// MARK: - Extension
extension String {
    func trimmed() -> String {
        return trimmingCharacters(in: .whitespaces)
    }
}

extension Array where Element: Equatable {
    func unique() -> [Element] {
        var result: [Element] = []
        for item in self where !result.contains(item) {
            result.append(item)
        }
        return result
    }
}

// MARK: - Actor (Swift 5.5+)
actor DataManager {
    private var cache: [String: Any] = [:]
    
    func getValue(for key: String) -> Any? {
        return cache[key]
    }
    
    func setValue(_ value: Any, for key: String) {
        cache[key] = value
    }
}

// MARK: - Typealias
typealias CompletionHandler = (Result<Data, Error>) -> Void
public typealias JSON = [String: Any]

// MARK: - Property Wrapper
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    let range: ClosedRange<Value>
    
    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
    
    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

// MARK: - Async Function
@MainActor
class ViewModel {
    func fetchData() async throws -> Data {
        // 异步获取数据
        return Data()
    }
}
