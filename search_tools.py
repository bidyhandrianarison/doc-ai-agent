from minsearch import Index
class SearchTool:
    """Tools for searching indexed documents."""

    def __init__(self, index: Index):
        self.index = index

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search the index for relevant documents."""
        results = self.index.search(query)
        return results