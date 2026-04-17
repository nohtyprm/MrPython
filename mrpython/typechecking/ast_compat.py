"""Compatibility helpers for AST differences across Python versions."""

import ast


def normalize_index_slice(slice_node):
    """Normalize Subscript slice between pre-3.9 Index wrapper and newer AST."""
    index_node = getattr(ast, "Index", None)
    if index_node is not None and isinstance(slice_node, index_node):
        return slice_node.value
    return slice_node


def as_str_literal(node):
    """Return string value for AST string literals across Python versions."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    # Fallback for pre-3.9 Python versions
    str_node = getattr(ast, "Str", None)
    if str_node is not None and isinstance(node, str_node):
        return node.s

    return None
