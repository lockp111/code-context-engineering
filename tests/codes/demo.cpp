#include <iostream>
#include <vector>

namespace MyNamespace {

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
