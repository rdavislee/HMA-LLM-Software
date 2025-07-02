"""
Unit tests for the mathematical expression utilities.
"""
import unittest
import math
from utils import (
    evaluate, derivative, indefinite_integral, definite_integral,
    simplify, get_variables, substitute
)


class TestEvaluate(unittest.TestCase):
    """Test expression evaluation."""
    
    def test_basic_arithmetic(self):
        self.assertEqual(evaluate("2 + 3"), 5.0)
        self.assertEqual(evaluate("10 - 4"), 6.0)
        self.assertEqual(evaluate("3 * 4"), 12.0)
        self.assertEqual(evaluate("15 / 3"), 5.0)
        self.assertEqual(evaluate("2^3"), 8.0)
    
    def test_with_variables(self):
        self.assertEqual(evaluate("x + 5", {"x": 3}), 8.0)
        self.assertEqual(evaluate("2*x + y", {"x": 3, "y": 4}), 10.0)
        self.assertEqual(evaluate("x^2", {"x": 4}), 16.0)
    
    def test_partial_evaluation(self):
        result = evaluate("x + y", {"x": 5})
        self.assertEqual(result, "(5 + y)")
        
        result = evaluate("x^2 + y^2", {"x": 3})
        self.assertEqual(result, "(9 + (y^2))")
    
    def test_functions(self):
        self.assertAlmostEqual(evaluate("sin(0)"), 0.0)
        self.assertAlmostEqual(evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(evaluate("exp(0)"), 1.0)
        self.assertAlmostEqual(evaluate("ln(1)"), 0.0)
    
    def test_complex_expressions(self):
        result = evaluate("(x + 1) * (x - 1)", {"x": 5})
        self.assertEqual(result, 24.0)  # 6 * 4
        
        result = evaluate("sin(x)^2 + cos(x)^2", {"x": 0.5})
        self.assertAlmostEqual(result, 1.0, places=10)


class TestDerivative(unittest.TestCase):
    """Test symbolic differentiation."""
    
    def test_constants(self):
        self.assertEqual(derivative("5", "x"), "0")
        self.assertEqual(derivative("3.14", "x"), "0")
    
    def test_variables(self):
        self.assertEqual(derivative("x", "x"), "1")
        self.assertEqual(derivative("y", "x"), "0")
    
    def test_power_rule(self):
        self.assertEqual(derivative("x^2", "x"), "(2 * x)")
        self.assertEqual(derivative("x^3", "x"), "(3 * (x^2))")
        self.assertEqual(derivative("x^0", "x"), "0")
        self.assertEqual(derivative("x^1", "x"), "1")
    
    def test_sum_difference(self):
        deriv = derivative("x + y", "x")
        self.assertEqual(deriv, "(1 + 0)")
        
        deriv = derivative("x^2 + 3*x + 2", "x")
        # Should simplify to something like ((2 * x) + 3)
        self.assertIn("2", deriv)
        self.assertIn("x", deriv)
        self.assertIn("3", deriv)
    
    def test_product_rule(self):
        # d/dx(x * x) = 2x
        deriv = derivative("x * x", "x")
        result = evaluate(deriv, {"x": 5})
        self.assertEqual(result, 10.0)  # 2 * 5
    
    def test_quotient_rule(self):
        # d/dx(1/x) = -1/x^2
        deriv = derivative("1/x", "x")
        result = evaluate(deriv, {"x": 2})
        self.assertEqual(result, -0.25)  # -1/4
    
    def test_trig_functions(self):
        self.assertEqual(derivative("sin(x)", "x"), "cos(x)")
        self.assertEqual(derivative("cos(x)", "x"), "(-1 * sin(x))")
    
    def test_exponential_logarithm(self):
        self.assertEqual(derivative("exp(x)", "x"), "exp(x)")
        self.assertEqual(derivative("ln(x)", "x"), "(1 / x)")


class TestIndefiniteIntegral(unittest.TestCase):
    """Test indefinite integration."""
    
    def test_constants(self):
        integral = indefinite_integral("5", "x")
        self.assertIn("5", integral)
        self.assertIn("x", integral)
        self.assertIn("C", integral)
    
    def test_power_rule(self):
        integral = indefinite_integral("x", "x")
        self.assertIn("x^2", integral.replace(" ", ""))
        self.assertIn("/2", integral.replace(" ", ""))
        self.assertIn("C", integral)
        
        integral = indefinite_integral("x^2", "x")
        self.assertIn("x^3", integral.replace(" ", ""))
        self.assertIn("/3", integral.replace(" ", ""))
        self.assertIn("C", integral)
    
    def test_trig_functions(self):
        integral = indefinite_integral("sin(x)", "x")
        self.assertIn("cos(x)", integral)
        self.assertIn("-1", integral)
        self.assertIn("C", integral)
        
        integral = indefinite_integral("cos(x)", "x")
        self.assertIn("sin(x)", integral)
        self.assertIn("C", integral)
    
    def test_exponential(self):
        integral = indefinite_integral("exp(x)", "x")
        self.assertIn("exp(x)", integral)
        self.assertIn("C", integral)
    
    def test_logarithmic(self):
        integral = indefinite_integral("1/x", "x")
        self.assertIn("ln(x)", integral)
        self.assertIn("C", integral)


class TestDefiniteIntegral(unittest.TestCase):
    """Test definite integration."""
    
    def test_constant(self):
        result = definite_integral("1", "x", 0, 5)
        self.assertEqual(result, 5.0)
    
    def test_linear(self):
        result = definite_integral("x", "x", 0, 2)
        self.assertEqual(result, 2.0)  # x^2/2 from 0 to 2 = 4/2 = 2
    
    def test_quadratic(self):
        result = definite_integral("x^2", "x", 0, 1)
        self.assertAlmostEqual(result, 1/3, places=5)
    
    def test_trig(self):
        # ∫[0,π] sin(x) dx = 2
        result = definite_integral("sin(x)", "x", 0, math.pi)
        self.assertAlmostEqual(result, 2.0, places=5)
        
        # ∫[0,π/2] cos(x) dx = 1
        result = definite_integral("cos(x)", "x", 0, math.pi/2)
        self.assertAlmostEqual(result, 1.0, places=5)
    
    def test_exponential(self):
        # ∫[0,1] e^x dx = e - 1
        result = definite_integral("exp(x)", "x", 0, 1)
        self.assertAlmostEqual(result, math.e - 1, places=5)


class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_variables(self):
        vars = get_variables("x + y + z")
        self.assertEqual(sorted(vars), ["x", "y", "z"])
        
        vars = get_variables("x^2 + sin(theta)")
        self.assertEqual(sorted(vars), ["theta", "x"])
        
        vars = get_variables("5 + 3.14")
        self.assertEqual(vars, [])
    
    def test_simplify(self):
        self.assertEqual(simplify("x + 0"), "x")
        self.assertEqual(simplify("x * 1"), "x")
        self.assertEqual(simplify("0 * x"), "0")
        self.assertEqual(simplify("x - x"), "0")
        self.assertEqual(simplify("x^0"), "1")
        self.assertEqual(simplify("x^1"), "x")
    
    def test_substitute(self):
        result = substitute("x + y", {"x": 5})
        self.assertEqual(result, "(5 + y)")
        
        result = substitute("a*x + b", {"a": 2, "b": 3})
        self.assertEqual(result, "((2 * x) + 3)")
        
        result = substitute("x^2 + x + 1", {"x": 2})
        self.assertEqual(result, "7.0")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            evaluate("1/0")
        
        with self.assertRaises(ValueError):
            evaluate("1/x", {"x": 0})
    
    def test_invalid_logarithm(self):
        with self.assertRaises(ValueError):
            evaluate("ln(0)")
        
        with self.assertRaises(ValueError):
            evaluate("ln(-1)")
    
    def test_invalid_syntax(self):
        with self.assertRaises(ValueError):
            evaluate("x +")
        
        with self.assertRaises(ValueError):
            evaluate("(x + 2")
        
        with self.assertRaises(ValueError):
            evaluate("sin()")
    
    def test_undefined_function(self):
        with self.assertRaises(ValueError):
            evaluate("tan(x)")
        
        with self.assertRaises(ValueError):
            evaluate("sqrt(x)")


if __name__ == "__main__":
    unittest.main()