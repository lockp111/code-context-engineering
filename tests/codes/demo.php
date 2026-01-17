<?php
namespace MyNamespace;

use Another\Class as Alias;

const CONST_VAL = 1;

interface MyInterface {
    public function method();
}

trait MyTrait {
    public function traitMethod() {}
}

abstract class AbstractClass {
    abstract protected function abstractMethod();
}

class MyClass extends AbstractClass implements MyInterface {
    use MyTrait;
    
    public static $staticProp;
    
    public function method() {}
    
    protected function abstractMethod() {}
}

function my_func() {}
