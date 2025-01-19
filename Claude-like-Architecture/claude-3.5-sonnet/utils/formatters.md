
### Key Functions

#### 1. `format_response`
- **Purpose:** Acts as a dispatcher to choose the correct formatting function based on the `format_type`.
- **Parameters:**
  - `content`: The content to be formatted.
  - `format_type`: The desired output type (`text`, `code`, `markdown`, `html`, `json`).
  - `metadata`: Optional parameters to customize the formatting.
- **Output:** Returns formatted content.

#### 2. `format_text`
- **Purpose:** Cleans and normalizes plain text content.
- **Key Operations:**
  - Strips extra whitespace.
  - Replaces multiple spaces with a single space.

#### 3. `format_code`
- **Purpose:** Formats code content.
- **Key Operations:**
  - Adds code block markers for Markdown.
  - Optionally includes a language specifier.

#### 4. `format_markdown`
- **Purpose:** Ensures consistent formatting for Markdown content.
- **Key Operations:**
  - Normalizes headers (`#`, `##`, etc.).
  - Ensures list markers (`-`, `*`, `+`) are uniform.
  - Cleans code block delimiters.

#### 5. `format_html`
- **Purpose:** Escapes and wraps content in specified HTML tags.
- **Key Operations:**
  - Escapes HTML special characters.
  - Allows customization of wrapping tags and CSS classes.

#### 6. `format_json`
- **Purpose:** Formats JSON data.
- **Key Operations:**
  - Parses and indents JSON for readability.
  - Handles both string and dictionary inputs.

#### 7. `format_timestamp`
- **Purpose:** Converts a timestamp into a human-readable string.
- **Key Operations:**
  - Handles Unix timestamps and `datetime` objects.
  - Customizable format string.

#### 8. `format_number`
- **Purpose:** Formats numbers with proper separators and decimal places.
- **Key Operations:**
  - Adds thousands separators.
  - Handles decimal precision.

#### 9. `format_size`
- **Purpose:** Converts byte sizes into human-readable units.
- **Key Operations:**
  - Supports binary (KiB, MiB) or decimal (KB, MB) formats.
  - Automatically adjusts units.

#### 10. `format_duration`
- **Purpose:** Formats a duration in seconds into a readable string (e.g., "2h 30m").
- **Key Operations:**
  - Breaks down seconds into days, hours, minutes, and seconds.
  - Optionally excludes seconds for simplicity.

### Custom Exception

#### `FormatError`
- **Purpose:** Raised for errors encountered during formatting.

---

### Use Cases
1. **API Response Formatting:** Use `format_response` to dynamically format responses based on the expected output type.
2. **Data Presentation:** Utilize `format_size` or `format_duration` for displaying system metrics or time data in user-friendly formats.
3. **Code Snippet Display:** Use `format_code` to generate Markdown-compatible code blocks.
4. **Log or Report Generation:** Apply `format_json` and `format_text` for structured and clean log outputs.
