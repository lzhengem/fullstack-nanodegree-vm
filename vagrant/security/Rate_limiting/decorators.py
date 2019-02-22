# In our chapter about recursive functions we introduced the factorial function. We wanted to keep the function as simple as possible and we didn't want to obscure the underlying idea, so we hadn't incorporated any argument checks. So, if somebody had called our function with a negative argument or with a float argument, our function would have got into an endless loop. 

# The following program uses a decorator function to ensure that the argument passed to the function factorial is a positive integer:

def argument_test_natural_number(f):
    def helper(x):
        if type(x) == int and x > 0:
            return f(x)
        else:
            raise Exception("Argument is not an integer")
    return helper
    
@argument_test_natural_number
def factorial(n):
    if n == 1:
        return 1
    else:
        return n * factorial(n-1)

for i in range(1,10):
    print(i, factorial(i))

print(factorial(-1))



# using decorators to see how many times a function has been run:

def call_counter(func):
    def helper(x):
        helper.calls += 1
        return func(x)
    helper.calls = 0

    return helper

@call_counter
def succ(x):
    return x + 1

print(succ.calls)
for i in range(10):
    succ(i)
    
print(succ.calls)

The output looks like this:
0
10


# These two decorators are nearly the same, except for the greeting. We want to add a parameter to the decorator to be capable of customizing the greeting, when we do the decoration. We have to wrap another function around our previous decorator function to accomplish this. We can now easy say "Good Morning" in the Greek way:
def greeting(expr):
    def greeting_decorator(func):
        def function_wrapper(x):
            print(expr + ", " + func.__name__ + " returns:")
            func(x)
        return function_wrapper
    return greeting_decorator

@greeting("καλημερα")
def foo(x):
    print(42)

foo("Hi")