import logging
import requests
from bs4 import BeautifulSoup
from my_cli_agent.models import ToolResult

def view_website(url: str) -> ToolResult:
    """
    Fetches the text content of a given URL.

    This tool is useful for reading articles, documentation, or other
    web pages. It returns the main text content, stripped of HTML tags.

    Args:
        url: The full URL of the website to view.

    Returns:
        A ToolResult object containing the website's text content or an error.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return ToolResult(success=False, error_message="Invalid URL provided. It must start with http:// or https://.")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Use BeautifulSoup to parse the HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = '\n'.join(chunk for chunk in chunks if chunk)

        if not text_content:
            return ToolResult(success=False, error_message=f"Could not extract any text content from the URL: {url}")

        return ToolResult(success=True, result=text_content)

    except requests.exceptions.Timeout:
        return ToolResult(success=False, error_message=f"The request to the URL timed out: {url}")
    except requests.exceptions.RequestException as e:
        return ToolResult(success=False, error_message=f"Failed to fetch the URL. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while viewing website: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")
