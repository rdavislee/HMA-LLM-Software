# Mathematical Expression Library

A Python library for parsing, evaluating, differentiating, and integrating mathematical expressions symbolically.

## Features

- **Expression Parsing**: Convert string expressions into an Abstract Syntax Tree (AST)
- **Evaluation**: Evaluate expressions with given variable values
- **Symbolic Differentiation**: Compute derivatives of expressions
- **Symbolic Integration**: Compute indefinite and definite integrals
- **Simplification**: Automatically simplify expressions

## File Structure

```
expression.py    - Core expression classes and AST implementation
parser.py        - Expression parser to convert strings to AST
operations.py    - Mathematical operations (integration, substitution)
utils.py         - Main interface functions
test_examples.py - Usage examples and demonstrations
```

## Installation

Simply place all Python files in your project directory. No external dependencies required!

## Quick Start

### Interactive Calculator

For an interactive experience similar to the TypeScript version, run:

```bash
python3 interactive_calculator.py
# or
python3 run_interactive.py
```

This provides a menu-driven interface where you can:
- Parse and evaluate expressions
- Compute derivatives
- Compute indefinite and definite integrals
- Simplify expressions
- Get variables from expressions
- Substitute values
- Run full workflows

### 1. Expression Evaluation

```python
from utils import evaluate

# Fully specified expression
result = evaluate("2*x + 3", {"x": 5})
print(result)  # 13.0

# Partially specified expression
result = evaluate("x^2 + y", {"x": 3})
print(result)  # '(9 + y)'

# With mathematical functions
result = evaluate("sin(0) + cos(0)")
print(result)  # 1.0
```

### 2. Derivatives

```python
from utils import derivative

# Simple polynomial
deriv = derivative("x^2", "x")
print(deriv)  # '(2 * x)'

# Trigonometric functions
deriv = derivative("sin(x)", "x")
print(deriv)  # 'cos(x)'

# Product rule
deriv = derivative("x * ln(x)", "x")
print(deriv)  # '((1 * ln(x)) + (x * (1 / x)))'
```

### 3. Indefinite Integrals

```python
from utils import indefinite_integral

# Power rule
integral = indefinite_integral("x^2", "x")
print(integral)  # '((x^3) / 3) + C)'

# Trigonometric
integral = indefinite_integral("sin(x)", "x")
print(integral)  # '((-1 * cos(x)) + C)'

# Logarithmic
integral = indefinite_integral("1/x", "x")
print(integral)  # '(ln(x) + C)'
```

### 4. Definite Integrals

```python
from utils import definite_integral

# Area under parabola
area = definite_integral("x^2", "x", 0, 1)
print(area)  # 0.3333...

# Sine wave integral
result = definite_integral("sin(x)", "x", 0, 3.14159)
print(result)  # 2.0
```

## Supported Operations

### Basic Operations
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Power: `^`

### Functions
- Trigonometric: `sin(x)`, `cos(x)`
- Logarithmic: `ln(x)`, `log(x)`
- Exponential: `exp(x)`

### Constants
- Numbers: `42`, `3.14`
- Variables: Any alphabetic string (`x`, `theta`, `var1`)

## Expression Syntax

```
# Basic expressions
"x + 2"
"3*x^2 - 2*x + 1"

# Parentheses for grouping
"(x + 1) * (x - 1)"
"2^(x + 3)"

# Functions
"sin(x) + cos(2*x)"
"ln(x^2 + 1)"
"exp(-x)"

# Nested expressions
"sin(cos(x))"
"ln(exp(x) + 1)"
```

## Integration Capabilities

The library can integrate:
- Polynomials: `x^n` → `x^(n+1)/(n+1)`
- Basic trigonometric: `sin(x)`, `cos(x)`
- Exponentials: `exp(x)`, `exp(ax)`
- Logarithmic: `1/x` → `ln(x)`
- Linear combinations of the above

For expressions it cannot integrate symbolically, definite integrals fall back to numerical integration using Simpson's rule.

## Limitations

1. **Integration**: Only basic integration rules are implemented. Complex techniques like integration by parts, trigonometric substitution, or partial fractions are not supported.

2. **Functions**: Limited to sin, cos, ln, and exp. No tan, arcsin, etc.

3. **Simplification**: Basic algebraic simplification only. Does not recognize all mathematical identities.

## Advanced Usage

### Getting Variables

```python
from utils import get_variables

vars = get_variables("x^2 + y*z + sin(theta)")
print(vars)  # ['theta', 'x', 'y', 'z']
```

### Simplification

```python
from utils import simplify

simple = simplify("x + 0")      # 'x'
simple = simplify("x * 1")      # 'x'
simple = simplify("x - x")      # '0'
```

### Substitution

```python
from utils import substitute

result = substitute("a*x^2 + b*x + c", {"a": 1, "b": -2, "c": 1})
print(result)  # '((1 * (x^2)) + ((-2) * x) + 1)'
```

## Examples

See `test_examples.py` for comprehensive examples including:
- Basic usage of all functions
- Physics applications (kinematics)
- Verification of mathematical properties
- Complex expression handling

## Interactive Calculator Usage

The interactive calculator provides an easy way to test the mathematical expression library:

```bash
$ python3 interactive_calculator.py

Welcome to the Opus 4 Mathematical Expression Calculator!
This calculator supports parsing, evaluation, differentiation, and integration.

=== Expression Examples ===
Basic arithmetic: 2*x + 3, x^2 + 3*x + 1
Trigonometric: sin(x), cos(x), tan(x)
Logarithmic: ln(x), log(x) (base 10)
Exponential: exp(x), e^x
Mixed: x^2 + sin(x) + ln(x)
Complex: (x + 1) * (x - 1), sin(x)^2 + cos(x)^2

=== Mathematical Expression Calculator (Opus 4) ===
1. Parse and evaluate expression
2. Differentiate expression
3. Integrate indefinite
4. Integrate definite
5. Simplify expression
6. Get variables from expression
7. Substitute values in expression
8. Full workflow (evaluate → differentiate → integrate)
9. Show examples
0. Exit
======================================================
Choose an option (0-9): 
```

Example session:
```
Choose an option (0-9): 1
Enter a mathematical expression: x^2 + 3*x + 1
Found variables: x
Enter value for "x": 2
✓ Result: 11.0
With values: x=2

Choose an option (0-9): 2
Enter expression (or press Enter to use last): 
Using last expression: "x^2 + 3*x + 1"
Enter variable to differentiate with respect to (e.g., x): x
✓ Original: x^2 + 3*x + 1
✓ Derivative d/dx: ((2 * x) + 3)
```

## Error Handling

All functions raise `ValueError` with descriptive messages when:
- Expression syntax is invalid
- Division by zero occurs
- Integration is not possible
- Variables are undefined for numerical evaluation

## Implementation Details

The library uses:
- **Recursive descent parser** for expression parsing
- **Abstract Syntax Tree (AST)** for expression representation
- **Visitor pattern** for operations on expressions
- **Symbolic manipulation** for derivatives and integrals
- **Simpson's rule** for numerical integration fallback