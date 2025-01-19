# generators/response/formatter.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import re
from models.response import Response, ResponseType

@dataclass
class FormattingConfig:
   """Configuration for response formatting."""
   style_guide: Optional[Dict[str, Any]] = None
   max_length: Optional[int] = None
   formatting_rules: Optional[Dict[str, Any]] = None
   indent_size: int = 2
   line_length: int = 80
   code_style: Optional[str] = None

class ResponseFormatter:
   """Formats response content based on type and style guidelines."""

   def __init__(self, config: Optional[FormattingConfig] = None):
       self.config = config or FormattingConfig()
       self.formatters: Dict[ResponseType, callable] = {}
       self.style_checkers: Dict[ResponseType, callable] = {}
       self._initialize_formatters()

   def format_response(self, 
                      response: Response,
                      format_type: Optional[ResponseType] = None) -> Response:
       """Format response according to type and style guide."""
       try:
           # Determine format type
           format_type = format_type or response.type

           # Get appropriate formatter
           formatter = self.formatters.get(format_type)
           if not formatter:
               return response

           # Apply formatting
           formatted_content = formatter(response.content)

           # Apply style guidelines if available
           if self.config.style_guide:
               formatted_content = self._apply_style_guide(
                   formatted_content,
                   format_type
               )

           # Update response with formatted content
           response.content = formatted_content
           response.metadata.update({
               'formatted': True,
               'format_type': format_type.value,
               'formatting_timestamp': datetime.now().isoformat()
           })

           return response

       except Exception as e:
           raise FormattingError(f"Formatting failed: {str(e)}")

   def _initialize_formatters(self) -> None:
       """Initialize response formatters."""
       self.formatters.update({
           ResponseType.TEXT: self._format_text,
           ResponseType.CODE: self._format_code,
           ResponseType.ERROR: self._format_error,
           ResponseType.FUNCTION: self._format_function
       })

       self.style_checkers.update({
           ResponseType.TEXT: self._check_text_style,
           ResponseType.CODE: self._check_code_style,
           ResponseType.ERROR: self._check_error_style,
           ResponseType.FUNCTION: self._check_function_style
       })

   def _format_text(self, content: str) -> str:
       """Format text content."""
       # Apply basic text formatting
       content = content.strip()

       # Handle line length
       if self.config.line_length:
           content = self._wrap_text(content, self.config.line_length)

       # Handle paragraphs
       content = self._format_paragraphs(content)

       # Handle lists
       content = self._format_lists(content)

       return content

   def _format_code(self, content: str) -> str:
       """Format code content."""
       # Apply code style if specified
       if self.config.code_style == "python":
           return self._format_python_code(content)
       elif self.config.code_style == "javascript":
           return self._format_javascript_code(content)
       
       # Default basic code formatting
       lines = content.split('\n')
       formatted_lines = []
       indent_level = 0
       
       for line in lines:
           stripped = line.strip()
           
           # Adjust indentation for blocks
           if stripped.endswith('{') or stripped.endswith(':'):
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
               indent_level += 1
           elif stripped.startswith('}') or stripped in ['else:', 'elif ', 'except:', 'finally:']:
               indent_level = max(0, indent_level - 1)
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
           else:
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
       
       return '\n'.join(formatted_lines)

   def _format_error(self, content: str) -> str:
       """Format error content."""
       # Standardize error format
       if isinstance(content, dict):
           return self._format_error_dict(content)
       
       # Basic error string formatting
       lines = []
       if ':' in content:
           error_type, message = content.split(':', 1)
           lines.extend([
               error_type.strip(),
               '-' * len(error_type),
               message.strip()
           ])
       else:
           lines.extend([
               'Error',
               '-----',
               content.strip()
           ])
       
       return '\n'.join(lines)

   def _format_function(self, content: str) -> str:
       """Format function content."""
       # Handle function call format
       if isinstance(content, dict):
           return self._format_function_dict(content)
       
       # Basic function string formatting
       content = content.strip()
       if content.startswith('def '):
           return self._format_function_definition(content)
       return self._format_function_call(content)

   def _wrap_text(self, text: str, length: int) -> str:
       """Wrap text to specified length."""
       lines = []
       for paragraph in text.split('\n\n'):
           words = paragraph.split()
           current_line = []
           current_length = 0
           
           for word in words:
               word_length = len(word)
               if current_length + word_length + 1 <= length:
                   current_line.append(word)
                   current_length += word_length + 1
               else:
                   lines.append(' '.join(current_line))
                   current_line = [word]
                   current_length = word_length + 1
           
           if current_line:
               lines.append(' '.join(current_line))
           lines.append('')
       
       return '\n'.join(lines).strip()

   def _format_paragraphs(self, content: str) -> str:
       """Format text paragraphs."""
       paragraphs = content.split('\n\n')
       formatted_paragraphs = []
       
       for paragraph in paragraphs:
           # Remove excess whitespace
           paragraph = ' '.join(paragraph.split())
           
           # Handle special paragraph types
           if paragraph.startswith('- '):
               paragraph = self._format_bullet_list(paragraph)
           elif re.match(r'\d+\.', paragraph):
               paragraph = self._format_numbered_list(paragraph)
               
           formatted_paragraphs.append(paragraph)
           
       return '\n\n'.join(formatted_paragraphs)

   def _format_lists(self, content: str) -> str:
       """Format bullet and numbered lists."""
       lines = content.split('\n')
       formatted_lines = []
       in_list = False
       list_indent = 0
       
       for line in lines:
           if line.lstrip().startswith('- ') or re.match(r'\d+\.', line.lstrip()):
               if not in_list:
                   formatted_lines.append('')
                   in_list = True
               list_indent = len(line) - len(line.lstrip())
               formatted_lines.append(line)
           else:
               if in_list and line.strip():
                   if len(line) - len(line.lstrip()) > list_indent:
                       formatted_lines.append(line)
                   else:
                       in_list = False
                       formatted_lines.extend(['', line])
               else:
                   formatted_lines.append(line)
                   
       return '\n'.join(formatted_lines)

   def _format_bullet_list(self, content: str) -> str:
       """Format bullet list items."""
       lines = content.split('\n')
       return '\n'.join(f"- {line.lstrip('- ')}" for line in lines)

   def _format_numbered_list(self, content: str) -> str:
       """Format numbered list items."""
       lines = content.split('\n')
       formatted_lines = []
       number = 1
       
       for line in lines:
           if re.match(r'\d+\.', line):
               formatted_lines.append(f"{number}. {line.split('.', 1)[1].lstrip()}")
               number += 1
           else:
               formatted_lines.append(line)
               
       return '\n'.join(formatted_lines)

   def _format_python_code(self, content: str) -> str:
       """Format Python code."""
       try:
           import black
           mode = black.Mode(
               line_length=self.config.line_length or 88,
               string_normalization=True,
               is_pyi=False
           )
           return black.format_str(content, mode=mode)
       except ImportError:
           return self._format_code(content)

   def _format_javascript_code(self, content: str) -> str:
       """Format JavaScript code."""
       # Basic JS formatting
       lines = content.split('\n')
       formatted_lines = []
       indent_level = 0
       
       for line in lines:
           stripped = line.strip()
           
           # Handle line endings
           if not stripped.endswith(';') and not stripped.endswith('{') and \
              not stripped.endswith('}') and stripped:
               stripped += ';'
           
           # Handle blocks
           if stripped.endswith('{'):
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
               indent_level += 1
           elif stripped.startswith('}'):
               indent_level = max(0, indent_level - 1)
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
           else:
               formatted_lines.append(' ' * (indent_level * self.config.indent_size) + stripped)
               
       return '\n'.join(formatted_lines)

   def _format_error_dict(self, content: Dict[str, Any]) -> str:
       """Format error dictionary."""
       lines = [
           content.get('type', 'Error'),
           '-' * len(content.get('type', 'Error')),
           content.get('message', ''),
           ''
       ]
       
       if 'details' in content:
           lines.extend([
               'Details:',
               '--------',
               str(content['details'])
           ])
           
       return '\n'.join(lines)

   def _format_function_dict(self, content: Dict[str, Any]) -> str:
       """Format function call dictionary."""
       lines = [
           f"Function: {content.get('name', 'unknown')}",
           '-' * (len(content.get('name', 'unknown')) + 10),
           ''
       ]
       
       if 'args' in content:
           lines.extend([
               'Arguments:',
               '---------'
           ])
           for arg in content['args']:
               lines.append(f"- {arg}")
           lines.append('')
           
       if 'kwargs' in content:
           lines.extend([
               'Keyword Arguments:',
               '-----------------'
           ])
           for key, value in content['kwargs'].items():
               lines.append(f"- {key}: {value}")
               
       return '\n'.join(lines)

   def _format_function_definition(self, content: str) -> str:
       """Format function definition."""
       # Basic formatting for function definitions
       lines = content.split('\n')
       formatted_lines = []
       
       for i, line in enumerate(lines):
           if i == 0:  # Function signature
               formatted_lines.append(line)
           else:
               formatted_lines.append(
                   ' ' * self.config.indent_size + line.strip()
               )
               
       return '\n'.join(formatted_lines)

   def _format_function_call(self, content: str) -> str:
       """Format function call."""
       # Basic formatting for function calls
       parts = content.split('(', 1)
       if len(parts) != 2:
           return content
           
       func_name, args = parts
       args = args.rstrip(')')
       
       # Format arguments
       if ',' in args:
           arg_parts = args.split(',')
           formatted_args = ',\n'.join(
               ' ' * (len(func_name) + 1) + arg.strip()
               for arg in arg_parts
           )
           return f"{func_name}(\n{formatted_args}\n)"
           
       return f"{func_name}({args})"

   def _apply_style_guide(self, content: str, format_type: ResponseType) -> str:
       """Apply style guide rules."""
       style_checker = self.style_checkers.get(format_type)
       if not style_checker:
           return content
           
       issues = style_checker(content)
       for issue in issues:
           if isinstance(issue, tuple):
               rule, fix = issue
               content = fix(content)
               
       return content

   def _check_text_style(self, content: str) -> List[tuple]:
       """Check text style rules."""
       issues = []
       
       # Check sentence spacing
       def fix_sentence_spacing(text):
           return re.sub(r'([.!?])\s*([A-Z])', r'\1  \2', text)
       
       if re.search(r'([.!?])\s*([A-Z])', content):
           issues.append(('sentence_spacing', fix_sentence_spacing))
           
       # Check list consistency
       def fix_list_markers(text):
           return re.sub(r'[*+]\s', '- ', text)
           
       if re.search(r'[*+]\s', content):
           issues.append(('list_markers', fix_list_markers))
           
       return issues

   def _check_code_style(self, content: str) -> List[tuple]:
       """Check code style rules."""
       issues = []
       
       # Check line length
       if self.config.line_length:
           def fix_line_length(text):
               return '\n'.join(
                   line[:self.config.line_length] + ' \\'
                   if len(line) > self.config.line_length else line
                   for line in text.split('\n')
               )
               
           if any(len(line) > self.config.line_length for line in content.split('\n')):
               issues.append(('line_length', fix_line_length))
               
       return issues

   def _check_error_style(self, content: str) -> List[tuple]:
       """Check error style rules."""
       issues = []
       
       # Check error format consistency
       def fix_error_format(text):
           if ':' not in text:
               return f"Error: {text}"
           return text
           
       if ':' not in content:
           issues.append(('error_format', fix_error_format))
           
       return issues

   def _check_function_style(self, content: str) -> List[tuple]:
       """Check function style rules."""
       issues = []
       
       # Check parentheses spacing
       def fix_parentheses_spacing(text):
           text = re.sub(r'\(\s+', '(', text)
           text = re.sub(r'\s+\)', ')', text)
           return text
           
       if re.search(r'\(\s+|\s+\)', content):
           issues.append(('parentheses_spacing', fix_parentheses_spacing))
           
       return issues

class FormattingError(Exception):
   """Raised when formatting fails."""
   pass