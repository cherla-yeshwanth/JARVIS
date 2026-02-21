"""
JARVIS v1.0 — Search Handler
Web search using DuckDuckGo (free, no API key).
Searches the web, then summarizes results using the LLM.
"""

from brain import Brain

class SearchHandler:
    """Web search and summarization handler."""

    def __init__(self, brain: Brain):
        self.brain = brain
        self.available = False
        try:
            from duckduckgo_search import DDGS
            self.ddgs = DDGS
            self.available = True
            print("[SEARCH] DuckDuckGo search ready.")
        except ImportError:
            print("[SEARCH] duckduckgo-search not installed. Search disabled.")

    def _search_web(self, query: str, max_results: int = 5) -> list[dict]:
        """Search DuckDuckGo and return results."""
        if not self.available:
            return []
        try:
            with self.ddgs() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception as e:
            print(f"[SEARCH] Error: {e}")
            return []

    def _search_news(self, query: str, max_results: int = 5) -> list[dict]:
        """Search DuckDuckGo News."""
        if not self.available:
            return []
        try:
            with self.ddgs() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
                return results
        except Exception as e:
            print(f"[SEARCH] News error: {e}")
            return []

    def handle(self, user_input: str, context: str = '') -> str:
        """Search the web and summarize results."""
        if not self.available:
            return "Web search is not available. Install duckduckgo-search package."

        # Determine if it's a news query
        lower = user_input.lower()
        is_news = any(w in lower for w in ['news', 'latest', 'recent', 'today', 'current'])

        print(f"[SEARCH] Searching: {user_input}")

        if is_news:
            results = self._search_news(user_input)
        else:
            results = self._search_web(user_input)

        if not results:
            return f"No search results found for '{user_input}'. This may be due to query phrasing, search engine limitations, or a temporary block. Try a different query or check for rate limits."

        # Format results for LLM summarization
        formatted = []
        for i, r in enumerate(results[:5], 1):
            title = r.get('title', 'No title')
            body = r.get('body', r.get('description', 'No description'))
            url = r.get('href', r.get('url', ''))
            formatted.append(f"{i}. {title}\n   {body}\n   Source: {url}")

        results_text = "\n\n".join(formatted)

        # Summarize with LLM
        summary_prompt = f"""Based on these search results, provide a clear and concise answer to the user's question.

User's question: "{user_input}"

Search results:
{results_text}

Provide a helpful summary. Cite sources when relevant. If the results don't fully answer the question, say so."""

        return self.brain.generate_response(summary_prompt, context)