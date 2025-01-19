### Summary

1. **Retry and Error Handling**: 
   - `retry_operation` retries a function with exponential backoff.
   - `safe_execute` executes a function safely, providing a default value on failure.

2. **Text Manipulation**: 
   - Functions for tokenization (`calculate_token_length`, `text_to_tokens`), text truncation (`truncate_text`), URL extraction (`extract_urls`), and cleaning text (`clean_text`).

3. **File I/O**: 
   - Functions for reading and writing JSON files (`load_json_file`, `save_json_file`).

4. **Date and Time Utilities**: 
   - Conversions between timestamps and datetime objects (`timestamp_to_datetime`, `datetime_to_timestamp`).

5. **Directory Operations**:
   - Functions for creating and removing directories (`create_directory`, `remove_directory`).

6. **Miscellaneous**: 
   - `chunks` for splitting lists into smaller parts.
