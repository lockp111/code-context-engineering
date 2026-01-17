use std::collections::HashMap;

const CONST_VAL: i32 = 10;
static STATIC_VAL: i32 = 20;

struct MyStruct {
    field: i32,
}

enum MyEnum {
    A,
    B(i32),
}

trait MyTrait {
    fn trait_method(&self);
}

impl MyStruct {
    fn new() -> Self {
        Self { field: 0 }
    }
}

impl MyTrait for MyStruct {
    fn trait_method(&self) {}
}

fn my_func() {}

macro_rules! my_macro {
    () => {};
}
