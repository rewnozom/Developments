### **`tokens.py` Overview**


#### **1. `TokenType` (Enum)**
- Defines different types of tokens:
  - **PROMPT**: Tokens for prompts.
  - **COMPLETION**: Tokens for generated completions.
  - **CONTEXT**: Tokens used for contextual information.
  - **TOTAL**: Total tokens available.

#### **2. `TokenUsage` (Data Class)**
- Represents an individual token allocation:
  - **`count`**: Number of tokens allocated.
  - **`type`**: Type of tokens.
  - **`timestamp`**: Time when tokens were allocated.
  - **`metadata`**: Additional information about the allocation.

#### **3. `TokenManager`**
- Core class for managing tokens:
  - Tracks usage by type.
  - Enforces limits per token type.
  - Provides methods for querying and resetting usage.
  
---

### **Key Features**

#### **1. Token Allocation**
- **Method**: `allocate_tokens(count, token_type, metadata)`
  - Allocates tokens for a specific type.
  - Validates if the requested allocation is within the limit.
  - Tracks the allocation as a `TokenUsage` instance.

#### **2. Token Availability**
- **Method**: `get_available_tokens(token_type)`
  - Returns the remaining number of tokens available for a given type.

- **Method**: `can_allocate(count, token_type)`
  - Checks if a given number of tokens can be allocated without exceeding the limit.

#### **3. Usage Tracking**
- **Method**: `get_current_usage(token_type)`
  - Returns the current token usage for a specified type.

- **Method**: `get_usage_history(token_type, start_time, end_time)`
  - Retrieves historical token usage within a time range.

- **Method**: `get_usage_stats()`
  - Provides a summary of token usage:
    - Total allocated tokens.
    - Current usage by type.
    - Remaining tokens by type.

#### **4. Usage Reset**
- **Method**: `reset_usage(token_type)`
  - Clears usage for a specific token type or all types.

#### **5. Token Limits**
- **Method**: `update_limits(token_type, new_limit)`
  - Updates the token limit for a specific type, ensuring it doesn’t violate current usage or the overall max limit.

---

### **Error Handling**

1. **`TokenError`**: Base class for token-related errors.
2. **Specific Errors**:
   - **`TokenLimitError`**: Raised when a token limit is exceeded.
     - Includes information about requested tokens and available tokens.
   - **`TokenTypeError`**: Raised for invalid token types.

