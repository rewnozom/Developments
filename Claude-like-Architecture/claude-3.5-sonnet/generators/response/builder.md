### **`builder.py` Overview**

#### **1. `ResponseConfig`**
- A dataclass defining configuration options for generating responses.
- Key attributes:
  - **`response_type`**: Type of the response (e.g., TEXT, HTML, MARKDOWN, CODE).
  - **`max_length`**: Optional maximum length for the response.
  - **`style_guide`**: Guidelines for formatting the response.
  - **`include_metadata`**: Whether to include metadata in the response.
  - **`validation_rules`**: Custom validation rules.
  - **`custom_settings`**: Additional custom configurations.

#### **2. `ResponseBuilder`**
- The main class that provides methods to build, format, validate, and enhance responses.

---

### **Key Methods**

#### **`build_response(content, response_type, metadata)`**
- Generates a response by:
  1. Formatting the content using `_format_content`.
  2. Validating the formatted content with `_validate_content`.
  3. Enhancing the content via `_enhance_content`.
  4. Creating and returning a `Response` object with metadata.

#### **`_initialize_processors()`**
- Initializes processors for:
  - **Formatting**: `_format_*` methods format content based on response type.
  - **Validation**: `_validate_*` methods validate the content for specific response types.
  - **Enhancement**: `_enhance_*` methods improve content based on specific requirements.

---

### **Formatting Processors**

1. **`_format_text(content)`**
   - Strips unnecessary spaces and formats paragraphs.
   - Applies length limits if specified.

2. **`_format_html(content)`**
   - Indents HTML tags for readability.
   - Ensures proper nesting of tags.

3. **`_format_markdown(content)`**
   - Formats headers, lists, and code blocks for Markdown.

4. **`_format_code(content)`**
   - Ensures consistent indentation and removes excessive blank lines.
   - Supports customization based on a style guide (e.g., max line length, indentation size).

---

### **Validation Processors**

1. **`_validate_text(content)`**
   - Ensures content is not empty.
   - Checks for length violations and malformed sentences.

2. **`_validate_html(content)`**
   - Validates tag matching and nesting integrity.
   - Detects unclosed or improperly nested tags.

3. **`_validate_markdown(content)`**
   - Ensures code blocks are properly closed.
   - Validates header syntax and formatting.

4. **`_validate_code(content)`**
   - Validates code syntax using Python's `ast` module.
   - Checks for indentation consistency and other common issues.

---

### **Enhancement Processors**

1. **`_enhance_text(content)`**
   - Fixes common punctuation issues.
   - Adds proper spacing after punctuation marks.

2. **`_enhance_html(content)`**
   - Adds accessibility attributes (e.g., `alt` for images, `aria-label` for buttons).

3. **`_enhance_markdown(content)`**
   - Converts URLs into reference links.
   - Ensures proper formatting of inline elements.

4. **`_enhance_code(content)`**
   - Adds basic docstrings if missing.
   - Prepares code with annotations or warnings if needed.

---

### **Additional Utilities**

1. **`_truncate_text(text, max_length)`**
   - Truncates text while preserving word boundaries.
   - Appends ellipsis (`...`) to truncated content.

2. **`_enhance_img_tag(attributes)`**
   - Adds `alt` attributes to `<img>` tags for accessibility.

3. **`_enhance_anchor_tag(attributes)`**
   - Adds `aria-label` to `<a>` tags if missing.

4. **`_enhance_button_tag(attributes)`**
   - Adds accessibility attributes to `<button>` tags.

---
