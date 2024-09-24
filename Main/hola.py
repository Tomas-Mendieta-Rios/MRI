class Calculator:
    def __init__(self):
        self.result = 0  # Initializes the internal state

    def add(self, x, y):
        self.result = x + y  # Updates the internal state
        return self.result

    def subtract(self, x, y):
        self.result = x - y  # Updates the internal state
        return self.result

Calculator().add(5,3)

print(Calculator().result)

calc = Calculator()  # Creates a Calculator instance
calc.add(5, 3)  # Updates result to 8
print(calc.result)  # Now prints 8, since calc.result was updated
