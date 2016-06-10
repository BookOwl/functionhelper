#!usr/bin/env python3

"""
Functional programming helpers
"""
# TODO:
# Add docs

import inspect
from functools import reduce

def curry(f):
    """A function decorator that automaticly curries a function.
    Examples:
    >>> @curry
    >>> def add3(a,b,c):
    ...     return a + b + c
    >>> add3(1)(2)(3)
    6
    >>> add3(1,2)(3)
    6
    >>> add3(1)(b=2)(c=3)
    6
    >>> add3()(1,2,3)
    6
    >>> add3(1,2,3)
    6
    """    
    def inner1(*args, **kwargs):
        f_args, f_kwargs = list(args), dict(kwargs)
        def tryret():
            try:
                return f(*f_args, **f_kwargs)
            except TypeError as e:
                if "missing" in e.args[0]:
                    return inner2
                else:
                    raise
        def inner2(*args, **kwargs):
            f_args.extend(args)
            f_kwargs.update(kwargs)
            return tryret()
        return tryret()
    return inner1

class Pipeline:
    """A Pipeline object allows you to send data through a chain of functions
    without having to nest a bunch of parentheses or using temporary variables.
    Examples:
    >>> import math
    >>> p = Pipeline(math.pi)
    >>> p.then(lambda n: n*2).then(math.cos).run().result
    1.0

    This object has three (3) public data members:
    self.data = The original data passed to the constructor.
    self.result = The result of running all the functions on self.data,
                or None if the run method hasn't been called.
    """
    def __init__(self, data):
        "Creates a Pipeline object out of data"
        self.data = data
        self.result = None
        self.hasrun = False
        self._funcs = []
    
    def then(self, func):
        "Arranges for func to be called next in the pipeline"
        if not callable(func):
            raise TypeError("func must be callable")
        self._funcs.append(func)
        self.hasrun = False
        return self
    
    def run(self, force=False):
        """Runs all of the functions on the data.
        This function is lazy. If no more functions have been added
        and this method has been run before, it will not do anything.
        You can change this by passing True for the force argument"""
        if force or not self.hasrun:
            self.result = reduce( (lambda data, func: func(data)),
                                   self._funcs,
                                   self.data)
            self.hasrun = True
        return self

class dispatch:
    """A function decorator for Haskell-style multidispactch
    on parameter values, types, and on predicates"""
    def __init__(self, func):
        self._base = func
        self._overloads = []
        self.__doc__ = self._base.__doc__
        
    def match(self, func):
        "Adds func as a possible dispatch function"
        self._overloads.append(func)
        return self
    
    def __call__(self, *args, **kwargs):
        "Finds the dispatch function that matches the given args and kwargs, and calls it"
        for overload in self._overloads:
            sig = inspect.signature(overload)
            try:
                bound = sig.bind(*args, **kwargs)
            except TypeError:
                pass
            else:
                for name, val in bound.arguments.items():
                    t = sig.parameters[name].annotation
                    if not (t != inspect._empty and t == val or
                            (not inspect.isclass(t) and callable(t) and t(val)) or
                            (isinstance(val, t) if (inspect.isclass(t) or type(t) == tuple) else False)):
                        break
                else:
                    return overload(*args, **kwargs)
        return self._base(*args, **kwargs)

def compose(*funcs):
    """Takes one or more functions and returns a new function that calls each function on the data
    compose(f, g)(x) is the same as f(g(x))"""
    if not funcs:
        raise TypeError("compose() takes one or more arguments (0 given)")
    if not all(callable(f) for f in funcs):
        raise TypeError("compose takes one or more callables")
    def call(val):
        return reduce((lambda data, func: func(data)), reversed(funcs), val)
    return call

def cascade(func, times):
    "Returns a function that calls f(f(... f(x))) times times."
    if not callable(func):
        raise TypeError("func is not a callable")
    return compose(*([func] * times))

def foreach(iterable, func):
    "Calls func on each item of iterable"
    if not callable(func):
        raise TypeError(repr(func) + " is not callable")
    for thing in iterable:
        func(thing)

def id_(thing):
    "Returns a function that always returns thing"
    return lambda: thing
    
