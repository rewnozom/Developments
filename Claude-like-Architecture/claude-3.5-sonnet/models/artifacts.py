# models/artifacts.py
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pathlib import Path
import hashlib
import json
import re
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

# Constants
DEFAULT_ARTIFACT_VERSION = "1.0.0"
DEFAULT_ARTIFACT_CREATOR = "Claude"

# Supported languages configuration
SUPPORTED_LANGUAGES = {
    'CODE': ['python', 'javascript', 'typescript', 'html', 'css'],
    'REACT': ['javascript', 'typescript'],
}

class ArtifactType(Enum):
    """Enumeration of artifact types."""
    CODE = "application/vnd.ant.code"
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    SVG = "image/svg+xml"
    MERMAID = "application/vnd.ant.mermaid"
    REACT = "application/vnd.ant.react"

@dataclass
class ArtifactMetadata:
    """Metadata for artifacts."""
    created_at: datetime
    modified_at: datetime
    version: str
    creator: str
    size: int
    checksum: str
    language: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "version": self.version,
            "creator": self.creator,
            "size": self.size,
            "checksum": self.checksum,
            "language": self.language,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactMetadata':
        """Create metadata from dictionary."""
        return cls(
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            version=data["version"],
            creator=data["creator"],
            size=data["size"],
            checksum=data["checksum"],
            language=data.get("language"),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            custom_data=data.get("custom_data", {})
        )

