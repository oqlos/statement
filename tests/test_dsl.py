"""Tests for DSL functionality."""

import pytest
import tempfile
from pathlib import Path

from sumd.dsl.parser import (
    DSLLexer,
    DSLParser,
    DSLExpression,
    DSLExpressionType,
    parse_dsl,
)
from sumd.dsl.engine import DSLEngine, DSLContext
from sumd.dsl.commands import DSLCommandRegistry, create_builtin_registry
from sumd.dsl.shell import DSLShell


class TestDSLLexer:
    """Test DSL lexer functionality."""
    
    def test_tokenize_simple_command(self):
        """Test tokenizing a simple command."""
        lexer = DSLLexer("scan .")
        tokens = lexer.tokenize()
        
        # Check tokens
        assert len(tokens) == 3  # scan, ., EOF
        assert tokens[0].type.value == "IDENTIFIER"
        assert tokens[0].value == "scan"
        assert tokens[1].type.value == "DOT"
        assert tokens[1].value == "."
        assert tokens[2].type.value == "EOF"
    
    def test_tokenize_function_call(self):
        """Test tokenizing a function call."""
        lexer = DSLLexer("len('test')")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 5  # len, (, 'test', ), EOF
        assert tokens[0].value == "len"
        assert tokens[1].value == "("
        assert tokens[2].value == "'test'"
        assert tokens[3].value == ")"
    
    def test_tokenize_arithmetic(self):
        """Test tokenizing arithmetic expression."""
        lexer = DSLLexer("1 + 2 * 3")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 6  # 1, +, 2, *, 3, EOF
        assert tokens[0].value == "1"
        assert tokens[1].value == "+"
        assert tokens[2].value == "2"
        assert tokens[3].value == "*"
        assert tokens[4].value == "3"
    
    def test_tokenize_string_literals(self):
        """Test tokenizing string literals."""
        lexer = DSLLexer('"hello world" \'test\'')
        tokens = lexer.tokenize()
        
        assert len(tokens) == 3  # "hello world", 'test', EOF
        assert tokens[0].value == '"hello world"'
        assert tokens[1].value == "'test'"
    
    def test_tokenize_comments(self):
        """Test tokenizing comments."""
        lexer = DSLLexer("scan . # comment")
        tokens = lexer.tokenize()
        
        assert len(tokens) == 3  # scan, ., EOF (comment skipped)
        assert tokens[0].value == "scan"
        assert tokens[1].value == "."


class TestDSLParser:
    """Test DSL parser functionality."""
    
    def test_parse_simple_command(self):
        """Test parsing a simple command."""
        expression = parse_dsl("scan .")
        
        assert expression.type == DSLExpressionType.COMMAND
        assert expression.value == "scan"
        assert len(expression.children) == 1
        assert expression.children[0].value == "."
    
    def test_parse_function_call(self):
        """Test parsing a function call."""
        expression = parse_dsl("len('test')")
        
        assert expression.type == DSLExpressionType.FUNCTION_CALL
        assert expression.value == "len"
        assert len(expression.children) == 1
        assert expression.children[0].type == DSLExpressionType.LITERAL
        assert expression.children[0].value == "test"
    
    def test_parse_arithmetic(self):
        """Test parsing arithmetic expression."""
        expression = parse_dsl("1 + 2 * 3")
        
        assert expression.type == DSLExpressionType.ARITHMETIC
        assert expression.value == "+"
        assert len(expression.children) == 2
        assert expression.children[0].value == 1
        assert expression.children[1].type == DSLExpressionType.ARITHMETIC
        assert expression.children[1].value == "*"
    
    def test_parse_assignment(self):
        """Test parsing assignment."""
        expression = parse_dsl("x = 42")
        
        assert expression.type == DSLExpressionType.ASSIGNMENT
        assert expression.value == "="
        assert len(expression.children) == 2
        assert expression.children[0].value == "x"
        assert expression.children[1].value == 42
    
    def test_parse_pipeline(self):
        """Test parsing pipeline."""
        expression = parse_dsl("scan . | validate .")
        
        assert expression.type == DSLExpressionType.PIPELINE
        assert len(expression.children) == 2
        assert expression.children[0].value == "scan"
        assert expression.children[1].value == "validate"
    
    def test_parse_comparison(self):
        """Test parsing comparison."""
        expression = parse_dsl("x == 42")
        
        assert expression.type == DSLExpressionType.COMPARISON
        assert expression.value == "=="
        assert len(expression.children) == 2
        assert expression.children[0].value == "x"
        assert expression.children[1].value == 42
    
    def test_parse_logical(self):
        """Test parsing logical expression."""
        expression = parse_dsl("x and y")
        
        assert expression.type == DSLExpressionType.LOGICAL
        assert expression.value == "and"
        assert len(expression.children) == 2
        assert expression.children[0].value == "x"
        assert expression.children[1].value == "y"


