from langchain_community.tools import DuckDuckGoSearchRun

def get_web_search_tool():
    """Returns a tool to search the live web."""
    return DuckDuckGoSearchRun()

# Example usage: 
# search = get_web_search_tool()
# print(search.run("Future of EV startups in India 2026"))