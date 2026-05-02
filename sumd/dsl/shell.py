"""DSL Shell for interactive SUMD DSL execution."""

from __future__ import annotations

import asyncio
import readline
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .engine import DSLEngine, DSLContext
from .parser import parse_dsl
from .commands import DSLCommandRegistry, create_builtin_registry


class DSLShell:
    """Interactive shell for SUMD DSL."""
    
    def __init__(
        self,
        engine: Optional[DSLEngine] = None,
        command_registry: Optional[DSLCommandRegistry] = None,
        working_directory: Optional[Path] = None,
    ):
        self.engine = engine or DSLEngine()
        self.command_registry = command_registry or create_builtin_registry()
        self.working_directory = working_directory or Path.cwd()
        self.context = DSLContext(self.working_directory)
        self.history: List[str] = []
        self.running = True
        
        # Setup readline for better input handling
        self._setup_readline()
        
        # Register command functions in context
        self._register_commands()
    
    def _setup_readline(self) -> None:
        """Setup readline for command history and completion."""
        try:
            # Load history
            history_file = Path.home() / ".sumd_dsl_history"
            if history_file.exists():
                readline.read_history_file(history_file)
            
            # Set history length
            readline.set_history_length(1000)
            
            # Setup tab completion
            readline.set_completer(self._completer)
            readline.parse_and_bind("tab: complete")
            
            self.history_file = history_file
        except Exception:
            # Readline not available (Windows, etc.)
            self.history_file = None
    
    def _completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for DSL commands."""
        options = []
        
        # Complete command names
        for command in self.command_registry.list_commands():
            if command.name.startswith(text):
                options.append(command.name)
            for alias in command.aliases:
                if alias.startswith(text):
                    options.append(alias)
        
        # Complete variable names
        for var_name in self.context.variables.keys():
            if var_name.startswith(text):
                options.append(var_name)
        
        # Complete built-in functions
        for func_name in self.engine.built_in_functions.keys():
            if func_name.startswith(text):
                options.append(func_name)
        
        if state < len(options):
            return options[state]
        return None
    
    def _register_commands(self) -> None:
        """Register command functions in the DSL context."""
        for command in self.command_registry.list_commands():
            self.context.register_function(command.name, command.function)
            for alias in command.aliases:
                self.context.register_function(alias, command.function)
    
    async def run(self) -> None:
        """Run the interactive shell."""
        print(f"SUMD DSL Shell v1.0")
        print(f"Working directory: {self.working_directory}")
        print(f"Type 'help' for available commands or 'exit' to quit.")
        print()
        
        try:
            while self.running:
                try:
                    # Get input
                    prompt = self._get_prompt()
                    line = input(prompt).strip()
                    
                    if not line:
                        continue
                    
                    # Handle shell commands
                    if line.startswith("!"):
                        await self._handle_shell_command(line[1:])
                        continue
                    
                    # Handle DSL commands
                    await self._execute_line(line)
                    
                except KeyboardInterrupt:
                    print("^C")
                    continue
                except EOFError:
                    print()
                    break
                except Exception as e:
                    print(f"Error: {e}")
        
        finally:
            # Save history
            if self.history_file:
                try:
                    readline.write_history_file(self.history_file)
                except Exception:
                    pass
            
            print("Goodbye!")
    
    def _get_prompt(self) -> str:
        """Get the current prompt."""
        return f"sumd:{self.working_directory.name}> "
    
    async def _handle_shell_command(self, command: str) -> None:
        """Handle shell commands (prefixed with !)."""
        command = command.strip()
        
        if command in ["exit", "quit"]:
            self.running = False
        elif command == "clear":
            import os
            os.system("clear" if os.name != "nt" else "cls")
        elif command == "help":
            print("Shell Commands:")
            print("  !exit, !quit  - Exit the shell")
            print("  !clear        - Clear the screen")
            print("  !help         - Show this help")
            print()
            print("Use 'help' for DSL commands.")
        elif command.startswith("cd "):
            path = command[3:].strip()
            try:
                new_path = self.working_directory / path
                if new_path.is_dir():
                    self.working_directory = new_path.resolve()
                    self.context.working_directory = self.working_directory
                    print(f"Changed to: {self.working_directory}")
                else:
                    print(f"Directory not found: {path}")
            except Exception as e:
                print(f"Error: {e}")
        elif command == "pwd":
            print(self.working_directory)
        elif command == "vars":
            if self.context.variables:
                print("Variables:")
                for name, value in self.context.variables.items():
                    print(f"  {name} = {value}")
            else:
                print("No variables set.")
        elif command == "history":
            for i, line in enumerate(self.history[-10:], 1):
                print(f"  {i}: {line}")
        else:
            print(f"Unknown shell command: {command}")
            print("Type !help for available shell commands.")
    
    async def _execute_line(self, line: str) -> None:
        """Execute a DSL line."""
        # Add to history
        self.history.append(line)
        
        try:
            # Parse and execute
            expression = parse_dsl(line)
            result = await self.engine.execute(expression, self.context)
            
            # Display result
            if result is not None:
                if isinstance(result, list):
                    if result:
                        for item in result:
                            print(f"  {item}")
                    else:
                        print("  (empty list)")
                elif isinstance(result, dict):
                    if result:
                        for key, value in result.items():
                            print(f"  {key}: {value}")
                    else:
                        print("  (empty dict)")
                else:
                    print(f"  {result}")
        
        except Exception as e:
            print(f"Error: {e}")
    
    async def execute_script(self, script_path: Path) -> None:
        """Execute a DSL script file."""
        if not script_path.exists():
            raise ValueError(f"Script not found: {script_path}")
        
        print(f"Executing script: {script_path}")
        
        try:
            content = script_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                
                print(f"{line_num}: {line}")
                
                try:
                    expression = parse_dsl(line)
                    result = await self.engine.execute(expression, self.context)
                    
                    if result is not None:
                        if isinstance(result, (list, dict)):
                            print(f"  Result: {len(result)} items")
                        else:
                            print(f"  Result: {result}")
                
                except Exception as e:
                    print(f"  Error on line {line_num}: {e}")
                    break
        
        except Exception as e:
            print(f"Error reading script: {e}")
    
    async def execute_command(self, command: str) -> Any:
        """Execute a single DSL command."""
        try:
            expression = parse_dsl(command)
            return await self.engine.execute(expression, self.context)
        except Exception as e:
            raise ValueError(f"Command execution failed: {e}")


class DSLShellServer:
    """Server for DSL shell operations (for MCP integration)."""
    
    def __init__(self, working_directory: Optional[Path] = None):
        self.working_directory = working_directory or Path.cwd()
        self.shell = DSLShell(working_directory=self.working_directory)
    
    async def execute_dsl(self, dsl_expression: str, context_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute DSL expression and return result."""
        try:
            # Set context variables
            if context_vars:
                for name, value in context_vars.items():
                    self.shell.context.set_variable(name, value)
            
            # Parse and execute
            expression = parse_dsl(dsl_expression)
            result = await self.shell.engine.execute(expression, self.shell.context)
            
            return {
                "success": True,
                "result": result,
                "working_directory": str(self.shell.working_directory),
                "variables": self.shell.context.variables,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "working_directory": str(self.shell.working_directory),
                "variables": self.shell.context.variables,
            }
    
    async def get_shell_info(self) -> Dict[str, Any]:
        """Get shell information."""
        return {
            "working_directory": str(self.shell.working_directory),
            "variables": self.shell.context.variables,
            "available_commands": [
                {
                    "name": cmd.name,
                    "description": cmd.description,
                    "usage": cmd.usage,
                    "aliases": cmd.aliases,
                    "category": cmd.category,
                }
                for cmd in self.shell.command_registry.list_commands()
            ],
            "available_functions": list(self.shell.engine.built_in_functions.keys()),
        }


# CLI entry point
async def main() -> None:
    """Main entry point for DSL shell."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SUMD DSL Shell")
    parser.add_argument("script", nargs="?", help="DSL script to execute")
    parser.add_argument("--directory", "-d", help="Working directory")
    parser.add_argument("--command", "-c", help="Execute single command")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactively after script")
    
    args = parser.parse_args()
    
    # Setup working directory
    working_directory = Path(args.directory) if args.directory else Path.cwd()
    if not working_directory.exists():
        print(f"Error: Directory not found: {working_directory}")
        sys.exit(1)
    
    # Create shell
    shell = DSLShell(working_directory=working_directory)
    
    try:
        if args.command:
            # Execute single command
            result = await shell.execute_command(args.command)
            if result is not None:
                print(result)
        
        elif args.script:
            # Execute script
            script_path = Path(args.script)
            await shell.execute_script(script_path)
        
        if args.interactive or not (args.command or args.script):
            # Run interactive shell
            await shell.run()
    
    except KeyboardInterrupt:
        print()
        print("Interrupted.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
