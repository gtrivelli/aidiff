"""Output formatter factory."""

from typing import Dict, Type
from aidiff.formatters import OutputFormatter
from aidiff.formatters.markdown_formatter import MarkdownFormatter
from aidiff.formatters.plain_formatter import PlainFormatter


class FormatterFactory:
    """Factory for creating output formatter instances."""

    _formatters: Dict[str, Type[OutputFormatter]] = {
        "markdown": MarkdownFormatter,
        "plain": PlainFormatter,
    }

    @classmethod
    def create_formatter(cls, format_name: str) -> OutputFormatter:
        """
        Create an output formatter instance.
        
        Args:
            format_name: Name of the format ("markdown", "plain")
            
        Returns:
            Configured formatter instance
            
        Raises:
            ValueError: If format is not supported
        """
        if format_name not in cls._formatters:
            available = ", ".join(cls._formatters.keys())
            raise ValueError(f"Format '{format_name}' is not supported. Available: {available}")
        
        formatter_class = cls._formatters[format_name]
        return formatter_class()

    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of supported format names."""
        return list(cls._formatters.keys())
