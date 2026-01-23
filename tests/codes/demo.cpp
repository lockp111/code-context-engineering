#include <iostream>
#include <vector>

namespace MyNamespace {

enum Color { Red, Green, Blue };

enum class Status { Active, Inactive };

typedef int IntAlias;

using StringAlias = std::string;

class MyClass {
public:
    MyClass();
    virtual ~MyClass();
    void method();
};

struct MyStruct {
    int x;
};

template <typename T>
void templateFunc(T t) {}

void my_func() {}

} // namespace MyNamespace
