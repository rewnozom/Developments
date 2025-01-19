

### **Core Components**

#### **1. `ContextItem`**
- Represents a single context item with attributes:
  - **`id`**: Unique identifier (UUID) for the item.
  - **`content`**: The actual data stored in the context.
  - **`timestamp`**: Time when the item was added.
  - **`priority`**: Priority level of the item (higher values indicate higher priority).
  - **`ttl`**: Time-to-live in seconds, indicating the item's validity duration.
  - **`metadata`**: Additional information about the item.

#### **2. `ContextManager`**
- Manages the lifecycle of context items, including adding, retrieving, updating, and removing items.
- Supports priority-based context retention, TTL-based expiration, and size-limited storage.

---

### **Key Features**

#### **1. Adding Context**
- **Method**: `add_context(content, priority=0, ttl=None, metadata=None)`
- Adds a new item to the context with optional priority, TTL, and metadata.
- Items with a `priority > 0` are tracked separately in the `priority_items` dictionary.
- Returns the UUID of the added item.

#### **2. Retrieving Context**
- **Method**: `get_context(max_items=None, min_priority=0)`
- Retrieves context items filtered by minimum priority and limited to `max_items`.
- Automatically removes expired items before retrieval.

#### **3. Updating Context**
- **Method**: `update_context(item_id, content=None, priority=None, ttl=None, metadata=None)`
- Updates the properties of a specific context item identified by `item_id`.
- Adjusts priority tracking if the item's priority changes.

#### **4. Removing Context**
- **Method**: `remove_context(item_id)`
- Removes a specific context item by its UUID.

#### **5. Clearing Context**
- **Method**: `clear_context(preserve_priority=True)`
- Clears all context items, optionally preserving high-priority items.

#### **6. Expiration Management**
- **Method**: `_cleanup_expired()`
- Removes expired items from the context and `priority_items`.
- Automatically invoked after adding new items or retrieving context.

#### **7. Context Optimization**
- **Method**: `optimize_context()`
- Removes low-priority items when the context size approaches the maximum limit.

#### **8. Context Information**
- **Methods**:
  - `get_context_size()`: Returns the current number of items in the context.
  - `get_priority_items()`: Returns all high-priority items as a dictionary.