class TestDSLEngine:
    """Test DSL engine functionality."""
    
    @pytest.mark.asyncio
    async def test_execute_literal(self):
        """Test executing literal expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test string literal
        expression = parse_dsl("'hello'")
        result = await engine.execute(expression, context)
        assert result == "hello"
        
        # Test number literal
        expression = parse_dsl("42")
        result = await engine.execute(expression, context)
        assert result == 42
        
        # Test boolean literal
        expression = parse_dsl("true")
        result = await engine.execute(expression, context)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_execute_arithmetic(self):
        """Test executing arithmetic expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test addition
        expression = parse_dsl("1 + 2")
        result = await engine.execute(expression, context)
        assert result == 3
        
        # Test multiplication
        expression = parse_dsl("2 * 3")
        result = await engine.execute(expression, context)
        assert result == 6
        
        # Test precedence
        expression = parse_dsl("1 + 2 * 3")
        result = await engine.execute(expression, context)
        assert result == 7
    
    @pytest.mark.asyncio
    async def test_execute_comparison(self):
        """Test executing comparison expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test equality
        expression = parse_dsl("1 == 1")
        result = await engine.execute(expression, context)
        assert result is True
        
        # Test inequality
        expression = parse_dsl("1 != 2")
        result = await engine.execute(expression, context)
        assert result is True
        
        # Test contains
        expression = parse_dsl("'hello' contains 'ell'")
        result = await engine.execute(expression, context)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_execute_logical(self):
        """Test executing logical expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test AND
        expression = parse_dsl("true and false")
        result = await engine.execute(expression, context)
        assert result is False
        
        # Test OR
        expression = parse_dsl("true or false")
        result = await engine.execute(expression, context)
        assert result is True
        
        # Test NOT
        expression = parse_dsl("not true")
        result = await engine.execute(expression, context)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_assignment(self):
        """Test executing assignment expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        expression = parse_dsl("x = 42")
        result = await engine.execute(expression, context)
        assert result == 42
        assert context.get_variable("x") == 42
    
    @pytest.mark.asyncio
    async def test_execute_function_call(self):
        """Test executing function calls."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test built-in function
        expression = parse_dsl("len('test')")
        result = await engine.execute(expression, context)
        assert result == 4
        
        # Test string conversion
        expression = parse_dsl("str(42)")
        result = await engine.execute(expression, context)
        assert result == "42"
    
    @pytest.mark.asyncio
    async def test_execute_pipeline(self):
        """Test executing pipeline expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Simple pipeline
        expression = parse_dsl("42 | str")
        result = await engine.execute(expression, context)
        assert result == "42"
        
        # Check pipeline variable
        assert context.get_variable("_") == "42"


class TestDSLCommandRegistry:
    """Test DSL command registry."""
    
    def test_builtin_registry(self):
        """Test built-in command registry."""
        registry = create_builtin_registry()
        
        # Check that commands are registered
        commands = registry.list_commands()
        assert len(commands) > 0
        
        # Check specific commands
        cat_cmd = registry.get_command("cat")
        assert cat_cmd is not None
        assert cat_cmd.name == "cat"
        assert cat_cmd.category == "files"
        
        # Check aliases
        type_cmd = registry.get_command("type")
        assert type_cmd is not None
        assert type_cmd.name == "cat"  # Should resolve to cat command
    
    def test_command_categories(self):
        """Test command categories."""
        registry = create_builtin_registry()
        
        categories = registry.list_categories()
        assert "files" in categories
        assert "sumd" in categories
        assert "utility" in categories
        
        # Check commands in category
        file_commands = registry.list_commands("files")
        assert any(cmd.name == "cat" for cmd in file_commands)
    
    def test_help_system(self):
        """Test help system."""
        registry = create_builtin_registry()
        
        # General help
        help_text = registry.get_help()
        assert "cat" in help_text
        assert "scan" in help_text
        
        # Specific command help
        cat_help = registry.get_help("cat")
        assert "cat" in cat_help
        assert "Display file contents" in cat_help


class TestDSLShell:
    """Test DSL shell functionality."""
    
    @pytest.mark.asyncio
    async def test_shell_initialization(self):
        """Test shell initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            working_dir = Path(tmp_dir)
            shell = DSLShell(working_directory=working_dir)
            
            assert shell.working_directory == working_dir
            assert shell.context.working_directory == working_dir
            assert shell.running is True
    
    @pytest.mark.asyncio
    async def test_execute_command(self):
        """Test executing commands in shell."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            working_dir = Path(tmp_dir)
            shell = DSLShell(working_directory=working_dir)
            
            # Test simple command
            result = await shell.execute_command("echo 'hello'")
            assert result == "hello"
            
            # Test arithmetic
            result = await shell.execute_command("1 + 2")
            assert result == 3
            
            # Test assignment
            result = await shell.execute_command("x = 42")
            assert result == 42
            assert shell.context.get_variable("x") == 42
    
    @pytest.mark.asyncio
    async def test_execute_script(self):
        """Test executing DSL script."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            working_dir = Path(tmp_dir)
            shell = DSLShell(working_directory=working_dir)
            
            # Create test script
            script_file = working_dir / "test.dsl"
            script_content = """
# Test script
x = 42
y = x + 8
echo "Result: {y}"
"""
            script_file.write_text(script_content)
            
            # Execute script
            await shell.execute_script(script_file)
            
            # Check variables
            assert shell.context.get_variable("x") == 42
            assert shell.context.get_variable("y") == 50


