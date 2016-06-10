#! usr/bin/env python3
# test.py - Test functionhelper.py
import functionhelper as fh
import pytest

def test_curry():
    @fh.curry
    def add3(a,b,c):
        return a + b + c
    assert add3(1)(2)(3) == 6
    assert add3()(1,2)(3) == 6
    assert add3(1)()(2,3) == 6
    assert add3(1,2,3) == 6
    assert add3(a=1)(b=2)(c=3) == 6
    assert add3(1,2)(c=3) == 6
    with pytest.raises(TypeError):
        add3(1,2,3,4)
    with pytest.raises(TypeError):
        add3(1)(2,3,4)
    with pytest.raises(TypeError):
        add3()(1)()(2)(3,4)
    with pytest.raises(TypeError):
        add3(a=1)(2)

def test_Pipeline():
    p = fh.Pipeline(1)
    p.then(lambda x: x + 1).then(lambda x: x*2)
    assert p.run().result == 4
    assert p.run().result == 4
    p.then(lambda x: x - 2)
    assert p.run().result == 2
    with pytest.raises(TypeError):
        p.then(1)

def test_compose():
    def f(x): return x + 1
    def g(x): return x * 3
    h = fh.compose(f, g)
    assert h(1) == 4
    assert h(2) == 7
    with pytest.raises(TypeError):
        fh.compose()
    with pytest.raises(TypeError):
        fh.compose(1,2)

def test_cascade():
    def f(x): return x * 2
    g = fh.cascade(f, 3)
    assert g(1) == 8
    with pytest.raises(TypeError):
        fh.cascade(1, 2)

def test_id_():
    i = fh.id_(3)
    assert i() == 3

def test_foreach():
    i = 0
    def f(x):
        nonlocal i
        i += x
    fh.foreach([1,2,3], f)
    assert i == 6
    with pytest.raises(TypeError):
        fh.foreach((), 1)

def test_dispatch():
    # Dispatch on values
    @fh.dispatch
    def fact(n):
        return n * fact(n-1)
    @fact.match
    def fact(n:1):
        return 1
    # Dispatch on types
    @fh.dispatch
    def print_thing(thing):
        return "An unknown thing"
    @print_thing.match
    def print_thing(thing: (int, float)):
        return "This is a very mathmatical thing"
    @print_thing.match
    def print_thing(thing: str):
        return "This is a very textual thing"
    # Dispatch on a predicate
    @fh.dispatch
    def fib(n):
        return fib(n - 1) + fib(n - 2)
    @fib.match
    def fib(n: (lambda n: n <= 2)):
        return 1
    
    assert fact(5) == 120
    assert print_thing("") == "This is a very textual thing"
    assert print_thing(1) == "This is a very mathmatical thing"
    assert print_thing(1.0) == "This is a very mathmatical thing"
    assert print_thing([]) == "An unknown thing"
