"""Schema-based DSL commands with NLP integration."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time

from .schema import (
    DSLCommandSchema,
    DSLCommandType,
    DSLActionType,
    DSLDataType,
    DSLProjectSchema,
    DSLCommandResult,
    DSLContext,
)
from .nlp import NLPIntegration, SimpleNLPModel


class SchemaCommandRegistry:
    """Registry for schema-based DSL commands."""
    
    def __init__(self, project_schema: DSLProjectSchema):
        """Initialize command registry with project schema."""
        self.project_schema = project_schema
        self.commands: Dict[str, DSLCommandSchema] = {}
        self.aliases: Dict[str, str] = {}
        self.nlp_integration = NLPIntegration(project_schema)
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands from project schema."""
        for command in self.project_schema.commands:
            self.commands[command.name] = command
            for alias in command.aliases:
                self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> Optional[DSLCommandSchema]:
        """Get command schema by name or alias."""
        if name in self.commands:
            return self.commands[name]
        elif name in self.aliases:
            return self.commands[self.aliases[name]]
        return None
    
    def list_commands(self, command_type: Optional[DSLCommandType] = None) -> List[DSLCommandSchema]:
        """List commands, optionally filtered by type."""
        commands = list(self.commands.values())
        if command_type:
            commands = [cmd for cmd in commands if cmd.command_type == command_type]
        return commands
    
    def validate_command_call(self, command_name: str, args: Dict[str, Any]) -> DSLCommandResult:
        """Validate command call against schema."""
        command = self.get_command(command_name)
        if not command:
            return DSLCommandResult(
                success=False,
                error=f"Unknown command: {command_name}",
                execution_time=0.0,
            )
        
        # Validate required parameters
        for param in command.parameters:
            if param.required and param.name not in args:
                return DSLCommandResult(
                    success=False,
                    error=f"Missing required parameter: {param.name}",
                    execution_time=0.0,
                )
        
        # Validate parameter types
        for param in command.parameters:
            if param.name in args:
                value = args[param.name]
                if not self._validate_parameter_type(value, param.data_type):
                    return DSLCommandResult(
                        success=False,
                        error=f"Invalid type for parameter {param.name}: expected {param.data_type}",
                        execution_time=0.0,
                    )
        
        return DSLCommandResult(success=True, execution_time=0.0)
    
    def _validate_parameter_type(self, value: Any, expected_type: DSLDataType) -> bool:
        """Validate parameter type."""
        type_mapping = {
            DSLDataType.STRING: str,
            DSLDataType.INTEGER: int,
            DSLDataType.FLOAT: (int, float),
            DSLDataType.BOOLEAN: bool,
            DSLDataType.LIST: list,
            DSLDataType.DICT: dict,
            DSLDataType.PATH: (str, Path),
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True
    
    def process_natural_language(self, text: str) -> DSLCommandResult:
        """Process natural language input."""
        return self.nlp_integration.process_natural_language(text)
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions."""
        return self.nlp_integration.get_suggestions(partial_input)


class SchemaBasedCommands:
    """Implementation of schema-based DSL commands."""
    
    def __init__(self, context: DSLContext, registry: SchemaCommandRegistry):
        """Initialize schema-based commands."""
        self.context = context
        self.registry = registry
        self.nlp_model = SimpleNLPModel()
    
    async def execute_command(self, command_name: str, args: Dict[str, Any]) -> DSLCommandResult:
        """Execute a schema-based command."""
        start_time = time.time()
        
        # Validate command
        validation = self.registry.validate_command_call(command_name, args)
        if not validation.success:
            return validation
        
        command = self.registry.get_command(command_name)
        if not command:
            return DSLCommandResult(
                success=False,
                error=f"Command not found: {command_name}",
                execution_time=0.0,
            )
        
        try:
            # Execute command based on type
            if command.command_type == DSLCommandType.SUMD:
                result = await self._execute_sumd_command(command, args)
            elif command.command_type == DSLCommandType.FILE:
                result = await self._execute_file_command(command, args)
            elif command.command_type == DSLCommandType.SEARCH:
                result = await self._execute_search_command(command, args)
            elif command.command_type == DSLCommandType.UTILITY:
                result = await self._execute_utility_command(command, args)
            elif command.command_type == DSLCommandType.NLP:
                result = await self._execute_nlp_command(command, args)
            elif command.command_type == DSLCommandType.SCHEMA:
                result = await self._execute_schema_command(command, args)
            else:
                result = {"error": f"Unsupported command type: {command.command_type}"}
            
            execution_time = time.time() - start_time
            return DSLCommandResult(
                success=True,
                result=result,
                execution_time=execution_time,
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return DSLCommandResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
            )
    
    async def _execute_sumd_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute SUMD command."""
        if command.name == "scan":
            return await self._cmd_sumd_scan(args)
        elif command.name == "validate":
            return await self._cmd_sumd_validate(args)
        elif command.name == "info":
            return await self._cmd_sumd_info(args)
        else:
            return {"error": f"Unknown SUMD command: {command.name}"}
    
    async def _execute_file_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute file command."""
        if command.name == "cat":
            return await self._cmd_cat(args)
        elif command.name == "ls":
            return await self._cmd_ls(args)
        elif command.name == "edit":
            return await self._cmd_edit(args)
        else:
            return {"error": f"Unknown file command: {command.name}"}
    
    async def _execute_search_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute search command."""
        if command.name == "find":
            return await self._cmd_find(args)
        elif command.name == "grep":
            return await self._cmd_grep(args)
        else:
            return {"error": f"Unknown search command: {command.name}"}
    
    async def _execute_utility_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute utility command."""
        if command.name == "echo":
            return await self._cmd_echo(args)
        elif command.name == "pwd":
            return await self._cmd_pwd(args)
        elif command.name == "cd":
            return await self._cmd_cd(args)
        else:
            return {"error": f"Unknown utility command: {command.name}"}
    
    async def _execute_nlp_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute NLP command."""
        if command.name == "ask":
            return await self._cmd_ask(args)
        elif command.name == "summarize":
            return await self._cmd_summarize(args)
        elif command.name == "analyze_sentiment":
            return await self._cmd_analyze_sentiment(args)
        else:
            return {"error": f"Unknown NLP command: {command.name}"}
    
    async def _execute_schema_command(self, command: DSLCommandSchema, args: Dict[str, Any]) -> Any:
        """Execute schema command."""
        if command.name == "schema_info":
            return await self._cmd_schema_info(args)
        elif command.name == "list_commands":
            return await self._cmd_list_commands(args)
        elif command.name == "command_help":
            return await self._cmd_command_help(args)
        else:
            return {"error": f"Unknown schema command: {command.name}"}
    
    # SUMD Commands
    async def _cmd_sumd_scan(self, args: Dict[str, Any]) -> Any:
        """Scan project and generate SUMD documentation."""
        path = args.get("path", ".")
        profile = args.get("profile", "rich")
        fix = args.get("fix", True)
        
        # Import SUMD scanner
        try:
            from ..scanner import scan_workspace
            from pathlib import Path
            
            scan_path = self.context.working_directory / path
            results = scan_workspace(scan_path, profile=profile, fix=fix)
            
            return {
                "scanned_projects": len(results),
                "results": results,
                "profile": profile,
            }
        except ImportError:
            return {"error": "SUMD scanner not available"}
    
    async def _cmd_sumd_validate(self, args: Dict[str, Any]) -> Any:
        """Validate SUMD document."""
        file_path = args["file"]
        full_path = self.context.working_directory / file_path
        
        try:
            from ..parser import parse_file
            from ..parser import SUMDParser
            
            document = parse_file(full_path)
            parser = SUMDParser()
            errors = parser.validate(document)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "file": str(full_path),
            }
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}
    
    async def _cmd_sumd_info(self, args: Dict[str, Any]) -> Any:
        """Get SUMD document information."""
        file_path = args["file"]
        full_path = self.context.working_directory / file_path
        
        try:
            from ..parser import parse_file
            
            document = parse_file(full_path)
            
            return {
                "project_name": document.project_name,
                "description": document.description,
                "sections": [
                    {
                        "name": section.name,
                        "type": section.type.value,
                        "level": section.level,
                    }
                    for section in document.sections
                ],
                "file": str(full_path),
            }
        except Exception as e:
            return {"error": f"Failed to get info: {str(e)}"}
    
    # File Commands
    async def _cmd_cat(self, args: Dict[str, Any]) -> Any:
        """Display file contents."""
        file_path = args["file"]
        full_path = self.context.working_directory / file_path
        
        try:
            content = full_path.read_text(encoding="utf-8")
            return content
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def _cmd_ls(self, args: Dict[str, Any]) -> Any:
        """List directory contents."""
        path = args.get("path", ".")
        pattern = args.get("pattern", "*")
        
        full_path = self.context.working_directory / path
        
        try:
            files = list(full_path.glob(pattern))
            return [str(f.relative_to(self.context.working_directory)) for f in files]
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}
    
    async def _cmd_edit(self, args: Dict[str, Any]) -> Any:
        """Edit file contents."""
        file_path = args["file"]
        content = args["content"]
        full_path = self.context.working_directory / file_path
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    # Search Commands
    async def _cmd_find(self, args: Dict[str, Any]) -> Any:
        """Find files matching pattern."""
        pattern = args.get("pattern", "*")
        path = args.get("path", ".")
        
        full_path = self.context.working_directory / path
        
        try:
            files = list(full_path.rglob(pattern))
            return [str(f.relative_to(self.context.working_directory)) for f in files if f.is_file()]
        except Exception as e:
            return {"error": f"Failed to find files: {str(e)}"}
    
    async def _cmd_grep(self, args: Dict[str, Any]) -> Any:
        """Search text in files."""
        pattern = args.get("pattern", "")
        path = args.get("path", ".")
        
        full_path = self.context.working_directory / path
        
        try:
            import re
            results = []
            
            for file_path in full_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.md', '.txt', '.js', '.ts']:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        if re.search(pattern, content, re.IGNORECASE):
                            results.append(str(file_path.relative_to(self.context.working_directory)))
                    except:
                        continue
            
            return results
        except Exception as e:
            return {"error": f"Failed to search files: {str(e)}"}
    
    # Utility Commands
    async def _cmd_echo(self, args: Dict[str, Any]) -> Any:
        """Display message."""
        text = args.get("text", "")
        return text
    
    async def _cmd_pwd(self, args: Dict[str, Any]) -> Any:
        """Print working directory."""
        return str(self.context.working_directory)
    
    async def _cmd_cd(self, args: Dict[str, Any]) -> Any:
        """Change directory."""
        path = args.get("path", ".")
        new_path = self.context.working_directory / path
        
        if new_path.is_dir():
            self.context.working_directory = new_path.resolve()
            return str(self.context.working_directory)
        else:
            return {"error": f"Directory not found: {path}"}
    
    # NLP Commands
    async def _cmd_ask(self, args: Dict[str, Any]) -> Any:
        """Ask natural language question."""
        question = args.get("question", "")
        context = args.get("context", "")
        
        # Simple NLP processing
        intent, confidence = self.nlp_model.predict_intent(question)
        
        if confidence < 0.7:
            return f"I'm not sure how to answer: {question}"
        
        # Generate response based on intent
        if intent == "scan_project":
            return "To scan the project, use: scan()"
        elif intent == "validate_document":
            return "To validate SUMD.md, use: validate('SUMD.md')"
        elif intent == "get_info":
            return "To get project info, use: info('SUMD.md')"
        else:
            return f"I understand you want to {intent.replace('_', ' ')}"
    
    async def _cmd_summarize(self, args: Dict[str, Any]) -> Any:
        """Generate summary."""
        target = args.get("target", "project")
        length = args.get("length", "medium")
        
        if target == "project":
            return f"This is a SUMD project with {len(self.registry.commands)} available commands."
        else:
            return f"Summary of {target} (length: {length})"
    
    async def _cmd_analyze_sentiment(self, args: Dict[str, Any]) -> Any:
        """Analyze sentiment of text."""
        text = args.get("text", "")
        
        # Simple sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "horrible", "worst"]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "positive_score": positive_count,
            "negative_score": negative_count,
            "confidence": max(positive_count, negative_count) / len(words) if words else 0.0,
        }
    
    # Schema Commands
    async def _cmd_schema_info(self, args: Dict[str, Any]) -> Any:
        """Get schema information."""
        return {
            "project_name": self.registry.project_schema.name,
            "version": self.registry.project_schema.version,
            "commands": len(self.registry.commands),
            "nlp_enabled": self.registry.project_schema.nlp_enabled,
        }
    
    async def _cmd_list_commands(self, args: Dict[str, Any]) -> Any:
        """List available commands."""
        command_type = args.get("type")
        
        if command_type:
            try:
                cmd_type = DSLCommandType(command_type)
                commands = self.registry.list_commands(cmd_type)
            except ValueError:
                commands = list(self.registry.commands.values())
        else:
            commands = list(self.registry.commands.values())
        
        return [
            {
                "name": cmd.name,
                "type": cmd.command_type.value,
                "description": cmd.description,
                "aliases": cmd.aliases,
            }
            for cmd in commands
        ]
    
    async def _cmd_command_help(self, args: Dict[str, Any]) -> Any:
        """Get command help."""
        command_name = args.get("command")
        
        if not command_name:
            return {"error": "Command name required"}
        
        command = self.registry.get_command(command_name)
        if not command:
            return {"error": f"Command not found: {command_name}"}
        
        return {
            "name": command.name,
            "description": command.description,
            "parameters": [
                {
                    "name": param.name,
                    "type": param.data_type.value,
                    "required": param.required,
                    "default": param.default,
                    "description": param.description,
                }
                for param in command.parameters
            ],
            "examples": command.examples,
            "aliases": command.aliases,
        }
