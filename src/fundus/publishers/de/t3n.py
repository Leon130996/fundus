import datetime
from typing import List, Optional

from lxml.cssselect import CSSSelector

from fundus.parser import ArticleBody, BaseParser, ParserProxy, attribute
from fundus.parser.utility import generic_author_parsing, generic_date_parsing


class T3nParser(ParserProxy):
    class V1(BaseParser):
        _paragraph_selector = CSSSelector("div[class='article-content'] > p")

        @attribute
        def body(self) -> Optional[str]:
            return self.precomputed.meta.get("og:description")

        @attribute
        def publishing_date(self) -> Optional[datetime.datetime]:
            return generic_date_parsing(self.precomputed.ld.bf_search("datePublished"))

        @attribute
        def authors(self) -> List[str]:
            return generic_author_parsing(self.precomputed.ld.bf_search("author"))

        @attribute
        def title(self) -> Optional[str]:
            return self.precomputed.meta.get("og:title")
