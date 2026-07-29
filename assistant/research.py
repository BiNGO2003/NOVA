"""Public-web research for NOVA. It uses ordinary public web pages, not APIs."""
from html.parser import HTMLParser
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


class _TextExtractor(HTMLParser):
    allowed = {"p", "h1", "h2", "h3", "li"}
    ignored = {"script", "style", "nav", "footer", "header", "svg", "noscript"}

    def __init__(self):
        super().__init__()
        self.parts, self.depth, self.ignore_depth = [], 0, 0

    def handle_starttag(self, tag, attrs):
        if tag in self.ignored:
            self.ignore_depth += 1
        if tag in self.allowed and not self.ignore_depth:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in self.ignored and self.ignore_depth:
            self.ignore_depth -= 1
        if tag in self.allowed and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if self.depth and not self.ignore_depth and len(text) > 25:
            self.parts.append(text)


def _page_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "NOVA research assistant/1.0 (+local Django app)"})
    with urlopen(request, timeout=7) as response:
        html = response.read(450_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    parser = _TextExtractor()
    parser.feed(html)
    seen, chunks = set(), []
    for part in parser.parts:
        if part not in seen:
            chunks.append(part)
            seen.add(part)
        if len(" ".join(chunks)) > 950:
            break
    return " ".join(chunks)


def _source(name: str, url: str) -> dict:
    try:
        text = _page_text(url)
        return {"name": name, "url": url, "excerpt": text[:1000] or "Страница не вернула читаемый фрагмент."}
    except Exception:
        return {"name": name, "url": url, "excerpt": "Источник сейчас недоступен. Откройте его по ссылке позже."}


def is_medical(question: str) -> bool:
    markers = ("здоров", "бол", "симптом", "болезн", "лекар", "врач", "давлен", "температур", "каш", "диабет", "беремен", "анализ")
    return any(marker in question.lower() for marker in markers)


def urgent_warning(question: str) -> str | None:
    markers = ("боль в груди", "не могу дышать", "трудно дышать", "сильное кровотечение", "потеря сознания", "инсульт", "суицид")
    if any(marker in question.lower() for marker in markers):
        return "Это может требовать срочной помощи. Не ждите ответа NOVA: позвоните в местную экстренную службу или обратитесь в ближайшее отделение неотложной помощи."
    return None


def research(question: str) -> dict:
    emergency = urgent_warning(question)
    if emergency:
        return {"answer": emergency, "medical": True, "sources": []}

    encoded = quote_plus(question)
    if is_medical(question):
        sources = [
            _source("MedlinePlus (Национальная медицинская библиотека США)", f"https://medlineplus.gov/search/?query={encoded}"),
            _source("NHS — Conditions A to Z", f"https://www.nhs.uk/search/results?q={encoded}"),
            _source("Wikipedia", f"https://ru.wikipedia.org/w/index.php?title=Special:Search&search={encoded}"),
        ]
        answer = "Я собрала справочные материалы из медицинских источников. Это не диагноз и не замена врачу: сверяйте рекомендации с квалифицированным специалистом, особенно если симптомы усиливаются или появились внезапно."
        return {"answer": answer, "medical": True, "sources": sources}

    sources = [_source("Wikipedia", f"https://ru.wikipedia.org/w/index.php?title=Special:Search&search={encoded}")]
    return {"answer": "Вот что удалось найти по вашему вопросу. Я привела источник и краткий фрагмент; для спорных или важных решений лучше открыть первоисточник.", "medical": False, "sources": sources}
