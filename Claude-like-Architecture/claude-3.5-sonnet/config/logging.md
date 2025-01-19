### Summary of `config/logging.py`

1. **`setup_logging` Function**:
   - Configures logging for the application.
   - Adds console and file handlers.
   - Supports rotating logs with configurable size and backup count.
   - Default log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.

2. **`LogFormatter` Class**:
   - Extends `logging.Formatter`.
   - Adds support for including custom `extra` fields in log messages.
   - Formats log records with additional context, like JSON-encoded metadata.

3. **`LogManager` Class**:
   - Manages logging configuration, including handlers for console, file, and error logs.
   - Provides functionality to:
     - Dynamically update log levels.
     - Add and remove handlers.
     - Rotate and archive logs.
     - Clean up old logs based on age.
   - Supports loading configurations from JSON or YAML files.

4. **Additional Features**:
   - **Error Handling**:
     - Ensures robust log management even if the configuration fails.
   - **Archive and Cleanup**:
     - Moves logs to an archive directory and cleans up old logs.
   - **Dynamic Handler Management**:
     - Enables adding/removing custom handlers at runtime.
