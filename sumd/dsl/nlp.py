"""NLP Integration for DSL - Natural Language Processing capabilities."""

import re
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json

from .schema import (
    DSLCommandSchema,
    DSLCommandType,
    DSLActionType,
    NLPIntent,
    NLPEntity,
    NLPModel,
    DSLProjectSchema,
    DSLCommandResult,
)


class NLPProcessor:
    """Natural Language Processor for DSL commands."""
    
    def __init__(self, project_schema: DSLProjectSchema):
        """Initialize NLP processor with project schema."""
        self.project_schema = project_schema
        self.intents: Dict[str, NLPIntent] = {}
        self.entities: Dict[str, NLPEntity] = {}
        self.patterns: Dict[str, List[str]] = {}
        self._initialize_default_intents()
        self._initialize_default_entities()
    
    def _initialize_default_intents(self):
        """Initialize default NLP intents."""
        self.intents = {
            "scan_project": NLPIntent(
                name="scan_project",
                description="Scan project and generate documentation",
                examples=[
                    "scan the project",
                    "generate SUMD documentation",
                    "analyze the project structure",
                    "create project documentation",
                    "scan this directory",
                ],
                entities={"path": "path", "profile": "string"},
                dsl_mapping="scan",
            ),
            "validate_document": NLPIntent(
                name="validate_document",
                description="Validate SUMD document",
                examples=[
                    "validate SUMD.md",
                    "check if SUMD is valid",
                    "validate the documentation",
                    "check SUMD file",
                ],
                entities={"file": "path"},
                dsl_mapping="validate",
            ),
            "get_info": NLPIntent(
                name="get_info",
                description="Get information about project or file",
                examples=[
                    "show project info",
                    "get information about SUMD",
                    "tell me about this project",
                    "what is this project about",
                    "project details",
                ],
                entities={"file": "path"},
                dsl_mapping="info",
            ),
            "list_files": NLPIntent(
                name="list_files",
                description="List files in directory",
                examples=[
                    "list files",
                    "show all files",
                    "what files are here",
                    "list directory contents",
                    "show files in src",
                ],
                entities={"path": "path", "pattern": "string"},
                dsl_mapping="ls",
            ),
            "read_file": NLPIntent(
                name="read_file",
                description="Read file contents",
                examples=[
                    "read the file",
                    "show file contents",
                    "display README",
                    "open the file",
                    "what's in this file",
                ],
                entities={"file": "path"},
                dsl_mapping="cat",
            ),
            "ask_question": NLPIntent(
                name="ask_question",
                description="Ask natural language question",
                examples=[
                    "what are the dependencies",
                    "how do I run this",
                    "what does this function do",
                    "explain the architecture",
                    "tell me about the tests",
                ],
                entities={"question": "string", "context": "string"},
                dsl_mapping="ask",
            ),
            "summarize": NLPIntent(
                name="summarize",
                description="Generate summary",
                examples=[
                    "summarize the project",
                    "give me a summary",
                    "brief overview",
                    "summarize this file",
                    "quick summary",
                ],
                entities={"target": "string", "length": "string"},
                dsl_mapping="summarize",
            ),
            "create_file": NLPIntent(
                name="create_file",
                description="Create or edit file",
                examples=[
                    "create a file",
                    "write to file",
                    "edit the file",
                    "add content to file",
                    "create new file",
                ],
                entities={"file": "path", "content": "string"},
                dsl_mapping="edit",
            ),
        }
    
    def _initialize_default_entities(self):
        """Initialize default NLP entities."""
        self.entities = {
            "path": NLPEntity(
                name="path",
                type="path",
                values=[".", "src", "lib", "app", "docs", "tests", "SUMD.md", "README.md"],
                patterns=[
                    r"[\w\-/\.]+\.(md|py|js|ts|json|yaml|yml|toml)",
                    r"[\w\-/\.]+",
                    r"this (?:file|directory|folder|project)",
                    r"current (?:directory|folder)",
                ],
            ),
            "string": NLPEntity(
                name="string",
                type="string",
                values=[],
                patterns=[
                    r'"[^"]*"',
                    r"'[^']*'",
                    r"[\w\s\-]+",
                ],
            ),
            "profile": NLPEntity(
                name="profile",
                type="string",
                values=["minimal", "light", "rich", "refactor"],
                patterns=[
                    r"(?:minimal|light|rich|refactor)",
                ],
            ),
            "length": NLPEntity(
                name="length",
                type="string",
                values=["short", "medium", "long"],
                patterns=[
                    r"(?:short|medium|long)",
                ],
            ),
        }
    
    def parse_natural_language(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Parse natural language input and return intent and entities."""
        text = text.lower().strip()
        
        # Try to match intents
        for intent_name, intent in self.intents.items():
            for example in intent.examples:
                if self._text_matches_intent(text, example):
                    entities = self._extract_entities(text, intent)
                    return intent.dsl_mapping, entities
        
        # Fallback: try to extract command directly
        return self._extract_command_fallback(text)
    
    def _text_matches_intent(self, text: str, example: str) -> bool:
        """Check if text matches intent example."""
        # Simple keyword matching for now
        text_words = set(text.split())
        example_words = set(example.split())
        
        # Check if enough words match
        intersection = text_words.intersection(example_words)
        return len(intersection) >= max(2, len(example_words) // 2)
    
    def _extract_entities(self, text: str, intent: NLPIntent) -> Dict[str, Any]:
        """Extract entities from text based on intent."""
        entities = {}
        
        for entity_name, entity_type in intent.entities.items():
            if entity_name in self.entities:
                entity = self.entities[entity_name]
                value = self._extract_entity_value(text, entity)
                if value:
                    entities[entity_name] = value
        
        return entities
    
    def _extract_entity_value(self, text: str, entity: NLPEntity) -> Optional[str]:
        """Extract entity value from text."""
        for pattern in entity.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip('"\'')
        
        # Check for exact values
        text_lower = text.lower()
        for value in entity.values:
            if value.lower() in text_lower:
                return value
        
        return None
    
    def _extract_command_fallback(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Fallback command extraction."""
        # Look for command keywords
        command_patterns = {
            "scan": r"\bscan\b",
            "validate": r"\bvalidate\b|\bcheck\b",
            "info": r"\binfo\b|\bdetails\b|\btell me\b",
            "list": r"\blist\b|\bls\b|\bshow\b",
            "cat": r"\bread\b|\bshow\b|\bdisplay\b|\bopen\b",
            "ask": r"\bask\b|\bwhat\b|\bhow\b|\bwhy\b",
            "summarize": r"\bsummarize\b|\bsummary\b|\boverview\b",
            "edit": r"\bcreate\b|\bwrite\b|\bedit\b|\badd\b",
        }
        
        for command, pattern in command_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                entities = self._extract_entities_fallback(text)
                return command, entities
        
        return "echo", {"text": text}
    
    def _extract_entities_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback entity extraction."""
        entities = {}
        
        # Extract file paths
        path_pattern = r"[\w\-/\.]+\.(md|py|js|ts|json|yaml|yml|toml)"
        path_matches = re.findall(path_pattern, text, re.IGNORECASE)
        if path_matches:
            entities["file"] = path_matches[0]
        
        # Extract quoted strings
        string_pattern = r'["\']([^"\']+)["\']'
        string_matches = re.findall(string_pattern, text)
        if string_matches:
            entities["text"] = string_matches[0]
        
        return entities
    
    def generate_dsl_command(self, intent: str, entities: Dict[str, Any]) -> str:
        """Generate DSL command from intent and entities."""
        # Generate function call syntax
        if entities:
            # Create parameter list
            params = []
            for param_name, param_value in entities.items():
                if param_value and param_name != "path":  # Skip invalid entities
                    if isinstance(param_value, str):
                        params.append(f'"{param_value}"')
                    else:
                        params.append(str(param_value))
            
            if params:
                return f"{intent}({', '.join(params)})"
            else:
                return f"{intent}()"
        else:
            return f"{intent}()"
    
    def suggest_commands(self, partial_input: str) -> List[str]:
        """Suggest commands based on partial input."""
        suggestions = []
        partial_lower = partial_input.lower()
        
        for intent_name, intent in self.intents.items():
            for example in intent.examples:
                if partial_lower in example.lower():
                    dsl_cmd = self.generate_dsl_command(intent.dsl_mapping, {})
                    suggestions.append(dsl_cmd)
        
        return list(set(suggestions))[:5]  # Return top 5 unique suggestions


class NLPIntegration:
    """NLP integration for DSL engine."""
    
    def __init__(self, project_schema: DSLProjectSchema):
        """Initialize NLP integration."""
        self.project_schema = project_schema
        self.processor = NLPProcessor(project_schema)
        self.enabled = project_schema.nlp_enabled
    
    def process_natural_language(self, text: str) -> DSLCommandResult:
        """Process natural language input and return DSL command."""
        if not self.enabled:
            return DSLCommandResult(
                success=False,
                error="NLP is not enabled",
                execution_time=0.0,
            )
        
        try:
            # Parse intent and entities
            intent, entities = self.processor.parse_natural_language(text)
            
            # Generate DSL command
            dsl_command = self.processor.generate_dsl_command(intent, entities)
            
            return DSLCommandResult(
                success=True,
                result={
                    "original_text": text,
                    "intent": intent,
                    "entities": entities,
                    "dsl_command": dsl_command,
                },
                execution_time=0.1,
            )
        
        except Exception as e:
            return DSLCommandResult(
                success=False,
                error=f"NLP processing failed: {str(e)}",
                execution_time=0.0,
            )
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions based on partial input."""
        if not self.enabled:
            return []
        
        return self.processor.suggest_commands(partial_input)
    
    def add_custom_intent(self, intent: NLPIntent):
        """Add custom intent to NLP processor."""
        self.processor.intents[intent.name] = intent
    
    def add_custom_entity(self, entity: NLPEntity):
        """Add custom entity to NLP processor."""
        self.processor.entities[entity.name] = entity
    
    def get_available_intents(self) -> List[str]:
        """Get list of available intents."""
        return list(self.processor.intents.keys())
    
    def get_intent_examples(self, intent_name: str) -> List[str]:
        """Get example phrases for an intent."""
        if intent_name in self.processor.intents:
            return self.processor.intents[intent_name].examples
        return []


class SimpleNLPModel:
    """Simple NLP model implementation for basic functionality."""
    
    def __init__(self):
        """Initialize simple NLP model."""
        self.name = "simple_nlp"
        self.type = "rule_based"
        self.version = "1.0.0"
        self.confidence_threshold = 0.7
    
    def predict_intent(self, text: str) -> Tuple[str, float]:
        """Predict intent with confidence score."""
        # Simple keyword-based prediction
        intent_keywords = {
            "scan_project": ["scan", "generate", "analyze", "create", "documentation"],
            "validate_document": ["validate", "check", "verify", "test"],
            "get_info": ["info", "details", "tell me", "about", "project"],
            "list_files": ["list", "show", "files", "directory", "contents"],
            "read_file": ["read", "show", "display", "open", "contents"],
            "ask_question": ["what", "how", "why", "ask", "question"],
            "summarize": ["summarize", "summary", "overview", "brief"],
            "create_file": ["create", "write", "edit", "add", "file"],
        }
        
        text_lower = text.lower()
        best_intent = "echo"
        best_score = 0.0
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            score = score / len(keywords)  # Normalize
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, best_score
    
    def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract entities based on intent."""
        entities = {}
        
        # Extract file paths
        path_pattern = r"[\w\-/\.]+\.(md|py|js|ts|json|yaml|yml|toml)"
        path_matches = re.findall(path_pattern, text, re.IGNORECASE)
        if path_matches:
            entities["file"] = path_matches[0]
        
        # Extract quoted strings
        string_pattern = r'["\']([^"\']+)["\']'
        string_matches = re.findall(string_pattern, text)
        if string_matches:
            entities["text"] = string_matches[0]
        
        # Extract directories
        dir_pattern = r"\b(src|lib|app|docs|tests|bin|config)\b"
        dir_matches = re.findall(dir_pattern, text, re.IGNORECASE)
        if dir_matches:
            entities["path"] = dir_matches[0]
        
        return entities


# Create default NLP model
DEFAULT_NLP_MODEL = NLPModel(
    name="simple_nlp",
    type="rule_based",
    version="1.0.0",
    confidence_threshold=0.7,
    intents=[],  # Will be populated from processor
    entities=[],  # Will be populated from processor
)
