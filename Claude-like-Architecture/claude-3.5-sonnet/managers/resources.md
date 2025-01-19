### **`resources.py` Overview**

#### **1. `Resource`**
- Represents a single resource in the system:
  - **`name`**: Identifier for the resource.
  - **`type`**: Resource type (e.g., JSON, YAML, text).
  - **`location`**: Path to the resource file.
  - **`size`**: Size of the resource in bytes.
  - **`loaded`**: Indicates if the resource is currently loaded into memory.
  - **`last_accessed`**: Timestamp of the last access.
  - **`metadata`**: Additional metadata for the resource.

#### **2. `ResourceManager`**
- Handles the registration, loading, and management of resources.
- Key functionalities:
  - **Registration**: Add a new resource to the system.
  - **Loading/Unloading**: Load resources into memory or remove them to save memory.
  - **Updating**: Modify resource content.
  - **Optimization**: Free unused resources to optimize memory usage.
  - **Resource Tracking**: Track resource size, type, and metadata.

---

### **Key Features**

#### **1. Resource Registration**
- **Method**: `register_resource(name, type, location, metadata)`
  - Registers a new resource by creating a `Resource` object.
  - Validates the existence of the resource file and calculates its size.

#### **2. Resource Loading**
- **Method**: `load_resource(name)`
  - Loads a resource into memory, supporting formats like JSON, YAML, and text.
  - Marks the resource as loaded and updates its last accessed time.

#### **3. Resource Unloading**
- **Method**: `unload_resource(name)`
  - Removes a loaded resource from memory to optimize resource usage.

#### **4. Resource Update**
- **Method**: `update_resource(name, content, type)`
  - Updates the content of a resource file.
  - Automatically updates its size and last accessed time.
  - Supports JSON, YAML, and text formats.

#### **5. Resource Deletion**
- **Method**: `delete_resource(name)`
  - Deletes the resource file and removes it from the resource manager.

#### **6. Resource Retrieval**
- **Methods**:
  - `get_resource(name)`: Retrieve details of a specific resource.
  - `get_resources_by_type(type)`: Get all resources of a specific type.
  - `get_loaded_resources()`: Get currently loaded resources.

#### **7. Resource Optimization**
- **Method**: `optimize_memory()`
  - Unloads resources that haven’t been accessed for a specified time (default: 1 hour).
  - Frees up memory while maintaining frequently used resources in memory.

#### **8. Resource Usage Statistics**
- **Method**: `get_resource_usage()`
  - Provides statistics on total and loaded resources, including their sizes.

---

### **Error Handling**

1. **`ResourceError`**: Base class for resource-related errors.
2. **Specific Errors**:
   - **`ResourceNotFoundError`**: Raised when a requested resource is not found.
   - **`ResourceTypeError`**: Raised when an unsupported resource type is encountered.
   - **`ResourceLimitError`**: Raised when resource limits are exceeded.