class TestDSLIntegration:
    """Integration tests for DSL functionality."""
    
    @pytest.mark.asyncio
    async def test_dsl_with_sumd_commands(self):
        """Test DSL with SUMD commands."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            working_dir = Path(tmp_dir)
            
            # Create a simple project structure
            pyproject_content = """
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
"""
            (working_dir / "pyproject.toml").write_text(pyproject_content)
            
            # Initialize shell
            shell = DSLShell(working_directory=working_dir)
            
            # Test SUMD commands
            result = await shell.execute_command("pwd")
            assert str(working_dir) in result
            
            # Test file operations
            (working_dir / "test.txt").write_text("test content")
            result = await shell.execute_command("exists('test.txt')")
            assert result is True
            
            result = await shell.execute_command("read_file('test.txt')")
            assert "test content" in result
    
    @pytest.mark.asyncio
    async def test_complex_dsl_expressions(self):
        """Test complex DSL expressions."""
        engine = DSLEngine()
        context = DSLContext()
        
        # Test complex arithmetic
        expression = parse_dsl("(1 + 2) * (3 + 4)")
        result = await engine.execute(expression, context)
        assert result == 21
        
        # Test complex logical
        expression = parse_dsl("true and (false or true)")
        result = await engine.execute(expression, context)
        assert result is True
        
        # Test nested function calls
        expression = parse_dsl("str(len('hello world'))")
        result = await engine.execute(expression, context)
        assert result == "11"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in DSL."""
        engine = DSLEngine()
        context = DSLContext(working_directory=Path.cwd())
        
        # Test division by zero
        with pytest.raises(ZeroDivisionError):
            expression = parse_dsl("1 / 0")
            await engine.execute(expression, context)
        
        # Test undefined variable
        expression = parse_dsl("undefined_var")
        result = await engine.execute(expression, context)
        assert result == "undefined_var"  # Returns variable name as fallback
        
        # Test unknown function
        with pytest.raises(ValueError):
            expression = parse_dsl("unknown_function()")
            await engine.execute(expression, context)


if __name__ == "__main__":
    pytest.main([__file__])
