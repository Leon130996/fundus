import datetime
from typing import List, Optional

from lxml.cssselect import CSSSelector

from fundus.parser import ArticleBody, BaseParser, ParserProxy, attribute
from fundus.parser.utility import extract_article_body_with_selector, generic_author_parsing, generic_date_parsing


class T3nParser(ParserProxy):
    class V1(BaseParser):
        _paragraph_selector = CSSSelector("div[class='article-content'] > p")
        _summary_selector = CSSSelector("div[data-testid=article-header] > p")
        _subheadline_selector = CSSSelector("div[id=articleBody] > h2")

        @attribute
        def body(self) -> ArticleBody:
            summary = self.precomputed.meta.get("og:description")
            if not summary:
                summary = extract_article_body_with_selector(
                    self.precomputed.doc,
                    paragraph_selector=self._paragraph_selector,
                    subheadline_selector=self._subheadline_selector,
                    summary_selector=self._summary_selector,
                )
            else:
                return summary
            return ArticleBody(summary=summary, sections=[])

        @attribute
        def publishing_date(self) -> Optional[datetime.datetime]:
            return generic_date_parsing(self.precomputed.ld.bf_search("datePublished"))

        @attribute
        def authors(self) -> List[str]:
            return generic_author_parsing(self.precomputed.ld.bf_search("author"))

        @attribute
        def title(self) -> Optional[str]:
            return self.precomputed.meta.get("og:title")
