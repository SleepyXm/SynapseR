import requests
from bs4 import BeautifulSoup
import urllib.parse

def should_search(user_input: str) -> bool:
    triggers = ["search", "look up", "find info", "google", "can you check online", "what does the internet say"]
    text = user_input.lower()
    return any(trigger in text for trigger in triggers)

def duckduckgo_search(query, num_results=3):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://duckduckgo.com/html/?q={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for link in soup.find_all("a", class_="result__a", limit=num_results):
        raw_href = link.get("href")
        # Decode DuckDuckGo redirect
        parsed = urllib.parse.urlparse(raw_href)
        query_params = urllib.parse.parse_qs(parsed.query)
        real_url = query_params.get("uddg", [raw_href])[0]
        title = link.get_text(strip=True)
        results.append({"title": title, "url": real_url})
    return results

def fetch_page_paragraphs(url, max_paragraphs=7):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
        return paragraphs[:max_paragraphs]
    except Exception as e:
        return [f"Error fetching {url}: {e}"]

def get_top_paragraphs(query):
    results = duckduckgo_search(query)
    all_paragraphs = []

    for r in results:
        print(f"\nFetching from: {r['title']} ({r['url']})")
        paras = fetch_page_paragraphs(r['url'])
        all_paragraphs.extend(paras)

    return all_paragraphs

if __name__ == "__main__":
    user_query = input("Enter search query: ")
    paragraphs = get_top_paragraphs(user_query)

    print("\n--- Aggregated Paragraphs ---\n")
    for i, p in enumerate(paragraphs, 1):
        print(f"{i}. {p}\n")