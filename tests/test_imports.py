#!/usr/bin/env python3
"""
Basic test to verify that the formatter modules can be parsed
and have correct syntax.
"""
import ast
import os


def test_syntax(filename):
    """Test that a Python file has valid syntax."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r') as f:
        source = f.read()

    try:
        ast.parse(source, filename=filename)
        print(f"✓ {filename} syntax check passed")
        return True
    except SyntaxError as e:
        print(f"✗ {filename} syntax error: {e}")
        return False


def test_required_functions_and_classes(filename, expected_names):
    """Test that a Python file contains expected function/class names."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r') as f:
        source = f.read()

    tree = ast.parse(source, filename=filename)

    # Extract all top-level function and class names
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)

    missing = set(expected_names) - names
    if missing:
        print(f"✗ {filename} missing expected names: {missing}")
        return False
    else:
        print(f"✓ {filename} contains all expected names: {expected_names}")
        return True


def test_boost_formatter():
    """Test boost_formatter syntax and structure."""
    expected_names = ['dereferenced_type', 'BoostSmallVectorProvider',
                      '__lldb_init_module']
    return (test_syntax('boost_formatter.py') and
            test_required_functions_and_classes('boost_formatter.py',
                                                expected_names))


def test_eigen_formatter():
    """Test eigen_formatter syntax and structure."""
    expected_names = ['dereferenced_type', 'EigenMatrixProvider',
                      'EigenArrayProvider', '__lldb_init_module']
    return (test_syntax('eigen_formatter.py') and
            test_required_functions_and_classes('eigen_formatter.py',
                                                expected_names))


if __name__ == '__main__':
    success = True
    success &= test_boost_formatter()
    success &= test_eigen_formatter()

    if success:
        print("✓ All syntax and structure tests passed!")
    else:
        print("✗ Some tests failed!")
        exit(1)
