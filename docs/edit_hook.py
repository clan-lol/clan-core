"""MkDocs hooks for customizing documentation behavior."""

from typing import Any


def on_page_markdown(markdown: str, page: Any, config: Any, files: Any) -> str:  # noqa: ARG001
    """Hook to set custom edit URL from page frontmatter.

    This allows individual pages to override the default edit URL
    by setting 'edit_url' in their frontmatter.
    """
    # Check if page has custom edit_url in metadata
    if page.meta and "edit_url" in page.meta:
        # Override the edit_url for this page
        page.edit_url = page.meta["edit_url"]

    return markdown
