"""
Core expression classes for representing mathematical expressions as an AST.
"""
from abc import ABC, abstractmethod
import math
from typing import Dict, Set, Optional, Union


class Expression(ABC):
    """Base class for all mathematical expressions."""
    
    @abstractmethod
    def evaluate(self, variables: Dict[str, float]) -> Union[float, 'Expression']:
        """Evaluate the expression with given variable values."""
        pass
    
    @abstractmethod
    def derivative(self, var: str) -> 'Expression':
        """Compute the derivative with respect to a variable."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the expression."""
        pass
    
    @abstractmethod
    def get_variables(self) -> Set[str]:
        """Get all variables in the expression."""
        pass
    
    @abstractmethod
    def simplify(self) -> 'Expression':
        """Simplify the expression."""
        pass
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Add(self, other)
    
    def __radd__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Add(other, self)
    
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Subtract(self, other)
    
    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Subtract(other, self)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Multiply(self, other)
    
    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Multiply(other, self)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Divide(self, other)
    
    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Divide(other, self)
    
    def __pow__(self, other):
        if isinstance(other, (int, float)):
            other = Number(other)
        return Power(self, other)
    
    def __neg__(self):
        return Multiply(Number(-1), self)


class Number(Expression):
    """Represents a numeric constant."""
    
    def __init__(self, value: float):
        self.value = float(value)
    
    def evaluate(self, variables: Dict[str, float]) -> float:
        return self.value
    
    def derivative(self, var: str) -> Expression:
        return Number(0)
    
    def __str__(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)
    
    def get_variables(self) -> Set[str]:
        return set()
    
    def simplify(self) -> Expression:
        return self


class Variable(Expression):
    """Represents a variable."""
    
    def __init__(self, name: str):
        self.name = name
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        if self.name in variables:
            return variables[self.name]
        return self
    
    def derivative(self, var: str) -> Expression:
        if self.name == var:
            return Number(1)
        return Number(0)
    
    def __str__(self) -> str:
        return self.name
    
    def get_variables(self) -> Set[str]:
        return {self.name}
    
    def simplify(self) -> Expression:
        return self


class BinaryOp(Expression):
    """Base class for binary operations."""
    
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()


class Add(BinaryOp):
    """Addition operation."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)
        
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val + right_val
        
        if isinstance(left_val, Expression) or isinstance(right_val, Expression):
            return Add(
                left_val if isinstance(left_val, Expression) else Number(left_val),
                right_val if isinstance(right_val, Expression) else Number(right_val)
            )
    
    def derivative(self, var: str) -> Expression:
        return Add(self.left.derivative(var), self.right.derivative(var))
    
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 + x = x
        if isinstance(left, Number) and left.value == 0:
            return right
        if isinstance(right, Number) and right.value == 0:
            return left
        
        # Constant folding
        if isinstance(left, Number) and isinstance(right, Number):
            return Number(left.value + right.value)
        
        return Add(left, right)


class Subtract(BinaryOp):
    """Subtraction operation."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)
        
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val - right_val
        
        if isinstance(left_val, Expression) or isinstance(right_val, Expression):
            return Subtract(
                left_val if isinstance(left_val, Expression) else Number(left_val),
                right_val if isinstance(right_val, Expression) else Number(right_val)
            )
    
    def derivative(self, var: str) -> Expression:
        return Subtract(self.left.derivative(var), self.right.derivative(var))
    
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # x - 0 = x
        if isinstance(right, Number) and right.value == 0:
            return left
        
        # x - x = 0
        if str(left) == str(right):
            return Number(0)
        
        # Constant folding
        if isinstance(left, Number) and isinstance(right, Number):
            return Number(left.value - right.value)
        
        return Subtract(left, right)


class Multiply(BinaryOp):
    """Multiplication operation."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)
        
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val * right_val
        
        if isinstance(left_val, Expression) or isinstance(right_val, Expression):
            return Multiply(
                left_val if isinstance(left_val, Expression) else Number(left_val),
                right_val if isinstance(right_val, Expression) else Number(right_val)
            )
    
    def derivative(self, var: str) -> Expression:
        # Product rule: (f*g)' = f'*g + f*g'
        return Add(
            Multiply(self.left.derivative(var), self.right),
            Multiply(self.left, self.right.derivative(var))
        )
    
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 * x = 0
        if isinstance(left, Number) and left.value == 0:
            return Number(0)
        if isinstance(right, Number) and right.value == 0:
            return Number(0)
        
        # 1 * x = x
        if isinstance(left, Number) and left.value == 1:
            return right
        if isinstance(right, Number) and right.value == 1:
            return left
        
        # Constant folding
        if isinstance(left, Number) and isinstance(right, Number):
            return Number(left.value * right.value)
        
        return Multiply(left, right)


class Divide(BinaryOp):
    """Division operation."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)
        
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            if right_val == 0:
                raise ValueError("Division by zero")
            return left_val / right_val
        
        if isinstance(left_val, Expression) or isinstance(right_val, Expression):
            return Divide(
                left_val if isinstance(left_val, Expression) else Number(left_val),
                right_val if isinstance(right_val, Expression) else Number(right_val)
            )
    
    def derivative(self, var: str) -> Expression:
        # Quotient rule: (f/g)' = (f'*g - f*g') / g^2
        return Divide(
            Subtract(
                Multiply(self.left.derivative(var), self.right),
                Multiply(self.left, self.right.derivative(var))
            ),
            Power(self.right, Number(2))
        )
    
    def __str__(self) -> str:
        return f"({self.left} / {self.right})"
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 / x = 0
        if isinstance(left, Number) and left.value == 0:
            return Number(0)
        
        # x / 1 = x
        if isinstance(right, Number) and right.value == 1:
            return left
        
        # x / x = 1
        if str(left) == str(right):
            return Number(1)
        
        # Constant folding
        if isinstance(left, Number) and isinstance(right, Number):
            if right.value == 0:
                raise ValueError("Division by zero")
            return Number(left.value / right.value)
        
        return Divide(left, right)


