from langchain_community.tools import DuckDuckGoSearchRun

def search_tool(query: str):
    """
    Executes a web search and returns the top results.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)