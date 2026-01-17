package main

import "fmt"

const ConstVal = 10

type MyInterface interface {
	Method()
}

type MyStruct struct {
	Field int
}

func (s *MyStruct) Method() {
	fmt.Println("Method")
}

func Function(a int) int {
	return a
}

type Alias int
