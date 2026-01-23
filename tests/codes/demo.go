package main

import "fmt"

const ConstVal = 10
var GlobalVar = "hello"

type MyInterface interface {
	Method()
}

type MyStruct struct {
	Field int
}

type Alias int
type StringAlias = string
type FuncType func(int) int

func (s *MyStruct) Method() {
	fmt.Println("Method")
}

func Function(a int) int {
	return a
}

func GenericFunc[T any](val T) T {
	return val
}