class Power(BinaryOp):
    """Power operation."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        left_val = self.left.evaluate(variables)
        right_val = self.right.evaluate(variables)
        
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val ** right_val
        
        if isinstance(left_val, Expression) or isinstance(right_val, Expression):
            return Power(
                left_val if isinstance(left_val, Expression) else Number(left_val),
                right_val if isinstance(right_val, Expression) else Number(right_val)
            )
    
    def derivative(self, var: str) -> Expression:
        # For f(x)^n where n is constant: n * f(x)^(n-1) * f'(x)
        if isinstance(self.right, Number):
            return Multiply(
                Multiply(self.right, Power(self.left, Number(self.right.value - 1))),
                self.left.derivative(var)
            )
        # General case: f(x)^g(x) = exp(g(x) * ln(f(x)))
        return Multiply(
            self,
            Add(
                Multiply(self.right.derivative(var), Ln(self.left)),
                Multiply(
                    self.right,
                    Divide(self.left.derivative(var), self.left)
                )
            )
        )
    
    def __str__(self) -> str:
        return f"({self.left}^{self.right})"
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # x^0 = 1
        if isinstance(right, Number) and right.value == 0:
            return Number(1)
        
        # x^1 = x
        if isinstance(right, Number) and right.value == 1:
            return left
        
        # 0^x = 0 (for x > 0)
        if isinstance(left, Number) and left.value == 0:
            return Number(0)
        
        # 1^x = 1
        if isinstance(left, Number) and left.value == 1:
            return Number(1)
        
        # Constant folding
        if isinstance(left, Number) and isinstance(right, Number):
            return Number(left.value ** right.value)
        
        return Power(left, right)


class UnaryOp(Expression):
    """Base class for unary operations."""
    
    def __init__(self, expr: Expression):
        self.expr = expr
    
    def get_variables(self) -> Set[str]:
        return self.expr.get_variables()


class Sin(UnaryOp):
    """Sine function."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        val = self.expr.evaluate(variables)
        if isinstance(val, (int, float)):
            return math.sin(val)
        return Sin(val)
    
    def derivative(self, var: str) -> Expression:
        # (sin(f))' = cos(f) * f'
        return Multiply(Cos(self.expr), self.expr.derivative(var))
    
    def __str__(self) -> str:
        return f"sin({self.expr})"
    
    def simplify(self) -> Expression:
        expr = self.expr.simplify()
        if isinstance(expr, Number):
            return Number(math.sin(expr.value))
        return Sin(expr)


class Cos(UnaryOp):
    """Cosine function."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        val = self.expr.evaluate(variables)
        if isinstance(val, (int, float)):
            return math.cos(val)
        return Cos(val)
    
    def derivative(self, var: str) -> Expression:
        # (cos(f))' = -sin(f) * f'
        return Multiply(
            Multiply(Number(-1), Sin(self.expr)),
            self.expr.derivative(var)
        )
    
    def __str__(self) -> str:
        return f"cos({self.expr})"
    
    def simplify(self) -> Expression:
        expr = self.expr.simplify()
        if isinstance(expr, Number):
            return Number(math.cos(expr.value))
        return Cos(expr)


class Ln(UnaryOp):
    """Natural logarithm function."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        val = self.expr.evaluate(variables)
        if isinstance(val, (int, float)):
            if val <= 0:
                raise ValueError("Logarithm of non-positive number")
            return math.log(val)
        return Ln(val)
    
    def derivative(self, var: str) -> Expression:
        # (ln(f))' = f' / f
        return Divide(self.expr.derivative(var), self.expr)
    
    def __str__(self) -> str:
        return f"ln({self.expr})"
    
    def simplify(self) -> Expression:
        expr = self.expr.simplify()
        if isinstance(expr, Number):
            if expr.value <= 0:
                raise ValueError("Logarithm of non-positive number")
            return Number(math.log(expr.value))
        return Ln(expr)


class Exp(UnaryOp):
    """Exponential function (e^x)."""
    
    def evaluate(self, variables: Dict[str, float]) -> Union[float, Expression]:
        val = self.expr.evaluate(variables)
        if isinstance(val, (int, float)):
            return math.exp(val)
        return Exp(val)
    
    def derivative(self, var: str) -> Expression:
        # (e^f)' = e^f * f'
        return Multiply(self, self.expr.derivative(var))
    
    def __str__(self) -> str:
        return f"exp({self.expr})"
    
    def simplify(self) -> Expression:
        expr = self.expr.simplify()
        if isinstance(expr, Number):
            return Number(math.exp(expr.value))
        return Exp(expr)