@dataclass
class ValidationResult:
    """Result of artifact validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

@dataclass
class Artifact:
    """Represents a generated artifact."""
    type: ArtifactType
    content: str
    identifier: str
    title: str
    metadata: ArtifactMetadata
    id: UUID = field(default_factory=uuid4)
    parent_id: Optional[UUID] = None
    validation: Optional[ValidationResult] = None

    def validate(self) -> ValidationResult:
        """Validate artifact content and structure."""
        errors = []
        warnings = []

        # Basic validation
        if not self.content.strip():
            errors.append("Content cannot be empty")
        if not self.identifier.strip():
            errors.append("Identifier cannot be empty")
        if not self.title.strip():
            errors.append("Title cannot be empty")

        # Type-specific validation
        if self.type == ArtifactType.CODE:
            if not self.metadata.language:
                errors.append("Language must be specified for code artifacts")
            elif self.metadata.language not in SUPPORTED_LANGUAGES.get('CODE', []):
                errors.append(f"Unsupported language for code artifact: {self.metadata.language}")

        elif self.type == ArtifactType.REACT:
            if "export default" not in self.content:
                errors.append("React component must have a default export")
            if self._has_arbitrary_tailwind_values(self.content):
                errors.append("Arbitrary Tailwind values are not allowed")
            if self.metadata.language and self.metadata.language not in SUPPORTED_LANGUAGES.get('REACT', []):
                errors.append(f"Unsupported language for React component: {self.metadata.language}")

        elif self.type == ArtifactType.SVG:
            if not self.content.strip().startswith("<svg"):
                errors.append("Invalid SVG content")
            if "width=" in self.content or "height=" in self.content:
                warnings.append("SVG should use viewBox instead of width/height")
            if not self._validate_svg_content():
                errors.append("Malformed SVG content")

        elif self.type == ArtifactType.HTML:
            if not self._validate_html_content():
                errors.append("Invalid HTML content")
            if self._has_external_resources():
                warnings.append("External resources should be limited to cdnjs.cloudflare.com")

        # Update validation result
        self.validation = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        return self.validation

    def _has_arbitrary_tailwind_values(self, content: str) -> bool:
        """Check for arbitrary Tailwind values."""
        arbitrary_pattern = r'\[[\w\d\s-]+\]'
        return bool(re.search(arbitrary_pattern, content))

    def _validate_html_content(self) -> bool:
        """Validate HTML content."""
        class HTMLValidator(HTMLParser):
            def __init__(self):
                super().__init__()
                self.valid = True
                self.errors = []
                self.tags_stack = []

            def handle_starttag(self, tag, attrs):
                self.tags_stack.append(tag)

            def handle_endtag(self, tag):
                if not self.tags_stack or self.tags_stack[-1] != tag:
                    self.valid = False
                    self.errors.append(f"Mismatched HTML tags near </{tag}>")
                else:
                    self.tags_stack.pop()

            def error(self, message):
                self.valid = False
                self.errors.append(message)

        validator = HTMLValidator()
        try:
            validator.feed(self.content)
            return validator.valid and not validator.tags_stack
        except Exception as e:
            return False

    def _validate_svg_content(self) -> bool:
        """Validate SVG content."""
        try:
            ET.fromstring(self.content)
            return True
        except ET.ParseError:
            return False
        except Exception:
            return False

    def _has_external_resources(self) -> bool:
        """Check for external resource references."""
        allowed_domain = "cdnjs.cloudflare.com"
        external_patterns = [
            r'src=["\'](?!data:)(?!\/api\/placeholder)(?!https:\/\/cdnjs\.cloudflare\.com)[^"\']*["\']',
            r'href=["\'](?!data:)(?!#)(?!https:\/\/cdnjs\.cloudflare\.com)[^"\']*["\']'
        ]
        
        for pattern in external_patterns:
            if re.search(pattern, self.content):
                return True
        return False

    def update_content(self, new_content: str) -> None:
        """Update artifact content and metadata."""
        self.content = new_content
        self.metadata.modified_at = datetime.now()
        self.metadata.size = len(new_content.encode('utf-8'))
        self.metadata.checksum = hashlib.sha256(
            new_content.encode('utf-8')
        ).hexdigest()
        self.validate()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the artifact."""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.metadata.modified_at = datetime.now()

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the artifact."""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.modified_at = datetime.now()
            return True
        return False

    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the artifact."""
        if dependency not in self.metadata.dependencies:
            self.metadata.dependencies.append(dependency)
            self.metadata.modified_at = datetime.now()

    def remove_dependency(self, dependency: str) -> bool:
        """Remove a dependency from the artifact."""
        if dependency in self.metadata.dependencies:
            self.metadata.dependencies.remove(dependency)
            self.metadata.modified_at = datetime.now()
            return True
        return False

    def update_metadata(self, key: str, value: Any) -> None:
        """Update custom metadata."""
        self.metadata.custom_data[key] = value
        self.metadata.modified_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary."""
        return {
            "id": str(self.id),
            "type": self.type.value,
            "content": self.content,
            "identifier": self.identifier,
            "title": self.title,
            "metadata": self.metadata.to_dict(),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "validation": self.validation.to_dict() if self.validation else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """Create artifact from dictionary."""
        return cls(
            id=UUID(data["id"]),
            type=ArtifactType(data["type"]),
            content=data["content"],
            identifier=data["identifier"],
            title=data["title"],
            metadata=ArtifactMetadata.from_dict(data["metadata"]),
            parent_id=UUID(data["parent_id"]) if data.get("parent_id") else None,
            validation=ValidationResult(**data["validation"]) if data.get("validation") else None
        )

    def to_xml(self) -> str:
        """Convert artifact to XML representation."""
        content_escaped = self.content.replace('<', '&lt;').replace('>', '&gt;')
        return (
            f'<ANTARTIFACTLINK identifier="{self.identifier}" '
            f'type="{self.type.value}" '
            f'title="{self.title}" '
            f'language="{self.metadata.language or ""}" '
            f'version="{self.metadata.version}">{content_escaped}</ANTARTIFACTLINK>'
        )

    @classmethod
    def from_xml(cls, xml_string: str) -> 'Artifact':
        """Create artifact from XML representation."""
        try:
            identifier = re.search(r'identifier="([^"]*)"', xml_string).group(1)
            type_str = re.search(r'type="([^"]*)"', xml_string).group(1)
            title = re.search(r'title="([^"]*)"', xml_string).group(1)
            language_match = re.search(r'language="([^"]*)"', xml_string)
            version_match = re.search(r'version="([^"]*)"', xml_string)
            content_match = re.search(r'>([^<]*)</ANTARTIFACTLINK>', xml_string)
            
            content = content_match.group(1).replace('&lt;', '<').replace('&gt;', '>') if content_match else ""
            language = language_match.group(1) if language_match else None
            version = version_match.group(1) if version_match else DEFAULT_ARTIFACT_VERSION

            # Create metadata
            metadata = ArtifactMetadata(
                created_at=datetime.now(),
                modified_at=datetime.now(),
                version=version,
                creator=DEFAULT_ARTIFACT_CREATOR,
                size=len(content.encode('utf-8')),
                checksum=hashlib.sha256(content.encode('utf-8')).hexdigest(),
                language=language
            )

            return cls(
                type=ArtifactType(type_str),
                content=content,
                identifier=identifier,
                title=title,
                metadata=metadata
            )
        except Exception as e:
            raise ArtifactError(f"Failed to parse XML: {str(e)}")

    def export_file(self, directory: Path) -> Path:
        """Export artifact to file."""
        directory.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension based on type and language
        extensions = {
            ArtifactType.CODE: {
                'python': '.py',
                'javascript': '.js',
                'typescript': '.ts',
                'html': '.html',
                'css': '.css',
                'default': '.txt'
            },
            ArtifactType.MARKDOWN: '.md',
            ArtifactType.HTML: '.html',
            ArtifactType.SVG: '.svg',
            ArtifactType.MERMAID: '.mmd',
            ArtifactType.REACT: '.jsx' if self.metadata.language == 'javascript' else '.tsx'
        }
        
        if self.type == ArtifactType.CODE:
            extension = extensions[self.type].get(self.metadata.language, extensions[self.type]['default'])
        else:
            extension = extensions.get(self.type, '.txt')
            
        # Create safe filename
        safe_identifier = re.sub(r'[^a-zA-Z0-9\-_]', '_', self.identifier)
        file_path = directory / f"{safe_identifier}{extension}"
        
        # Write content with appropriate encoding
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
                
            # Update metadata
            self.metadata.modified_at = datetime.now()
            self.metadata.custom_data['last_exported'] = datetime.now().isoformat()
            self.metadata.custom_data['export_path'] = str(file_path)
            
            return file_path
            
        except Exception as e:
            raise ArtifactError(f"Failed to export artifact: {str(e)}")

    def get_export_info(self) -> Dict[str, Any]:
        """Get information about the last export."""
        return {
            'last_exported': self.metadata.custom_data.get('last_exported'),
            'export_path': self.metadata.custom_data.get('export_path'),
            'file_size': self.metadata.size,
            'checksum': self.metadata.checksum
        }

    def create_backup(self, backup_dir: Path) -> Path:
        """Create a backup of the artifact."""
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{self.identifier}_{timestamp}.backup"
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            return backup_path
        except Exception as e:
            raise ArtifactError(f"Failed to create backup: {str(e)}")

    @classmethod
    def load_backup(cls, backup_path: Path) -> 'Artifact':
        """Load artifact from backup file."""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ArtifactError(f"Failed to load backup: {str(e)}")

    def get_dependencies_info(self) -> Dict[str, List[str]]:
        """Get detailed information about dependencies."""
        return {
            'direct': self.metadata.dependencies,
            'suggested': self._get_suggested_dependencies(),
            'conflicts': self._check_dependency_conflicts()
        }

    def _get_suggested_dependencies(self) -> List[str]:
        """Analyze content and suggest potential dependencies."""
        suggested = []
        
        if self.type == ArtifactType.REACT:
            # Check for common React library usage patterns
            if 'useState' in self.content or 'useEffect' in self.content:
                suggested.append('react')
            if 'className=' in self.content:
                suggested.append('tailwindcss')
                
        elif self.type == ArtifactType.CODE:
            # Analyze imports or requires
            import_pattern = r'(?:import|require)\s+[\'"]([^\'"]+)[\'"]'
            matches = re.findall(import_pattern, self.content)
            suggested.extend(matches)
            
        return list(set(suggested))

    def _check_dependency_conflicts(self) -> List[str]:
        """Check for potential dependency conflicts."""
        conflicts = []
        
        if self.type == ArtifactType.REACT:
            # Example conflict checks
            if 'tailwindcss' in self.metadata.dependencies and 'styled-components' in self.metadata.dependencies:
                conflicts.append('tailwindcss and styled-components may conflict')
                
        return conflicts

    def get_stats(self) -> Dict[str, Any]:
        """Get statistical information about the artifact."""
        return {
            'size': self.metadata.size,
            'line_count': len(self.content.splitlines()),
            'created': self.metadata.created_at.isoformat(),
            'modified': self.metadata.modified_at.isoformat(),
            'version': self.metadata.version,
            'validation_status': self.validation.valid if self.validation else None,
            'warning_count': len(self.validation.warnings) if self.validation else 0,
            'error_count': len(self.validation.errors) if self.validation else 0
        }

def create_artifact_metadata(
    content: str,
    language: Optional[str] = None,
    creator: str = DEFAULT_ARTIFACT_CREATOR,
    version: str = DEFAULT_ARTIFACT_VERSION
) -> ArtifactMetadata:
    """Create artifact metadata with standard values."""
    content_bytes = content.encode('utf-8')
    now = datetime.now()
    
    return ArtifactMetadata(
        created_at=now,
        modified_at=now,
        version=version,
        creator=creator,
        size=len(content_bytes),
        checksum=hashlib.sha256(content_bytes).hexdigest(),
        language=language
    )

def validate_artifact_type(artifact_type: ArtifactType, content: str) -> List[str]:
    """Validate content against artifact type."""
    warnings = []
    
    if artifact_type == ArtifactType.CODE and len(content.split('\n')) < 2:
        warnings.append("Code artifacts should typically contain multiple lines")
        
    elif artifact_type == ArtifactType.MARKDOWN and not any(line.startswith('#') for line in content.split('\n')):
        warnings.append("Markdown should typically contain headers")
        
    elif artifact_type == ArtifactType.HTML and not content.strip().lower().startswith('<!doctype html>'):
        warnings.append("HTML should start with DOCTYPE declaration")
        
    return warnings

def generate_safe_identifier(title: str) -> str:
    """Generate a safe identifier from a title."""
    # Remove special characters and convert spaces to hyphens
    safe = re.sub(r'[^\w\s-]', '', title.lower())
    safe = re.sub(r'[-\s]+', '-', safe).strip('-')
    
    # Ensure it starts with a letter
    if safe and not safe[0].isalpha():
        safe = f"artifact-{safe}"
        
    return safe

def merge_artifacts(artifacts: List[Artifact]) -> Artifact:
    """Merge multiple artifacts into one."""
    if not artifacts:
        raise ValueError("No artifacts to merge")
        
    if len(set(a.type for a in artifacts)) > 1:
        raise ArtifactTypeError(
            "Cannot merge artifacts of different types",
            expected_type=next(iter(artifacts)).type,
            received_type=next(iter(a.type for a in artifacts if a.type != next(iter(artifacts)).type))
        )
        
    # Combine content
    combined_content = "\n\n".join(a.content for a in artifacts)
    
    # Create merged metadata
    now = datetime.now()
    merged_metadata = ArtifactMetadata(
        created_at=min(a.metadata.created_at for a in artifacts),
        modified_at=now,
        version=max(a.metadata.version for a in artifacts),
        creator=artifacts[0].metadata.creator,
        size=len(combined_content.encode('utf-8')),
        checksum=hashlib.sha256(combined_content.encode('utf-8')).hexdigest(),
        language=artifacts[0].metadata.language,
        tags=list(set(tag for a in artifacts for tag in a.metadata.tags)),
        dependencies=list(set(dep for a in artifacts for dep in a.metadata.dependencies))
    )
    
    # Create merged artifact
    merged = Artifact(
        type=artifacts[0].type,
        content=combined_content,
        identifier=f"merged-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        title=f"Merged Artifact ({len(artifacts)} sources)",
        metadata=merged_metadata
    )
    
    merged.validate()
    return merged

class ArtifactError(Exception):
    """Base class for artifact-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'error_type': self.__class__.__name__,
            'message': str(self),
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class ArtifactValidationError(ArtifactError):
    """Raised when artifact validation fails."""
    def __init__(self, message: str, validation_result: ValidationResult):
        details = {
            'validation_result': validation_result.to_dict(),
            'severity': 'error' if validation_result.errors else 'warning'
        }
        super().__init__(message, details)
        self.validation_result = validation_result

