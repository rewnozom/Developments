# generators/artifacts/markdown.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
import re
from models.artifacts import (
    Artifact,
    ArtifactType,
    ArtifactMetadata,
    ArtifactError,
    ValidationResult
)

@dataclass
class MarkdownGenerationConfig:
    """Configuration for markdown generation."""
    style_guide: Optional[Dict[str, Any]] = None
    max_length: Optional[int] = None
    toc_enabled: bool = True
    link_validation: bool = True
    image_validation: bool = True
    formatting_rules: Dict[str, Any] = None
    custom_extensions: List[str] = None

class MarkdownGenerator:
    """Generator for markdown artifacts."""

    def __init__(self, config: Optional[MarkdownGenerationConfig] = None):
        self.config = config or MarkdownGenerationConfig()
        self.processors: Dict[str, callable] = {}
        self.validators: Dict[str, callable] = {}
        self._initialize_processors()

    def generate_markdown_artifact(self,
                                content: str,
                                identifier: str,
                                title: str,
                                metadata: Optional[Dict[str, Any]] = None) -> Artifact:
        """Generate a markdown artifact."""
        try:
            # Validate inputs
            if not content:
                raise ArtifactError("Markdown content cannot be empty")
                
            if not identifier:
                raise ArtifactError("Artifact identifier cannot be empty")
                
            if not title:
                raise ArtifactError("Artifact title cannot be empty")
                
            if metadata is not None and not isinstance(metadata, dict):
                raise ArtifactError("Metadata must be a dictionary")

            # Process and format content
            try:
                processed_content = self._process_content(content)
            except Exception as e:
                raise ArtifactError(f"Content processing failed: {str(e)}")

            # Validate content
            validation_result = self._validate_content(processed_content)
            if not validation_result.valid:
                raise ArtifactError(
                    f"Markdown validation failed: {', '.join(validation_result.errors)}"
                )

            try:
                # Create metadata
                artifact_metadata = ArtifactMetadata(
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    version="1.0.0",
                    creator="MarkdownGenerator",
                    size=len(processed_content.encode('utf-8')),
                    checksum=self._generate_checksum(processed_content),
                    custom_data=metadata or {}
                )
            except Exception as e:
                raise ArtifactError(f"Failed to create artifact metadata: {str(e)}")

            # Create artifact
            artifact = Artifact(
                type=ArtifactType.MARKDOWN,
                content=processed_content,
                identifier=identifier,
                title=title,
                metadata=artifact_metadata,
                validation=validation_result
            )

            return artifact

        except ArtifactError:
            raise
        except Exception as e:
            raise ArtifactError(f"Markdown generation failed: {str(e)}")

    def _initialize_processors(self) -> None:
        """Initialize markdown processors."""
        # Content processors
        self.processors.update({
            'headers': self._process_headers,
            'links': self._process_links,
            'images': self._process_images,
            'lists': self._process_lists,
            'code_blocks': self._process_code_blocks,
            'tables': self._process_tables
        })

        # Content validators
        self.validators.update({
            'structure': self._validate_structure,
            'links': self._validate_links,
            'images': self._validate_images,
            'formatting': self._validate_formatting
        })

    def _process_content(self, content: str) -> str:
        """Process markdown content."""
        processed_content = content

        # Apply processors
        for processor in self.processors.values():
            processed_content = processor(processed_content)

        # Add table of contents if enabled
        if self.config.toc_enabled:
            processed_content = self._add_table_of_contents(processed_content)

        return processed_content

    def _validate_content(self, content: str) -> ValidationResult:
        """Validate markdown content."""
        errors = []
        warnings = []

        # Apply validators
        for validator in self.validators.values():
            result = validator(content)
            errors.extend(result.get('errors', []))
            warnings.extend(result.get('warnings', []))

        # Check length
        if self.config.max_length and len(content) > self.config.max_length:
            warnings.append(f"Content exceeds maximum length of {self.config.max_length} characters")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _process_headers(self, content: str) -> str:
        """Process markdown headers."""
        lines = content.split('\n')
        processed_lines = []
        header_levels = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

        for line in lines:
            # Process ATX headers (#)
            header_match = re.match(r'^(#{1,6})\s*(.+?)(?:\s*#+\s*)?$', line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                header_levels[level] += 1
                processed_lines.append(f"{'#' * level} {text}")
                continue

            # Process Setext headers (=== or ---)
            if line.strip() and processed_lines:
                if line.strip('=') == '':
                    processed_lines[-1] = f"# {processed_lines[-1]}"
                    continue
                elif line.strip('-') == '':
                    processed_lines[-1] = f"## {processed_lines[-1]}"
                    continue

            processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _process_links(self, content: str) -> str:
        """Process markdown links."""
        def process_link(match):
            text = match.group(1).strip()
            url = match.group(2).strip()
            title = match.group(3).strip() if match.group(3) else ''
            
            # Format URL
            url = url.replace(' ', '%20')
            
            # Add title if present
            if title:
                return f'[{text}]({url} "{title}")'
            return f'[{text}]({url})'

        # Process inline links
        content = re.sub(r'\[([^\]]+)\]\(([^)"]+)(?:\s+"([^"]+)")?\)',
                        process_link, content)

        # Process reference links
        references = {}
        def collect_reference(match):
            label = match.group(1).lower()
            url = match.group(2)
            title = match.group(3) if match.group(3) else ''
            references[label] = (url, title)
            return ''

        content = re.sub(r'^\[([^\]]+)\]:\s*(\S+)(?:\s+"([^"]+)")?\s*$',
                        collect_reference, content, flags=re.MULTILINE)

        # Sort and append references
        if references:
            content = content.rstrip() + '\n\n'
            for label in sorted(references):
                url, title = references[label]
                if title:
                    content += f'[{label}]: {url} "{title}"\n'
                else:
                    content += f'[{label}]: {url}\n'

        return content

    def _process_images(self, content: str) -> str:
        """Process markdown images."""
        def process_image(match):
            alt_text = match.group(1).strip()
            src = match.group(2).strip()
            title = match.group(3).strip() if match.group(3) else ''
            
            # Format source URL
            src = src.replace(' ', '%20')
            
            # Add title if present
            if title:
                return f'![{alt_text}]({src} "{title}")'
            return f'![{alt_text}]({src})'

        # Process inline images
        return re.sub(r'!\[([^\]]+)\]\(([^)"]+)(?:\s+"([^"]+)")?\)',
                     process_image, content)

    def _process_lists(self, content: str) -> str:
        """Process markdown lists."""
        lines = content.split('\n')
        processed_lines = []
        list_indent = 0
        list_type = None  # 'ul' or 'ol'

        for line in lines:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            # Detect list items
            ul_match = re.match(r'^[-*+]\s', stripped)
            ol_match = re.match(r'^\d+\.\s', stripped)

            if ul_match or ol_match:
                current_type = 'ul' if ul_match else 'ol'
                
                # Adjust indentation for nested lists
                if list_type != current_type or indent != list_indent:
                    list_type = current_type
                    list_indent = indent

                # Format list item
                if list_type == 'ul':
                    line = ' ' * indent + '- ' + stripped[2:].strip()
                else:
                    line = ' ' * indent + '1. ' + stripped[stripped.find(' '):].strip()

            processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _process_code_blocks(self, content: str) -> str:
        """Process markdown code blocks."""
        lines = content.split('\n')
        processed_lines = []
        in_code_block = False
        code_fence = ''

        for line in lines:
            # Check for code fence
            fence_match = re.match(r'^(`{3,}|~{3,})', line)
            
            if fence_match:
                if not in_code_block:
                    # Start code block
                    code_fence = fence_match.group(1)
                    in_code_block = True
                    # Standardize to three backticks
                    line = '```' + line[len(code_fence):]
                elif fence_match.group(1)[0] == code_fence[0]:
                    # End code block
                    in_code_block = False
                    code_fence = ''
                    line = '```'

            # Process indented code blocks
            elif not in_code_block and line.startswith('    '):
                # Convert to fenced code block
                processed_lines.append('```')
                in_code_block = True
                code_fence = 'indent'
                line = line[4:]

            # End indented code block
            elif in_code_block and code_fence == 'indent' and not line.startswith('    '):
                if line.strip():
                    processed_lines.append('```')
                    in_code_block = False
                    code_fence = ''

            processed_lines.append(line)

        # Close any open code block
        if in_code_block:
            processed_lines.append('```')

        return '\n'.join(processed_lines)

    def _process_tables(self, content: str) -> str:
        """Process markdown tables."""
        lines = content.split('\n')
        processed_lines = []
        in_table = False
        column_widths = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Detect table header separator
            if re.match(r'^[|]?\s*[-:]+[-| :]+$', stripped):
                if i > 0 and not in_table:
                    # Previous line was header
                    in_table = True
                    # Calculate column widths
                    header = lines[i-1].strip()
                    cells = [cell.strip() for cell in header.split('|')[1:-1]]
                    column_widths = [max(3, len(cell)) for cell in cells]
                    # Format header
                    processed_lines[-1] = self._format_table_row(cells, column_widths)
                    # Format separator
                    line = self._format_table_separator(column_widths)
            
            elif in_table:
                if not stripped or not stripped.startswith('|'):
                    in_table = False
                else:
                    # Format table row
                    cells = [cell.strip() for cell in stripped.split('|')[1:-1]]
                    line = self._format_table_row(cells, column_widths)

            processed_lines.append(line)

        return '\n'.join(processed_lines)

    def _format_table_row(self, cells: List[str], widths: List[int]) -> str:
        """Format table row with consistent column widths."""
        formatted_cells = []
        for cell, width in zip(cells, widths):
            formatted_cells.append(f" {cell:<{width}} ")
        return f"|{'|'.join(formatted_cells)}|"

    def _format_table_separator(self, widths: List[int]) -> str:
        """Format table separator row."""
        separators = ['-' * width for width in widths]
        return f"|:{'-' * (widths[0]-1)}|" + \
               '|'.join(f"{'-' * (w-2)}:" for w in widths[1:]) + \
               f"|"

    def _add_table_of_contents(self, content: str) -> str:
        """Add table of contents to markdown content."""
        headers = []
        lines = content.split('\n')
        
        # Extract headers
        for line in lines:
            header_match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*#+\s*)?$', line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                headers.append((level, text))

        if not headers:
            return content

        # Generate ToC
        toc = ["# Table of Contents\n"]
        for level, text in headers:
            # Create anchor link
            anchor = text.lower().replace(' ', '-')
            anchor = re.sub(r'[^\w\-]', '', anchor)
            indent = '  ' * (level - 1)
            toc.append(f"{indent}- [{text}](#{anchor})")

        # Insert ToC after first header if exists
        if lines and re.match(r'^#\s+', lines[0]):
            return '\n'.join(lines[:1] + [''] + toc + [''] + lines[1:])
        return '\n'.join(toc + [''] + lines)

    def _validate_structure(self, content: str) -> Dict[str, List[str]]:
        """Validate markdown structure."""
        errors = []
        warnings = []

        # Check header hierarchy
        headers = []
        for line in content.split('\n'):
            header_match = re.match(r'^(#{1,6})\s+', line)
            if header_match:
                level = len(header_match.group(1))
                headers.append(level)

        if headers:
            if headers[0] != 1:
                warnings.append("Document should start with an H1 header")
            for i in range(1, len(headers)):
                if headers[i] > headers[i-1] + 1:
                    errors.append(f"Header level jumps from H{headers[i-1]} to H{headers[i]}")

        # Check for empty sections
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(r'^#+\s+', line):
                next_content = next((l for l in lines[i+1:] if l.strip()), '')
                if not next_content or re.match(r'^#+\s+', next_content):
                    warnings.append(f"Empty section: {line.strip()}")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_links(self, content: str) -> Dict[str, List[str]]:
        """Validate markdown links."""
        errors = []
        warnings = []

        # Check inline links
        inline_links = re.finditer(r'\[([^\]]+)\]\(([^)"]+)(?:\s+"[^"]+")?\)', content)

# generators/artifacts/markdown.py (continued)
        for link in inline_links:
            text = link.group(1)
            url = link.group(2)

            # Check for empty link text
            if not text.strip():
                errors.append(f"Empty link text for URL: {url}")

            # Check for malformed URLs
            if ' ' in url and '%20' not in url:
                errors.append(f"URL contains unescaped spaces: {url}")

            # Check for relative URLs
            if not url.startswith(('http://', 'https://', '/', '#', 'mailto:')):
                warnings.append(f"Relative URL used: {url}")

        # Check reference links
        refs = {}
        for match in re.finditer(r'^\[([^\]]+)\]:\s*(\S+)(?:\s+"[^"]+")?\s*$', content, re.MULTILINE):
            label = match.group(1).lower()
            url = match.group(2)
            refs[label] = url

        # Check for undefined references
        for match in re.finditer(r'\[([^\]]+)\]\[([^\]]*)\]', content):
            text = match.group(1)
            label = match.group(2) or text
            label = label.lower()
            
            if label not in refs:
                errors.append(f"Undefined reference: [{label}]")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_images(self, content: str) -> Dict[str, List[str]]:
        """Validate markdown images."""
        errors = []
        warnings = []

        # Check inline images
        for match in re.finditer(r'!\[([^\]]*)\]\(([^)"]+)(?:\s+"[^"]+")?\)', content):
            alt_text = match.group(1)
            src = match.group(2)

            # Check for empty alt text
            if not alt_text.strip():
                warnings.append(f"Missing alt text for image: {src}")

            # Check for malformed URLs
            if ' ' in src and '%20' not in src:
                errors.append(f"Image URL contains unescaped spaces: {src}")

            # Check for supported file types
            if not any(src.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                warnings.append(f"Possibly unsupported image type: {src}")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _validate_formatting(self, content: str) -> Dict[str, List[str]]:
        """Validate markdown formatting."""
        errors = []
        warnings = []

        # Check for consistent emphasis style
        asterisk_emphasis = len(re.findall(r'\*[^\*]+\*', content))
        underscore_emphasis = len(re.findall(r'_[^_]+_', content))
        if asterisk_emphasis and underscore_emphasis:
            warnings.append("Mixed emphasis styles used (* and _)")

        # Check for consistent strong emphasis style
        asterisk_strong = len(re.findall(r'\*\*[^\*]+\*\*', content))
        underscore_strong = len(re.findall(r'__[^_]+__', content))
        if asterisk_strong and underscore_strong:
            warnings.append("Mixed strong emphasis styles used (** and __)")

        # Check for proper list indentation
        lines = content.split('\n')
        list_indent = 0
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            if re.match(r'^[-*+]\s', stripped) or re.match(r'^\d+\.\s', stripped):
                if indent % 2 != 0:
                    errors.append(f"Improper list indentation at line {i+1}")
                if indent - list_indent > 2:
                    errors.append(f"List indentation jump too large at line {i+1}")
                list_indent = indent

        # Check for proper code fence usage
        in_code_block = False
        fence_char = None
        for i, line in enumerate(lines):
            if line.startswith('```') or line.startswith('~~~'):
                if not in_code_block:
                    in_code_block = True
                    fence_char = line[0]
                    if len(set(line)) > 1 and not re.match(r'^[`~]+\w+$', line):
                        warnings.append(f"Unclear code block language specification at line {i+1}")
                else:
                    if line[0] != fence_char:
                        errors.append(f"Mismatched code fence at line {i+1}")
                    in_code_block = False

        if in_code_block:
            errors.append("Unclosed code block")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def _generate_checksum(self, content: str) -> str:
        """Generate checksum for content."""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def cleanup_markdown(self, content: str) -> str:
        """Clean up markdown content."""
        # Remove multiple blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Ensure single space after list markers
        content = re.sub(r'^([-*+])\s+', r'\1 ', content, flags=re.MULTILINE)
        content = re.sub(r'^(\d+\.)\s+', r'\1 ', content, flags=re.MULTILINE)

        # Normalize emphasis markers
        if self.config.formatting_rules and 'emphasis_style' in self.config.formatting_rules:
            style = self.config.formatting_rules['emphasis_style']
            if style == 'asterisk':
                content = re.sub(r'_([^_]+)_', r'*\1*', content)
            elif style == 'underscore':
                content = re.sub(r'\*([^\*]+)\*', r'_\1_', content)

        # Normalize strong emphasis markers
        if self.config.formatting_rules and 'strong_emphasis_style' in self.config.formatting_rules:
            style = self.config.formatting_rules['strong_emphasis_style']
            if style == 'asterisk':
                content = re.sub(r'__([^_]+)__', r'**\1**', content)
            elif style == 'underscore':
                content = re.sub(r'\*\*([^\*]+)\*\*', r'__\1__', content)

        # Ensure single space after headers
        content = re.sub(r'^(#+)(\S)', r'\1 \2', content, flags=re.MULTILINE)

        # Clean up spaces around code spans
        content = re.sub(r'\s*`([^`]+)`\s*', r' `\1` ', content)

        # Normalize horizontal rules
        content = re.sub(r'^[-*_]{3,}\s*$', '---', content, flags=re.MULTILINE)

        return content.strip() + '\n'

    def format_markdown(self, content: str) -> str:
        """Format markdown content according to style guide."""
        if not self.config.style_guide:
            return content

        formatted = content

        # Apply header style
        if 'header_style' in self.config.style_guide:
            style = self.config.style_guide['header_style']
            if style == 'atx':
                # Convert Setext headers to ATX
                lines = formatted.split('\n')
                for i in range(1, len(lines)):
                    if lines[i].strip('=') == '':
                        lines[i-1] = f"# {lines[i-1]}"
                        lines[i] = ''
                    elif lines[i].strip('-') == '':
                        lines[i-1] = f"## {lines[i-1]}"
                        lines[i] = ''
                formatted = '\n'.join(lines)
            elif style == 'setext':
                # Convert ATX headers to Setext (only for h1 and h2)
                lines = formatted.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# '):
                        lines[i] = line[2:]
                        lines.insert(i+1, '='*len(lines[i]))
                    elif line.startswith('## '):
                        lines[i] = line[3:]
                        lines.insert(i+1, '-'*len(lines[i]))
                formatted = '\n'.join(lines)

        # Apply list style
        if 'list_style' in self.config.style_guide:
            style = self.config.style_guide['list_style']
            if style in ['-', '*', '+']:
                # Convert all unordered list markers to specified style
                formatted = re.sub(r'^([ \t]*)[*+-]', rf'\1{style}', formatted, flags=re.MULTILINE)

        # Apply link style
        if 'link_style' in self.config.style_guide:
            style = self.config.style_guide['link_style']
            if style == 'inline':
                # Convert reference links to inline
                references = {}
                def collect_reference(match):
                    label = match.group(1).lower()
                    url = match.group(2)
                    title = match.group(3) if match.group(3) else None
                    references[label] = (url, title)
                    return ''
                
                formatted = re.sub(r'^\[([^\]]+)\]:\s*(\S+)(?:\s+"([^"]+)")?\s*$',
                                    collect_reference, formatted, flags=re.MULTILINE)
                
                def reference_to_inline(match):
                    text = match.group(1)
                    label = (match.group(2) or text).lower()
                    if label in references:
                        url, title = references[label]
                        if title:
                            return f'[{text}]({url} "{title}")'
                        return f'[{text}]({url})'
                    return match.group(0)
                
                formatted = re.sub(r'\[([^\]]+)\](?:\[([^\]]*)\])',
                                    reference_to_inline, formatted)

        return formatted

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from markdown content."""
        metadata = {}

        # Extract title
        header_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
        if header_match:
            metadata['title'] = header_match.group(1).strip()

        # Extract tags
        tag_matches = re.finditer(r'#(\w+)', content)
        metadata['tags'] = [m.group(1) for m in tag_matches]

        # Extract links
        link_matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
        metadata['links'] = [{'text': m.group(1), 'url': m.group(2)} 
                            for m in link_matches]

        # Extract code block languages
        code_blocks = re.finditer(r'```(\w+)', content)
        metadata['languages'] = list(set(m.group(1) for m in code_blocks if m.group(1)))

        # Count sections
        header_levels = {}
        for match in re.finditer(r'^(#{1,6})\s', content, re.MULTILINE):
            level = len(match.group(1))
            header_levels[level] = header_levels.get(level, 0) + 1
        metadata['section_counts'] = header_levels

        return metadata
