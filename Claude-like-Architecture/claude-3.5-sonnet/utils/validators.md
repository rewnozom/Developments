### Summary


1. **General Validation**:
   - `validate_input` dynamically validates data based on the specified type using predefined validation functions.
   - Validation functions include `validate_text`, `validate_number`, `validate_email`, `validate_url`, `validate_json`, `validate_path`, and `validate_datetime`.

2. **Schema Validation**:
   - `validate_schema` and `validate_value` support JSON schema-based validation, enabling flexible and detailed data integrity checks.

3. **Predefined Validators**:
   - Common validators, such as `validate_positive_number`, `validate_percentage`, and `validate_year`, are readily available for reuse.
   - Specialized email and URL validators (`validate_email_strict`, `validate_http_url`, etc.) cover specific use cases.

4. **Utility Validators**:
   - Combine multiple validators with `validate_all` and `validate_any` to apply complex validation logic.

5. **Error Handling**:
   - Custom exceptions (`ValidationError`, `SchemaValidationError`, `ValueError`) provide detailed error reporting and differentiation between validation types.

6. **Validator Factories**:
   - `create_validator` simplifies the creation of reusable validators with preset parameters.