class ArtifactTypeError(ArtifactError):
    """Raised when there's an artifact type mismatch."""
    def __init__(self, message: str, expected_type: ArtifactType, received_type: ArtifactType):
        details = {
            'expected_type': expected_type.value,
            'received_type': received_type.value
        }
        super().__init__(message, details)

class ArtifactNotFoundError(ArtifactError):
    """Raised when an artifact is not found."""
    def __init__(self, message: str, search_criteria: Optional[Dict[str, Any]] = None):
        details = {'search_criteria': search_criteria} if search_criteria else {}
        super().__init__(message, details)

class ArtifactContentError(ArtifactError):
    """Raised when there's an issue with artifact content."""
    def __init__(self, message: str, content_type: str, content_size: int):
        details = {
            'content_type': content_type,
            'content_size': content_size
        }
        super().__init__(message, details)

class ArtifactCollection:
    """Collection of related artifacts."""

    def __init__(self):
        self.artifacts: Dict[UUID, Artifact] = {}
        self._index: Dict[str, Dict[Any, List[UUID]]] = {
            'identifiers': {},
            'types': {},
            'tags': {},
            'languages': {}
        }
        self.last_modified: datetime = datetime.now()

    def add_artifact(self, artifact: Artifact) -> None:
        """Add artifact to collection."""
        if not artifact.validation:
            artifact.validate()
        if not artifact.validation.valid:
            raise ArtifactValidationError(
                f"Cannot add invalid artifact: {artifact.validation.errors}",
                artifact.validation
            )
            
        # Add to main storage
        self.artifacts[artifact.id] = artifact
        
        # Update indices
        self._update_indices(artifact)
        self.last_modified = datetime.now()

    def _update_indices(self, artifact: Artifact) -> None:
        """Update internal indices for fast lookups."""
        # Index by identifier
        self._index['identifiers'].setdefault(artifact.identifier, []).append(artifact.id)
        
        # Index by type
        self._index['types'].setdefault(artifact.type.value, []).append(artifact.id)
        
        # Index by tags
        for tag in artifact.metadata.tags:
            self._index['tags'].setdefault(tag, []).append(artifact.id)
            
        # Index by language
        if artifact.metadata.language:
            self._index['languages'].setdefault(
                artifact.metadata.language, []
            ).append(artifact.id)

    def _remove_from_indices(self, artifact: Artifact) -> None:
        """Remove artifact from all indices."""
        # Remove from identifier index
        if artifact.identifier in self._index['identifiers']:
            self._index['identifiers'][artifact.identifier].remove(artifact.id)
            if not self._index['identifiers'][artifact.identifier]:
                del self._index['identifiers'][artifact.identifier]
                
        # Remove from type index
        if artifact.type.value in self._index['types']:
            self._index['types'][artifact.type.value].remove(artifact.id)
            if not self._index['types'][artifact.type.value]:
                del self._index['types'][artifact.type.value]
                
        # Remove from tags index
        for tag in artifact.metadata.tags:
            if tag in self._index['tags']:
                self._index['tags'][tag].remove(artifact.id)
                if not self._index['tags'][tag]:
                    del self._index['tags'][tag]
                    
        # Remove from language index
        if (artifact.metadata.language and 
            artifact.metadata.language in self._index['languages']):
            self._index['languages'][artifact.metadata.language].remove(artifact.id)
            if not self._index['languages'][artifact.metadata.language]:
                del self._index['languages'][artifact.metadata.language]

    def get_artifact(self, artifact_id: UUID) -> Optional[Artifact]:
        """Get artifact by ID."""
        return self.artifacts.get(artifact_id)

    def get_artifacts_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """Get all artifacts of specific type."""
        artifact_ids = self._index['types'].get(artifact_type.value, [])
        return [self.artifacts[aid] for aid in artifact_ids if aid in self.artifacts]

    def get_artifacts_by_tag(self, tag: str) -> List[Artifact]:
        """Get all artifacts with specific tag."""
        artifact_ids = self._index['tags'].get(tag, [])
        return [self.artifacts[aid] for aid in artifact_ids if aid in self.artifacts]

    def get_artifacts_by_identifier(self, identifier: str) -> List[Artifact]:
        """Get all artifacts with specific identifier."""
        artifact_ids = self._index['identifiers'].get(identifier, [])
        return [self.artifacts[aid] for aid in artifact_ids if aid in self.artifacts]

    def get_artifacts_by_language(self, language: str) -> List[Artifact]:
        """Get all artifacts in a specific language."""
        artifact_ids = self._index['languages'].get(language, [])
        return [self.artifacts[aid] for aid in artifact_ids if aid in self.artifacts]

    def remove_artifact(self, artifact_id: UUID) -> bool:
        """Remove artifact from collection."""
        if artifact_id not in self.artifacts:
            raise ArtifactNotFoundError(f"Artifact {artifact_id} not found", {'artifact_id': str(artifact_id)})
            
        artifact = self.artifacts[artifact_id]
        self._remove_from_indices(artifact)
        del self.artifacts[artifact_id]
        self.last_modified = datetime.now()
        return True

    def clear(self) -> None:
        """Remove all artifacts from collection."""
        self.artifacts.clear()
        self._index = {
            'identifiers': {},
            'types': {},
            'tags': {},
            'languages': {}
        }
        self.last_modified = datetime.now()

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            'total_artifacts': len(self.artifacts),
            'artifacts_by_type': {
                t: len(ids) 
                for t, ids in self._index['types'].items()
            },
            'total_tags': len(self._index['tags']),
            'languages_used': list(self._index['languages'].keys()),
            'last_modified': self.last_modified.isoformat()
        }

    def export_directory(self, directory: Path) -> Dict[str, Any]:
        """Export all artifacts to directory structure."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        export_results = {
            'successful': [],
            'failed': []
        }
        
        # Create subdirectories by type
        for artifact_type in ArtifactType:
            type_dir = directory / artifact_type.value.split('/')[-1]
            type_dir.mkdir(exist_ok=True)
            
            artifacts = self.get_artifacts_by_type(artifact_type)
            for artifact in artifacts:
                try:
                    exported_path = artifact.export_file(type_dir)
                    export_results['successful'].append({
                        'id': str(artifact.id),
                        'path': str(exported_path)
                    })
                except Exception as e:
                    export_results['failed'].append({
                        'id': str(artifact.id),
                        'error': str(e)
                    })
        
        return export_results

    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary."""
        return {
            'artifacts': {
                str(art_id): artifact.to_dict()
                for art_id, artifact in self.artifacts.items()
            },
            'stats': self.get_stats()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactCollection':
        """Create collection from dictionary."""
        collection = cls()
        for art_id, art_data in data.get('artifacts', {}).items():
            artifact = Artifact.from_dict(art_data)
            collection.add_artifact(artifact)
        return collection

class ArtifactError(Exception):
    """Base class for artifact-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'error_type': self.__class__.__name__,
            'message': str(self),
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class ArtifactValidationError(ArtifactError):
    """Raised when artifact validation fails."""
    def __init__(self, message: str, validation_result: ValidationResult):
        details = {
            'validation_result': validation_result.to_dict(),
            'severity': 'error' if validation_result.errors else 'warning'
        }
        super().__init__(message, details)
        self.validation_result = validation_result

class ArtifactTypeError(ArtifactError):
    """Raised when there's an artifact type mismatch."""
    def __init__(self, message: str, expected_type: ArtifactType, received_type: ArtifactType):
        details = {
            'expected_type': expected_type.value,
            'received_type': received_type.value
        }
        super().__init__(message, details)

class ArtifactNotFoundError(ArtifactError):
    """Raised when an artifact is not found."""
    def __init__(self, message: str, search_criteria: Optional[Dict[str, Any]] = None):
        details = {'search_criteria': search_criteria} if search_criteria else {}
        super().__init__(message, details)

class ArtifactContentError(ArtifactError):
    """Raised when there's an issue with artifact content."""
    def __init__(self, message: str, content_type: str, content_size: int):
        details = {
            'content_type': content_type,
            'content_size': content_size
        }
        super().__init__(message, details)

# Utility functions
def create_artifact_metadata(
    content: str,
    language: Optional[str] = None,
    creator: str = DEFAULT_ARTIFACT_CREATOR,
    version: str = DEFAULT_ARTIFACT_VERSION
) -> ArtifactMetadata:
    """Create artifact metadata with standard values."""
    content_bytes = content.encode('utf-8')
    now = datetime.now()
    
    return ArtifactMetadata(
        created_at=now,
        modified_at=now,
        version=version,
        creator=creator,
        size=len(content_bytes),
        checksum=hashlib.sha256(content_bytes).hexdigest(),
        language=language
    )

def validate_artifact_type(artifact_type: ArtifactType, content: str) -> List[str]:
    """Validate content against artifact type."""
    warnings = []
    
    if artifact_type == ArtifactType.CODE and len(content.split('\n')) < 2:
        warnings.append("Code artifacts should typically contain multiple lines")
        
    elif artifact_type == ArtifactType.MARKDOWN and not any(line.startswith('#') for line in content.split('\n')):
        warnings.append("Markdown should typically contain headers")
        
    elif artifact_type == ArtifactType.HTML and not content.strip().lower().startswith('<!doctype html>'):
        warnings.append("HTML should start with DOCTYPE declaration")
        
    return warnings

def generate_safe_identifier(title: str) -> str:
    """Generate a safe identifier from a title."""
    # Remove special characters and convert spaces to hyphens
    safe = re.sub(r'[^\w\s-]', '', title.lower())
    safe = re.sub(r'[-\s]+', '-', safe).strip('-')
    
    # Ensure it starts with a letter
    if safe and not safe[0].isalpha():
        safe = f"artifact-{safe}"
        
    return safe

def merge_artifacts(artifacts: List[Artifact]) -> Artifact:
    """Merge multiple artifacts into one."""
    if not artifacts:
        raise ValueError("No artifacts to merge")
        
    if len(set(a.type for a in artifacts)) > 1:
        first_type = next(iter(artifacts)).type
        for a in artifacts:
            if a.type != first_type:
                raise ArtifactTypeError(
                    "Cannot merge artifacts of different types",
                    expected_type=first_type,
                    received_type=a.type
                )
                
    # Combine content
    combined_content = "\n\n".join(a.content for a in artifacts)
    
    # Create merged metadata
    now = datetime.now()
    merged_metadata = ArtifactMetadata(
        created_at=min(a.metadata.created_at for a in artifacts),
        modified_at=now,
        version=max(a.metadata.version for a in artifacts),
        creator=artifacts[0].metadata.creator,
        size=len(combined_content.encode('utf-8')),
        checksum=hashlib.sha256(combined_content.encode('utf-8')).hexdigest(),
        language=artifacts[0].metadata.language,
        tags=list(set(tag for a in artifacts for tag in a.metadata.tags)),
        dependencies=list(set(dep for a in artifacts for dep in a.metadata.dependencies))
    )
    
    # Create merged artifact
    merged = Artifact(
        type=artifacts[0].type,
        content=combined_content,
        identifier=f"merged-{now.strftime('%Y%m%d-%H%M%S')}",
        title=f"Merged Artifact ({len(artifacts)} sources)",
        metadata=merged_metadata
    )
    
    merged.validate()
    return merged

def initialize_module() -> None:
    """Initialize the artifacts module."""
    # Ensure all ArtifactType values are unique
    type_values = [t.value for t in ArtifactType]
    if len(type_values) != len(set(type_values)):
        raise ValueError("Duplicate ArtifactType values found")

    # Validate supported languages configuration
    for artifact_type, languages in SUPPORTED_LANGUAGES.items():
        if not isinstance(languages, list):
            raise TypeError(f"Languages for {artifact_type} must be a list")

# Module initialization
initialize_module()
