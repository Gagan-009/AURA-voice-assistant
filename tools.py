"""AURA Tools Module

Provides safe, local client-side tool implementations for AURA:
1. get_current_time: Returns the current local date, time, and timezone.
2. calculate: Safely evaluates arithmetic expressions using an AST visitor without eval().
"""

import ast
import operator
import re
from datetime import datetime
from typing import Any, Dict, Optional, Union

from elevenlabs.conversational_ai.conversation import ClientTools

# Mapping of allowed AST binary/unary operators to Python functions
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

MAX_EXPONENT = 1000  # Guard against denial-of-service via massive power operations


def get_current_time(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Returns the current local date and time in a human-readable format.

    Uses the host machine's local timezone.
    """
    now = datetime.now().astimezone()
    formatted = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    return f"The current local date and time is {formatted}."


def _evaluate_ast_node(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate an AST node strictly restricted to numeric arithmetic.

    Raises ValueError or ZeroDivisionError if invalid or unsafe operations are
    encountered.
    """
    if isinstance(node, ast.Expression):
        return _evaluate_ast_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _ALLOWED_OPERATORS:
            operand = _evaluate_ast_node(node.operand)
            return _ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _ALLOWED_OPERATORS:
            left = _evaluate_ast_node(node.left)
            right = _evaluate_ast_node(node.right)

            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division or modulo by zero is not allowed.")

            if op_type == ast.Pow:
                if isinstance(right, (int, float)) and right > MAX_EXPONENT:
                    raise ValueError(f"Exponent exceeds safe limit of {MAX_EXPONENT}.")

            result = _ALLOWED_OPERATORS[op_type](left, right)
            return result

        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

    raise ValueError(f"Disallowed expression syntax: {type(node).__name__}")


def calculate(expression: str) -> str:
    """Safely evaluates a mathematical expression without using unrestricted eval().

    Supports +, -, *, /, //, %, powers (^ or **), parentheses, and decimals.
    """
    if not expression or not isinstance(expression, str):
        return "Error: Please provide a valid mathematical expression."

    clean_expr = expression.strip()

    # Normalize caret (^) to Python power operator (**)
    clean_expr = re.sub(r"\^", "**", clean_expr)

    try:
        # Parse expression into an AST (mode='eval' enforces single expression)
        tree = ast.parse(clean_expr, mode="eval")
        result = _evaluate_ast_node(tree)

        # Format integer results cleanly without trailing '.0'
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return f"The result of {expression} is {result}."
    except ZeroDivisionError as e:
        return f"Error: {str(e)}"
    except (ValueError, SyntaxError) as e:
        return f"Error: Unable to evaluate expression '{expression}'. {str(e)}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def handle_get_current_time(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Handler wrapper for ElevenLabs ClientTools integration."""
    print("\n[Tool Executing]: get_current_time()", flush=True)
    res = get_current_time(parameters)
    print(f"[Tool Result]: {res}", flush=True)
    return res


def handle_calculate(parameters: Optional[Dict[str, Any]] = None) -> str:
    """Handler wrapper for ElevenLabs ClientTools integration."""
    parameters = parameters or {}
    expr = parameters.get("expression", "")
    print(f"\n[Tool Executing]: calculate(expression='{expr}')", flush=True)
    res = calculate(expr)
    print(f"[Tool Result]: {res}", flush=True)
    return res


def create_client_tools() -> ClientTools:
    """Factory function to initialize and register all AURA client tools."""
    client_tools = ClientTools()
    client_tools.register("get_current_time", handle_get_current_time)
    client_tools.register("calculate", handle_calculate)
    client_tools.start()
    return client_tools
