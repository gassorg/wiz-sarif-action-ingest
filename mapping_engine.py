"""
Field Mapping Engine for SARIF to Wiz Converter

Provides a configurable, extensible mapping system to control which fields
are extracted from SARIF and how they map to the Wiz output schema.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class MappingEngine:
    """Handles field mapping from SARIF to Wiz format based on configuration."""

    def __init__(self, config_path: Path):
        """
        Initialize the mapping engine with a configuration file.
        
        Args:
            config_path: Path to field_mappings.json configuration file
        """
        self.config = self._load_config(config_path)
        self.transformations = self._compile_transformations()

    @staticmethod
    def _load_config(config_path: Path) -> Dict[str, Any]:
        """Load the mapping configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Mapping configuration not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in mapping configuration: {e}")
            raise

    def _compile_transformations(self) -> Dict[str, Callable]:
        """Compile transformation functions from config."""
        return {
            "map_severity": self._transform_map_severity,
            "clean_fixed_version": self._transform_clean_fixed_version,
            "format_remediation": self._transform_format_remediation
        }

    @staticmethod
    def _transform_map_severity(value: str, transform_config: Dict) -> str:
        """Map SARIF severity level to Wiz severity."""
        mapping = transform_config.get("mappings", {})
        return mapping.get(value.lower(), "Medium")

    @staticmethod
    def _transform_clean_fixed_version(value: str, transform_config: Dict) -> str:
        """Clean fixed version, return empty if 'no fix available'."""
        if not value:
            return ""
        if value.lower() == transform_config.get("returns_empty_if", "no fix available").lower():
            return ""
        return value

    @staticmethod
    def _transform_format_remediation(value: str, transform_config: Dict) -> str:
        """Format remediation string from fixed version."""
        if not value:
            return ""
        template = transform_config.get("template", "Update to version: {value}")
        return template.format(value=value)

    def get_field_mappings(self, section: str = "finding_level") -> List[Dict[str, Any]]:
        """
        Get enabled field mappings for a section.
        
        Args:
            section: Mapping section name (finding_level, target_component, etc.)
            
        Returns:
            List of enabled mapping configurations
        """
        section_config = self.config.get("sarif_to_wiz_mappings", {}).get(section, {})
        mappings = section_config.get("mappings", [])
        return [m for m in mappings if m.get("enabled", True)]

    def get_all_enabled_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all enabled mappings from all sections."""
        result = {}
        for section_name, section_config in self.config.get("sarif_to_wiz_mappings", {}).items():
            if section_name in ["description", "version"]:
                continue
            if section_config.get("enabled", True):
                result[section_name] = self.get_field_mappings(section_name)
        return result

    def extract_value(self, obj: Dict[str, Any], path: str) -> Any:
        """
        Extract value from nested object using dot notation and array indices.
        
        Supports:
        - Simple paths: "ruleId"
        - Nested paths: "message.text"
        - Array access: "locations[0].physicalLocation"
        
        Args:
            obj: Object to extract from
            path: Path to extract (dot notation with optional array indices)
            
        Returns:
            Extracted value or None if not found
        """
        parts = self._parse_path(path)
        current = obj

        for part in parts:
            if current is None:
                return None

            if isinstance(part, int):
                # Array index
                if isinstance(current, list) and -len(current) <= part < len(current):
                    current = current[part]
                else:
                    return None
            else:
                # Object key
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None

        return current

    @staticmethod
    def _parse_path(path: str) -> List[Any]:
        """
        Parse a path string into components.
        
        Examples:
            "ruleId" -> ["ruleId"]
            "message.text" -> ["message", "text"]
            "locations[0].physicalLocation" -> ["locations", 0, "physicalLocation"]
        """
        parts = []
        current = ""

        for char in path:
            if char == ".":
                if current:
                    parts.append(current)
                    current = ""
            elif char == "[":
                if current:
                    parts.append(current)
                    current = ""
            elif char == "]":
                if current.isdigit():
                    parts.append(int(current))
                    current = ""
            else:
                current += char

        if current:
            parts.append(current)

        return parts

    def apply_mapping(
        self,
        sarif_result: Dict[str, Any],
        mapping_config: Dict[str, Any],
        severity_map: Optional[Dict[str, str]] = None
    ) -> tuple[str, Any]:
        """
        Apply a single field mapping to extract and transform a value.
        
        Args:
            sarif_result: SARIF result object
            mapping_config: Mapping configuration for this field
            severity_map: Optional severity mapping for transformations
            
        Returns:
            Tuple of (wiz_field_path, extracted_value)
        """
        wiz_field = mapping_config.get("wiz_field")
        source = mapping_config.get("source")

        # Handle constant values
        if source == "constant":
            value = mapping_config.get("value")
            return wiz_field, value

        # Handle SARIF result extraction
        if source == "sarif_result":
            sarif_path = mapping_config.get("sarif_path")
            value = self.extract_value(sarif_result, sarif_path)

            if value is None:
                default = mapping_config.get("default")
                value = default if default is not None else None

            # Apply transformation if specified
            transform_name = mapping_config.get("transform")
            if transform_name and value is not None:
                transform_func = self.transformations.get(transform_name)
                if transform_func:
                    transform_config = self.config.get("transformations", {}).get(transform_name, {})
                    value = transform_func(value, transform_config)

            return wiz_field, value

        return wiz_field, None

    def set_nested_field(self, obj: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a value in a nested object using dot notation.
        
        Args:
            obj: Target object
            path: Path to set (dot notation with optional nesting)
            value: Value to set
            
        Examples:
            set_nested_field(obj, "name", "test") -> obj["name"] = "test"
            set_nested_field(obj, "targetComponent.library.filePath", "file.json")
        """
        parts = path.split(".")
        current = obj

        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value
        current[parts[-1]] = value

    def enable_mapping(self, section: str, field_name: str, enabled: bool = True) -> None:
        """
        Enable or disable a specific mapping field.
        
        Args:
            section: Section name (finding_level, target_component, etc.)
            field_name: Field name to enable/disable
            enabled: True to enable, False to disable
        """
        mappings = self.config.get("sarif_to_wiz_mappings", {}).get(section, {}).get("mappings", [])
        for mapping in mappings:
            if mapping.get("wiz_field") == field_name:
                mapping["enabled"] = enabled
                logger.info(f"Field {field_name} in {section} set to {enabled}")
                break

    def get_mapping_summary(self) -> str:
        """Get a human-readable summary of all enabled mappings."""
        summary = []
        all_mappings = self.get_all_enabled_mappings()

        for section, mappings in all_mappings.items():
            summary.append(f"\n[{section}]")
            for mapping in mappings:
                wiz_field = mapping.get("wiz_field", "unknown")
                sarif_path = mapping.get("sarif_path", "N/A")
                source = mapping.get("source", "unknown")
                desc = mapping.get("description", "")
                summary.append(f"  {wiz_field}")
                summary.append(f"    ← {source}: {sarif_path}")
                if desc:
                    summary.append(f"    # {desc}")

        return "\n".join(summary)
