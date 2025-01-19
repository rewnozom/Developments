# generators/artifacts/special.py

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
import re
import json
import logging
import xml.etree.ElementTree as ET
from core.exceptions import GenerationError, ArtifactError
from models.artifacts import (
    Artifact,
    ArtifactType,
    ArtifactMetadata,
    ValidationResult
)

@dataclass
class SpecialGenerationConfig:
    """Configuration for special artifacts generation."""
    type: ArtifactType
    style_guide: Optional[Dict[str, Any]] = None
    max_size: Optional[int] = None
    validation_rules: Optional[Dict[str, Any]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    help_url: Optional[str] = None

@dataclass
class SpecialArtifact:
    """Special artifact data."""
    type: ArtifactType
    content: str
    metadata: ArtifactMetadata
    timestamp: datetime

class SpecialArtifactGenerator:
    """Generates special artifacts like SVG, Mermaid diagrams, React components, and charts."""

    def __init__(self, config: Optional[SpecialGenerationConfig] = None):
        self.config = config or SpecialGenerationConfig(type=ArtifactType.SVG)
        self.generators: Dict[ArtifactType, callable] = {}
        self.validators: Dict[ArtifactType, callable] = {}
        self.formatters: Dict[ArtifactType, callable] = {}
        self.optimizers: Dict[ArtifactType, callable] = {}
        self._initialize_processors()
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def generate_artifact(self,
                        content: Dict[str, Any],
                        identifier: str,
                        title: str,
                        artifact_type: ArtifactType,
                        metadata: Optional[Dict[str, Any]] = None) -> Artifact:
        """Generate a special artifact."""
        try:
            self.logger.debug(f"Starting generation of {artifact_type.value} artifact.")
            
            # Validate inputs
            if not content:
                raise ArtifactError("Content cannot be empty")
                
            if not identifier:
                raise ArtifactError("Identifier cannot be empty")
                
            if not title:
                raise ArtifactError("Title cannot be empty")
                
            if not isinstance(content, dict):
                raise ArtifactError("Content must be a dictionary")
                
            if not isinstance(artifact_type, ArtifactType):
                raise ArtifactError("Invalid artifact type")
                
            if metadata is not None and not isinstance(metadata, dict):
                raise ArtifactError("Metadata must be a dictionary")

            # Validate artifact type
            if artifact_type not in self.generators:
                raise ArtifactError(f"No generator found for type: {artifact_type.value}")

            # Generate artifact content
            try:
                generator = self.generators[artifact_type]
                generated_content = generator(content, self.config.custom_settings or {})
                self.logger.debug(f"Generated content for {artifact_type.value}")
            except Exception as e:
                raise ArtifactError(f"Content generation failed: {str(e)}")

            # Validate artifact content
            validator = self.validators.get(artifact_type)
            if validator:
                validation_result = validator(generated_content)
                if not validation_result.valid:
                    self.logger.error(f"Validation failed for {artifact_type.value}: {validation_result.errors}")
                    raise ArtifactError(
                        f"Generated {artifact_type.value} artifact validation failed: {', '.join(validation_result.errors)}"
                    )
                if validation_result.warnings:
                    self.logger.warning(f"Validation warnings for {artifact_type.value}: {validation_result.warnings}")
            else:
                validation_result = ValidationResult(valid=True, errors=[], warnings=[])

            # Format and optimize content
            try:
                formatted_content = self._format_content(generated_content, artifact_type)
                optimized_content = self._optimize_content(formatted_content, artifact_type)
            except Exception as e:
                raise ArtifactError(f"Content processing failed: {str(e)}")

            # Create metadata
            try:
                artifact_metadata = ArtifactMetadata(
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    version="1.0.0",
                    creator="SpecialArtifactGenerator",
                    size=len(optimized_content.encode('utf-8')),
                    checksum=self._generate_checksum(optimized_content),
                    custom_data=metadata or {}
                )
            except Exception as e:
                raise ArtifactError(f"Failed to create artifact metadata: {str(e)}")

            # Create artifact
            artifact = Artifact(
                type=artifact_type,
                content=optimized_content,
                identifier=identifier,
                title=title,
                metadata=artifact_metadata,
                validation=validation_result
            )

            self.logger.info(f"Successfully generated {artifact_type.value} artifact with ID: {identifier}")
            return artifact

        except ArtifactError:
            raise
        except Exception as e:
            self.logger.error(f"Artifact generation failed: {str(e)}")
            raise ArtifactError(f"Failed to generate {artifact_type.value} artifact: {str(e)}")

        except Exception as e:
            self.logger.error(f"Artifact generation failed: {str(e)}")
            raise ArtifactError(f"Failed to generate {artifact_type.value} artifact: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize processors for different artifact types."""
        # Generators
        self.generators.update({
            ArtifactType.SVG: self._generate_svg,
            ArtifactType.MERMAID: self._generate_mermaid,
            ArtifactType.REACT: self._generate_react,
            ArtifactType.CHART: self._generate_chart
        })

        # Validators
        self.validators.update({
            ArtifactType.SVG: self._validate_svg,
            ArtifactType.MERMAID: self._validate_mermaid,
            ArtifactType.REACT: self._validate_react,
            ArtifactType.CHART: self._validate_chart
        })

        # Formatters
        self.formatters.update({
            ArtifactType.SVG: self._format_svg,
            ArtifactType.MERMAID: self._format_mermaid,
            ArtifactType.REACT: self._format_react,
            ArtifactType.CHART: self._format_chart
        })

        # Optimizers
        self.optimizers.update({
            ArtifactType.SVG: self._optimize_svg,
            ArtifactType.MERMAID: self._optimize_mermaid,
            ArtifactType.REACT: self._optimize_react,
            ArtifactType.CHART: self._optimize_chart
        })

    # =====================
    # Generators
    # =====================

    def _generate_svg(self,
                      content: Dict[str, Any],
                      settings: Dict[str, Any]) -> str:
        """Generate SVG artifact."""
        try:
            self.logger.debug("Generating SVG artifact.")
            # Extract SVG elements
            elements = content.get('elements', [])
            viewbox = content.get('viewBox', '0 0 100 100')
            
            # Build SVG structure
            svg_lines = [
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">'
            ]
            
            # Add elements
            for element in elements:
                if element['type'] == 'rect':
                    svg_lines.append(self._generate_svg_rect(element))
                elif element['type'] == 'circle':
                    svg_lines.append(self._generate_svg_circle(element))
                elif element['type'] == 'path':
                    svg_lines.append(self._generate_svg_path(element))
                elif element['type'] == 'text':
                    svg_lines.append(self._generate_svg_text(element))
                    
            svg_lines.append('</svg>')
            
            return '\n'.join(svg_lines)

        except Exception as e:
            self.logger.error(f"SVG generation failed: {str(e)}")
            raise GenerationError(f"SVG generation failed: {str(e)}")

    def _generate_mermaid(self,
                          content: Dict[str, Any],
                          settings: Dict[str, Any]) -> str:
        """Generate Mermaid diagram."""
        try:
            self.logger.debug("Generating Mermaid diagram.")
            diagram_type = content.get('type', 'graph')
            elements = content.get('elements', [])
            
            # Start diagram
            diagram_lines = [f"{diagram_type} TD"]
            
            # Add elements
            for element in elements:
                if element.get('type') == 'node':
                    diagram_lines.append(self._generate_mermaid_node(element))
                elif element.get('type') == 'connection':
                    diagram_lines.append(self._generate_mermaid_connection(element))
                    
            return '\n'.join(diagram_lines)

        except Exception as e:
            self.logger.error(f"Mermaid generation failed: {str(e)}")
            raise GenerationError(f"Mermaid generation failed: {str(e)}")

    def _generate_react(self,
                        content: Dict[str, Any],
                        settings: Dict[str, Any]) -> str:
        """Generate React component."""
        try:
            self.logger.debug("Generating React component.")
            # Extract component details
            name = content.get('name', 'Component')
            props = content.get('props', [])
            elements = content.get('elements', [])
            
            # Build component
            component_lines = [
                'import React from "react";',
                '',
                f'export default function {name}({self._format_props(props)}) {{',
                '  return (',
                '    <div className="container">'
            ]
            
            # Add elements
            for element in elements:
                component_lines.extend(
                    self._generate_react_element(element, indent=6)
                )
                
            component_lines.extend([
                '    </div>',
                '  );',
                '}'
            ])
            
            return '\n'.join(component_lines)

        except Exception as e:
            self.logger.error(f"React component generation failed: {str(e)}")
            raise GenerationError(f"React component generation failed: {str(e)}")

    def _generate_chart(self,
                        content: Dict[str, Any],
                        settings: Dict[str, Any]) -> str:
        """Generate chart configuration."""
        try:
            self.logger.debug("Generating chart configuration.")
            chart_type = content.get('type', 'line')
            data = content.get('data', [])
            config = content.get('config', {})
            
            # Generate chart configuration
            chart_config = {
                'type': chart_type,
                'data': {
                    'labels': [item.get('label') for item in data],
                    'datasets': [{
                        'data': [item.get('value') for item in data],
                        **config
                    }]
                },
                'options': settings
            }
            
            return json.dumps(chart_config, indent=2)

        except Exception as e:
            self.logger.error(f"Chart generation failed: {str(e)}")
            raise GenerationError(f"Chart generation failed: {str(e)}")

    # =====================
    # SVG Element Generators
    # =====================

    def _generate_svg_rect(self, element: Dict[str, Any]) -> str:
        """Generate SVG rectangle element."""
        attrs = {
            'x': element.get('x', 0),
            'y': element.get('y', 0),
            'width': element.get('width', 10),
            'height': element.get('height', 10),
            'fill': element.get('fill', 'black'),
            **element.get('attributes', {})
        }
        return f'<rect {self._format_attributes(attrs)}/>'

    def _generate_svg_circle(self, element: Dict[str, Any]) -> str:
        """Generate SVG circle element."""
        attrs = {
            'cx': element.get('cx', 0),
            'cy': element.get('cy', 0),
            'r': element.get('r', 5),
            'fill': element.get('fill', 'black'),
            **element.get('attributes', {})
        }
        return f'<circle {self._format_attributes(attrs)}/>'

    def _generate_svg_path(self, element: Dict[str, Any]) -> str:
        """Generate SVG path element."""
        attrs = {
            'd': element.get('d', ''),
            'stroke': element.get('stroke', 'black'),
            'fill': element.get('fill', 'none'),
            **element.get('attributes', {})
        }
        return f'<path {self._format_attributes(attrs)}/>'

    def _generate_svg_text(self, element: Dict[str, Any]) -> str:
        """Generate SVG text element."""
        attrs = {
            'x': element.get('x', 0),
            'y': element.get('y', 0),
            'font-size': element.get('fontSize', 12),
            **element.get('attributes', {})
        }
        return f'<text {self._format_attributes(attrs)}>{element.get("text", "")}</text>'

    # =====================
    # Mermaid Generators
    # =====================

    def _generate_mermaid_node(self, element: Dict[str, Any]) -> str:
        """Generate Mermaid node."""
        node_id = element.get('id', 'A')
        label = element.get('label', node_id)
        shape = element.get('shape', '')
        
        if shape:
            return f"{node_id}[{label}]"
        return f"{node_id}({label})"

    def _generate_mermaid_connection(self, element: Dict[str, Any]) -> str:
        """Generate Mermaid connection."""
        from_id = element.get('from', 'A')
        to_id = element.get('to', 'B')
        label = element.get('label', '')
        style = element.get('style', '-->')
        
        if label:
            return f"{from_id} {style}|{label}| {to_id}"
        return f"{from_id} {style} {to_id}"

    # =====================
    # React Element Generator
    # =====================

    def _generate_react_element(self, 
                                element: Dict[str, Any],
                                indent: int = 0) -> List[str]:
        """Generate React element."""
        tag = element.get('tag', 'div')
        className = element.get('className', '')
        children = element.get('children', [])
        props = element.get('props', {})
        
        lines = []
        spaces = ' ' * indent
        
        # Opening tag with props
        props_str = self._format_props_dict(props)
        if className:
            props_str = f'className="{className}" ' + props_str
        if props_str:
            lines.append(f'{spaces}<{tag} {props_str}>')
        else:
            lines.append(f'{spaces}<{tag}>')
            
        # Children
        for child in children:
            if isinstance(child, str):
                lines.append(f'{spaces}  {child}')
            elif isinstance(child, dict):
                lines.extend(self._generate_react_element(child, indent + 2))
                
        # Closing tag
        lines.append(f'{spaces}</{tag}>')
        
        return lines

    def _format_props_dict(self, props: Dict[str, Any]) -> str:
        """Format React component props from a dictionary."""
        if not props:
            return ''
        return ' '.join(f'{k}="{v}"' for k, v in props.items())

    # =====================
    # Formatters
    # =====================

    def _format_svg(self, content: str) -> str:
        """Format SVG content."""
        self.logger.debug("Formatting SVG content.")
        try:
            # Remove unnecessary whitespace
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'>\s+<', '><', content)
            
            # Format viewBox if present
            viewbox_match = re.search(r'viewBox=["\']([0-9\s.-]+)["\']', content)
            if viewbox_match:
                values = viewbox_match.group(1).split()
                formatted_viewbox = f'viewBox="{" ".join(values)}"'
                content = re.sub(r'viewBox=["\'"][0-9\s.-]+["\']', formatted_viewbox, content)

            # Remove width/height attributes if present
            content = re.sub(r'\s(width|height)=["\'][0-9]+["\']', '', content)

            return content.strip()
        except Exception as e:
            self.logger.error(f"SVG formatting failed: {str(e)}")
            raise ArtifactError(f"SVG formatting failed: {str(e)}")

    def _format_mermaid(self, content: str) -> str:
        """Format Mermaid diagram content."""
        self.logger.debug("Formatting Mermaid diagram.")
        try:
            lines = content.strip().split('\n')
            formatted_lines = []
            indent_level = 0

            for line in lines:
                stripped = line.strip()
                
                # Adjust indent for subgraphs
                if stripped.startswith('subgraph'):
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped == 'end':
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('    ' * indent_level + stripped)

            return '\n'.join(formatted_lines)
        except Exception as e:
            self.logger.error(f"Mermaid formatting failed: {str(e)}")
            raise ArtifactError(f"Mermaid formatting failed: {str(e)}")

    def _format_react(self, content: str) -> str:
        """Format React component content."""
        self.logger.debug("Formatting React component.")
        try:
            # Basic formatting with indentation
            lines = content.strip().split('\n')
            formatted_lines = []
            indent_level = 0

            for line in lines:
                stripped = line.strip()
                
                # Adjust indent for blocks
                if stripped.endswith('{') or stripped.endswith('('):
                    formatted_lines.append('  ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith('}'):
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('  ' * indent_level + stripped)
                else:
                    formatted_lines.append('  ' * indent_level + stripped)

            content = '\n'.join(formatted_lines)

            # Format JSX className attributes
            content = self._format_jsx(content)

            return content
        except Exception as e:
            self.logger.error(f"React formatting failed: {str(e)}")
            raise ArtifactError(f"React formatting failed: {str(e)}")

    def _format_chart(self, content: str) -> str:
        """Format chart configuration."""
        self.logger.debug("Formatting chart configuration.")
        try:
            # Pretty-print JSON if necessary
            return json.dumps(json.loads(content), indent=2)
        except json.JSONDecodeError as e:
            self.logger.error(f"Chart formatting failed: {str(e)}")
            raise ArtifactError(f"Chart formatting failed: {str(e)}")

    def _format_jsx(self, content: str) -> str:
        """Format JSX content."""
        # Sort className attributes alphabetically
        self.logger.debug("Formatting JSX className attributes.")
        try:
            def sort_classnames(match):
                classes = match.group(1).split()
                sorted_classes = ' '.join(sorted(classes))
                return f'className="{sorted_classes}"'

            content = re.sub(
                r'className=["\'](.*?)["\']',
                sort_classnames,
                content
            )
            return content
        except Exception as e:
            self.logger.error(f"JSX formatting failed: {str(e)}")
            raise ArtifactError(f"JSX formatting failed: {str(e)}")

    # =====================
    # Validators
    # =====================

    def _validate_content(self, content: str, artifact_type: ArtifactType) -> ValidationResult:
        """Validate content based on artifact type."""
        validator = self.validators.get(artifact_type)
        if not validator:
            return ValidationResult(valid=True, errors=[], warnings=[])
        return validator(content)

    def _validate_svg(self, content: str) -> ValidationResult:
        """Validate SVG content."""
        self.logger.debug("Validating SVG content.")
        errors = []
        warnings = []

        try:
            root = ET.fromstring(content)
            if root.tag != 'svg':
                errors.append("Content must start with <svg> tag.")

            # Check for viewBox attribute
            if 'viewBox' not in root.attrib:
                errors.append("SVG must include a viewBox attribute.")

            # Check for width and height attributes
            if 'width' in root.attrib or 'height' in root.attrib:
                warnings.append("SVG should use viewBox instead of width/height attributes.")

            # Check for unsafe content
            unsafe_patterns = [
                r'<script',
                r'javascript:',
                r'data:',
                r'xlink:href'
            ]
            for pattern in unsafe_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"SVG contains potentially unsafe content: {pattern}")

        except ET.ParseError as e:
            errors.append(f"Invalid SVG syntax: {str(e)}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_mermaid(self, content: str) -> ValidationResult:
        """Validate Mermaid diagram content."""
        self.logger.debug("Validating Mermaid diagram.")
        errors = []
        warnings = []

        try:
            if not content.strip():
                errors.append("Mermaid content cannot be empty.")

            # Check for valid diagram type
            valid_starts = [
                'graph ', 'sequenceDiagram', 'classDiagram',
                'stateDiagram', 'erDiagram', 'gantt', 'pie', 'flowchart '
            ]
            if not any(content.strip().startswith(start) for start in valid_starts):
                errors.append("Invalid Mermaid diagram type.")

            # Check for common syntax issues
            if '-->' in content and not re.search(r'[\w\s]-->[\w\s]', content):
                warnings.append("Possible syntax error in arrow notation.")

            if '==>' in content:
                warnings.append("Invalid arrow notation, use '-->' instead.")

        except Exception as e:
            errors.append(f"Mermaid validation error: {str(e)}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_react(self, content: str) -> ValidationResult:
        """Validate React component content."""
        self.logger.debug("Validating React component.")
        errors = []
        warnings = []

        try:
            # Basic validation
            if not content.strip():
                errors.append("React component cannot be empty.")

            # Check for export default
            if "export default" not in content:
                errors.append("React component must have a default export.")

            # Check for invalid Tailwind classes
            if re.search(r'className=["\'][^"\']*\[.*?\][^"\']*["\']', content):
                errors.append("Arbitrary Tailwind values are not allowed.")

            # Check for props validation
            if "props" in content and "PropTypes" not in content:
                warnings.append("Consider adding PropTypes for component props.")

            # Check for hooks usage
            if "useState" in content or "useEffect" in content:
                if not re.search(r'import\s+{\s*useState\s*,\s*useEffect\s*}\s+from\s+[\'"]react[\'"]', content):
                    warnings.append("Hooks should be imported from 'react'.")

            # Check for accessibility
            interactive_elements = re.findall(r'<(button|a|input|select|textarea)[^>]*>', content)
            for element in interactive_elements:
                if not re.search(r'aria-[\w-]+="[^"]+"', element):
                    warnings.append(f"Consider adding ARIA attributes to <{element}> for accessibility.")

        except Exception as e:
            errors.append(f"React validation error: {str(e)}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_chart(self, content: str) -> ValidationResult:
        """Validate chart configuration."""
        self.logger.debug("Validating chart configuration.")
        errors = []
        warnings = []

        try:
            config = json.loads(content)
            required_keys = {'type', 'data', 'options'}
            if not required_keys.issubset(config.keys()):
                missing = required_keys - config.keys()
                errors.append(f"Chart configuration missing keys: {', '.join(missing)}")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {str(e)}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )



    # =====================
    # Optimizers
    # =====================

    def _optimize_svg(self, content: str) -> str:
        """Optimize SVG content."""
        self.logger.debug("Optimizing SVG content.")
        try:
            # Remove comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            # Optimize numbers
            content = re.sub(r'(\d+\.\d{2})\d+', r'\1', content)
            
            # Remove empty groups
            content = re.sub(r'<g[^>]*>\s*</g>', '', content)
            
            # Remove unnecessary spaces in path data
            def optimize_path(match):
                return 'd="' + re.sub(r'\s+', ' ', match.group(1).strip()) + '"'
            
            content = re.sub(r'd="([^"]+)"', optimize_path, content)
            
            return content
        except Exception as e:
            self.logger.error(f"SVG optimization failed: {str(e)}")
            raise ArtifactError(f"SVG optimization failed: {str(e)}")

    def _optimize_mermaid(self, content: str) -> str:
        """Optimize Mermaid diagram content."""
        self.logger.debug("Optimizing Mermaid diagram.")
        try:
            # Remove empty lines
            lines = [line for line in content.split('\n') if line.strip()]
            
            # Remove comments
            lines = [line for line in lines if not line.strip().startswith('%')]
            
            return '\n'.join(lines)
        except Exception as e:
            self.logger.error(f"Mermaid optimization failed: {str(e)}")
            raise ArtifactError(f"Mermaid optimization failed: {str(e)}")

    def _optimize_react(self, content: str) -> str:
        """Optimize React component content."""
        self.logger.debug("Optimizing React component.")
        try:
            # Remove console.log statements
            content = re.sub(r'\s*console\.log\([^)]*\);?\n?', '', content)
            
            # Optimize imports by sorting
            def optimize_import(match):
                items = match.group(1).split(',')
                items = sorted(item.strip() for item in items)
                return f"import {{ {', '.join(items)} }} from 'react';"
            
            content = re.sub(r'import {([^}]+)} from \'react\';', optimize_import, content)
            
            return content
        except Exception as e:
            self.logger.error(f"React optimization failed: {str(e)}")
            raise ArtifactError(f"React optimization failed: {str(e)}")

    def _optimize_chart(self, content: str) -> str:
        """Optimize chart configuration."""
        self.logger.debug("Optimizing chart configuration.")
        try:
            # Remove unnecessary whitespace
            content = re.sub(r'\s+', ' ', content)
            return content
        except Exception as e:
            self.logger.error(f"Chart optimization failed: {str(e)}")
            raise ArtifactError(f"Chart optimization failed: {str(e)}")

    # =====================
    # Accessibility Validators
    # =====================

    def validate_svg_accessibility(self, content: str) -> List[str]:
        """Validate SVG accessibility."""
        self.logger.debug("Validating SVG accessibility.")
        issues = []
        
        # Check for title
        if '<title>' not in content:
            issues.append("SVG should include a <title> element.")
            
        # Check for description
        if '<desc>' not in content:
            issues.append("SVG should include a <desc> element.")
            
        # Check for ARIA attributes
        if 'role=' not in content:
            issues.append("SVG should specify a role attribute.")
            
        # Check for interactive elements
        interactive_elements = re.findall(r'<(a|button)[^>]*>', content, re.IGNORECASE)
        for element in interactive_elements:
            if not re.search(r'aria-label=["\'][^"\']+["\']', element, re.IGNORECASE):
                issues.append(f"<{element}> should have an aria-label for accessibility.")
                
        return issues

    def validate_react_accessibility(self, content: str) -> List[str]:
        """Validate React component accessibility."""
        self.logger.debug("Validating React component accessibility.")
        issues = []
        
        # Check for semantic HTML
        if re.search(r'<div[^>]*>', content) and not re.search(r'<(header|footer|main|nav|section|article|aside)>', content):
            issues.append("Consider using semantic HTML elements instead of excessive <div> tags.")
        
        # Check for image alt text
        images = re.findall(r'<img[^>]+>', content, re.IGNORECASE)
        for img in images:
            if not re.search(r'alt=["\']([^"\']+)["\']', img, re.IGNORECASE):
                issues.append("Images must have alt text for accessibility.")
        
        # Check for button accessibility
        buttons = re.findall(r'<button[^>]+>', content, re.IGNORECASE)
        for button in buttons:
            if not re.search(r'aria-label=["\']([^"\']+)["\']', button, re.IGNORECASE):
                issues.append("Buttons should have aria-labels or meaningful content.")
        
        return issues

    # =====================
    # Utilities
    # =====================

    def _generate_checksum(self, content: str) -> str:
        """Generate checksum for content."""
        import hashlib
        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        self.logger.debug(f"Generated checksum: {checksum}")
        return checksum

    def _format_attributes(self, attrs: Dict[str, Any]) -> str:
        """Format element attributes."""
        return ' '.join(f'{k}="{v}"' for k, v in attrs.items())

    # =====================
    # Extensibility
    # =====================

    def add_generator(self,
                     artifact_type: ArtifactType,
                     generator: callable,
                     validator: Optional[callable] = None,
                     formatter: Optional[callable] = None,
                     optimizer: Optional[callable] = None) -> None:
        """Add a custom artifact generator."""
        self.generators[artifact_type] = generator
        if validator:
            self.validators[artifact_type] = validator
        if formatter:
            self.formatters[artifact_type] = formatter
        if optimizer:
            self.optimizers[artifact_type] = optimizer
        self.logger.info(f"Added custom generator for {artifact_type.value}.")

    def remove_generator(self, artifact_type: ArtifactType) -> bool:
        """Remove an artifact generator."""
        removed = False
        if artifact_type in self.generators:
            del self.generators[artifact_type]
            removed = True
        if artifact_type in self.validators:
            del self.validators[artifact_type]
        if artifact_type in self.formatters:
            del self.formatters[artifact_type]
        if artifact_type in self.optimizers:
            del self.optimizers[artifact_type]
        if removed:
            self.logger.info(f"Removed generator for {artifact_type.value}.")
        return removed
