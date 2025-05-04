"""
Example script demonstrating how to use the WSLSearchClient to search for bills.
"""

import logging
import sys

from wa_leg_mcp.clients import WSLSearchClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def main():
    """Run the example script."""
    # Create the client
    client = WSLSearchClient()

    # Search for bills containing "artificial intelligence"
    print("Searching for bills related to 'artificial intelligence'...")
    results = client.search_bills(
        query="artificial intelligence", bienniums=["2025-26"], max_docs=10, sort_by="Rank"
    )

    # Display results
    if results:
        print(f"Found {len(results)} bills:")
        for bill in results:
            print(f"Bill: {bill['bill_id']} ({bill['biennium']})")
            print(f"Description: {bill['description']}")
            print("-" * 50)
    else:
        print("No results found or an error occurred.")


if __name__ == "__main__":
    main()
