import feedparser
import re

RSS_FEEDS = {
    "G1 Politica": "https://g1.globo.com/rss/g1/politica/",
    "G1 Economia": "https://g1.globo.com/rss/g1/economia/",
    "Folha Poder": "https://feeds.folha.uol.com.br/poder/rss091.xml",
    "Folha Mercado": "https://feeds.folha.uol.com.br/mercado/rss091.xml",
    "UOL Noticias": "https://rss.uol.com.br/feed/noticias.xml",
}

class NewsFetcher:
    def __init__(self):
        self.feeds = RSS_FEEDS

    def fetch_all_headlines(self, max_per_feed=5):
        all_news = []
        for source, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:max_per_feed]:
                    all_news.append({
                        "source": source,
                        "title": entry.get("title", "").strip(),
                        "summary": entry.get("summary", "")[:300].strip(),
                        "link": entry.get("link", "")
                    })
            except Exception as e:
                print(f"Erro ao buscar feed '{source}': {e}")
        return all_news

    def fetch_related_news(self, topic, max_results=5):
        keywords = self._extract_keywords(topic)
        all_news = self.fetch_all_headlines(max_per_feed=10)
        scored = []
        for news in all_news:
            score = self._relevance_score(news["title"] + " " + news["summary"], keywords)
            if score > 0:
                scored.append((score, news))
        scored.sort(key=lambda x: x[0], reverse=True)
        related = [news for _, news in scored[:max_results]]
        if not related:
            related = all_news[:max_results]
        return related

    def format_news_context(self, news_list):
        if not news_list:
            return ""
        lines = ["=== MANCHETES DO DIA (CONTEXTO REAL) ==="]
        for i, news in enumerate(news_list, 1):
            lines.append(f"{i}. [{news['source']}] {news['title']}")
            if news.get("summary"):
                lines.append(f"   {news['summary'][:150]}...")
        lines.append("==========================================")
        return "
".join(lines)

    def _extract_keywords(self, text):
        stopwords = {
            "de","da","do","das","dos","e","o","a","os","as","em","no","na",
            "com","por","para","que","se","um","uma","ao","foi","sao",
            "ser","tem","ter","como","mais","sobre","esse","essa","este","esta"
        }
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text, re.IGNORECASE)
        return [w.lower() for w in words if w.lower() not in stopwords]

    def _relevance_score(self, text, keywords):
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)
