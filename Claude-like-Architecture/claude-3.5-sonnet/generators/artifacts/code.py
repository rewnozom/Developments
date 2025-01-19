# generators/artifacts/code.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from pathlib import Path
import re
import ast
from models.artifacts import (
    Artifact,
    ArtifactType,
    ArtifactMetadata,
    ArtifactError,
    ValidationResult
)

@dataclass
class CodeGenerationConfig:
    """Configuration for code generation."""
    language: str
    style_guide: Optional[Dict[str, Any]] = None
    max_length: Optional[int] = None
    include_comments: bool = True
    include_docstrings: bool = True
    include_type_hints: bool = True
    formatting: Dict[str, Any] = None
    linting_rules: Dict[str, Any] = None

class CodeGenerator:
    """Generator for code artifacts."""

    def __init__(self, config: Optional[CodeGenerationConfig] = None):
        self.config = config or CodeGenerationConfig(language="python")
        self.formatters: Dict[str, callable] = {}
        self.validators: Dict[str, callable] = {}
        self.style_checkers: Dict[str, callable] = {}
        self._initialize_processors()

    def generate_code_artifact(self,
                            content: str,
                            identifier: str,
                            title: str,
                            metadata: Optional[Dict[str, Any]] = None) -> Artifact:
        """Generate a code artifact."""
        try:
            # Validate inputs
            if not content:
                raise ArtifactError("Code content cannot be empty")
                
            if not identifier:
                raise ArtifactError("Artifact identifier cannot be empty")
                
            if not title:
                raise ArtifactError("Artifact title cannot be empty")
                
            if metadata is not None and not isinstance(metadata, dict):
                raise ArtifactError("Metadata must be a dictionary")

            # Validate and format code
            try:
                formatted_code = self._format_code(content)
            except Exception as e:
                raise ArtifactError(f"Code formatting failed: {str(e)}")

            validation_result = self._validate_code(formatted_code)
            if not validation_result.valid:
                raise ArtifactError(
                    f"Code validation failed: {', '.join(validation_result.errors)}"
                )

            # Create metadata
            try:
                artifact_metadata = ArtifactMetadata(
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    version="1.0.0",
                    creator="CodeGenerator",
                    size=len(formatted_code.encode('utf-8')),
                    checksum=self._generate_checksum(formatted_code),
                    language=self.config.language,
                    custom_data=metadata or {}
                )
            except Exception as e:
                raise ArtifactError(f"Failed to create artifact metadata: {str(e)}")

            # Create artifact
            artifact = Artifact(
                type=ArtifactType.CODE,
                content=formatted_code,
                identifier=identifier,
                title=title,
                metadata=artifact_metadata,
                validation=validation_result
            )

            return artifact

        except ArtifactError:
            raise
        except Exception as e:
            raise ArtifactError(f"Code generation failed: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize code processors."""
        # Format processors
        self.formatters.update({
            "python": self._format_python,
            "javascript": self._format_javascript,
            "typescript": self._format_typescript
        })

        # Validation processors
        self.validators.update({
            "python": self._validate_python,
            "javascript": self._validate_javascript,
            "typescript": self._validate_typescript
        })

        # Style checkers
        self.style_checkers.update({
            "python": self._check_python_style,
            "javascript": self._check_javascript_style,
            "typescript": self._check_typescript_style
        })

    def _format_code(self, content: str) -> str:
        """Format code according to language rules."""
        formatter = self.formatters.get(self.config.language.lower())
        if not formatter:
            return content
        return formatter(content)

    def _validate_code(self, content: str) -> ValidationResult:
        """Validate code content."""
        errors = []
        warnings = []

        # Basic validation
        if not content.strip():
            errors.append("Code content cannot be empty")

        # Language-specific validation
        validator = self.validators.get(self.config.language.lower())
        if validator:
            result = validator(content)
            errors.extend(result.get('errors', []))
            warnings.extend(result.get('warnings', []))

        # Style validation
        style_checker = self.style_checkers.get(self.config.language.lower())
        if style_checker and self.config.style_guide:
            style_issues = style_checker(content)
            warnings.extend(style_issues)

        # Length validation
        if self.config.max_length and len(content) > self.config.max_length:
            warnings.append(f"Code exceeds maximum length of {self.config.max_length} characters")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _format_python(self, content: str) -> str:
        """Format Python code."""
        try:
            import black
            import autopep8

            # Apply autopep8 for basic formatting
            content = autopep8.fix_code(
                content,
                options={'aggressive': 1}
            )

            # Apply black for consistent style
            mode = black.Mode(
                line_length=88,
                string_normalization=True,
                is_pyi=False
            )
            content = black.format_str(content, mode=mode)

            return content

        except ImportError:
            return content  # Return unformatted if formatters not available
        except Exception as e:
            raise ArtifactError(f"Python formatting failed: {str(e)}")

    def _format_javascript(self, content: str) -> str:
        """Format JavaScript code."""
        try:
            # Basic formatting rules
            lines = content.split('\n')
            formatted_lines = []
            indent_level = 0

            for line in lines:
                stripped = line.strip()
                
                # Adjust indent for blocks
                if stripped.endswith('{'):
                    formatted_lines.append('  ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith('}'):
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('  ' * indent_level + stripped)
                else:
                    formatted_lines.append('  ' * indent_level + stripped)

            return '\n'.join(formatted_lines)

        except Exception as e:
            raise ArtifactError(f"JavaScript formatting failed: {str(e)}")

    def _format_typescript(self, content: str) -> str:
        """Format TypeScript code."""
        # Similar to JavaScript formatting for now
        return self._format_javascript(content)

    def _validate_python(self, content: str) -> Dict[str, List[str]]:
        """Validate Python code."""
        errors = []
        warnings = []

        try:
            # Syntax validation
            ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
            return {'errors': errors, 'warnings': warnings}

        # Check imports
        import_checker = ImportChecker()
        import_checker.visit(ast.parse(content))
        warnings.extend(import_checker.issues)

        # Check complexity
        complexity_checker = ComplexityChecker()
        complexity_checker.visit(ast.parse(content))
        warnings.extend(complexity_checker.issues)

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_javascript(self, content: str) -> Dict[str, List[str]]:
        """Validate JavaScript code."""
        errors = []
        warnings = []

        # Basic syntax validation
        try:
            # Check for common syntax issues
            if not content.strip():
                errors.append("Empty code")
            
            # Check for unmatched brackets/parentheses
            if content.count('{') != content.count('}'):
                errors.append("Unmatched curly braces")
            if content.count('(') != content.count(')'):
                errors.append("Unmatched parentheses")
            
            # Check for common issues
            if 'eval(' in content:
                warnings.append("Use of eval() is discouraged")
            if 'with(' in content:
                warnings.append("Use of with() is discouraged")

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_typescript(self, content: str) -> Dict[str, List[str]]:
        """Validate TypeScript code."""
        # Similar to JavaScript validation with additional type checking
        result = self._validate_javascript(content)
        
        # Additional TypeScript-specific checks
        if 'any' in content:
            result['warnings'].append("Use of 'any' type should be avoided")
        
        return result

    def _check_python_style(self, content: str) -> List[str]:
        """Check Python code style."""
        issues = []

        try:
            # Check line length
            max_line_length = self.config.style_guide.get('max_line_length', 88)
            for i, line in enumerate(content.split('\n'), 1):
                if len(line) > max_line_length:
                    issues.append(f"Line {i} exceeds maximum length of {max_line_length}")

            # Check naming conventions
            for node in ast.walk(ast.parse(content)):
                if isinstance(node, ast.ClassDef):
                    if not node.name[0].isupper():
                        issues.append(f"Class '{node.name}' should use CapWords convention")
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.islower():
                        issues.append(f"Function '{node.name}' should use lowercase_with_underscores")

        except Exception as e:
            issues.append(f"Style check failed: {str(e)}")

        return issues

    def _check_javascript_style(self, content: str) -> List[str]:
        """Check JavaScript code style."""
        issues = []

        # Check semicolon usage
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.endswith('{') and not line.endswith('}'):
                if not line.endswith(';'):
                    issues.append(f"Line {i} missing semicolon")

        # Check spacing around operators
        operator_pattern = r'[^=!<>]=[^=]|[+\-*/%]=?(?!=)|===?|!==?|<=?|>=?'
        for i, line in enumerate(lines, 1):
            for match in re.finditer(operator_pattern, line):
                op = match.group()
                if not re.search(r'\s+' + re.escape(op) + r'\s+', line):
                    issues.append(f"Line {i}: Missing spaces around operator '{op}'")

        return issues

    def _check_typescript_style(self, content: str) -> List[str]:
        """Check TypeScript code style."""
        # Include JavaScript style checks
        issues = self._check_javascript_style(content)

        # Additional TypeScript-specific checks
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check interface naming
            if 'interface' in line and not re.search(r'interface\s+I[A-Z]', line):
                issues.append(f"Line {i}: Interface names should start with 'I'")
            
            # Check type aliases
            if 'type' in line and not re.search(r'type\s+T[A-Z]', line):
                issues.append(f"Line {i}: Type aliases should start with 'T'")

        return issues

    def _generate_checksum(self, content: str) -> str:
        """Generate checksum for code content."""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()


class ImportChecker(ast.NodeVisitor):
    """Check Python imports."""
    def __init__(self):
        self.issues = []
        self.imported_modules = set()

    def visit_Import(self, node):
        for name in node.names:
            self.imported_modules.add(name.name)
            if name.name in ['os', 'sys', 'subprocess']:
                self.issues.append(f"Use of system module '{name.name}' should be reviewed")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in ['os', 'sys', 'subprocess']:
            self.issues.append(f"Use of system module '{node.module}' should be reviewed")
        self.generic_visit(node)


class ComplexityChecker(ast.NodeVisitor):
    """Check code complexity."""
    def __init__(self):
        self.issues = []
        self.function_complexity = {}

    def visit_FunctionDef(self, node):
        complexity = self._calculate_complexity(node)
        if complexity > 10:
            self.issues.append(
                f"Function '{node.name}' has high cyclomatic complexity ({complexity})"
            )
        self.generic_visit(node)

    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity