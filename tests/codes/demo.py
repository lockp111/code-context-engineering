import sys
import os
from typing import List, Optional

# Global variable
GLOBAL_VAR = "test"

def my_decorator(func):
    def wrapper():
        return func()
    return wrapper

@my_decorator
def decorated_func():
    """A decorated function"""
    pass

class MyClass:
    """A class docstring"""
    
    def __init__(self):
        self.value = 0

    def method_one(self, arg: int) -> None:
        pass

    @property
    def my_prop(self):
        return self.value

    async def async_method(self):
        pass

async def async_main():
    pass
