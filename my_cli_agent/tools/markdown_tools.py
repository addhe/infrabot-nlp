import logging
from my_cli_agent.models import ToolResult

try:
    from markitdown import MarkItDown
    # Initialize the converter once on startup for efficiency
    md_converter = MarkItDown(enable_plugins=False)
    HAS_MARKITDOWN = True
except ImportError:
    HAS_MARKITDOWN = False
    logging.warning("markitdown library not found. Markdown tools will be disabled.")

def convert_file_to_markdown(file_path: str) -> ToolResult:
    """
    Converts a file at a given path to Markdown format.

    This tool is useful for reading the content of various file types
    (like PDF, DOCX, etc.) in a structured text format.

    Args:
        file_path: The local path to the file to be converted.

    Returns:
        A ToolResult object containing the Markdown content or an error.
    """
    if not HAS_MARKITDOWN:
        return ToolResult(
            success=False,
            error_message="The 'markitdown' library is not installed. This tool is disabled."
        )

    if not file_path or not isinstance(file_path, str):
        return ToolResult(success=False, error_message="File path must be a non-empty string.")

    try:
        # The MarkItDown library handles file existence checks internally
        conversion_result = md_converter.convert(file_path)
        
        if not conversion_result.text_content:
            return ToolResult(
                success=False,
                error_message=f"File '{file_path}' was processed, but resulted in empty content. It might be an unsupported format or an empty file."
            )

        return ToolResult(success=True, result=conversion_result.text_content)

    except FileNotFoundError:
        return ToolResult(success=False, error_message=f"The file was not found at the specified path: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred during Markdown conversion for '{file_path}': {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred during conversion: {e}")
