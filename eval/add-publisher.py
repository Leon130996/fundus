import argparse
import gzip
import json
import subprocess
from pathlib import Path
from typing import List, NamedTuple

from fundus import BaseCrawler, Crawler, PublisherCollection
from fundus import __development_base_path__ as root_path
from fundus.scraping.article import Article
from fundus.scraping.html import FundusSource
from fundus.scraping.scraper import Scraper


def create_file_name(index: int) -> str:
    return f"{args.publisher}_{index}.html.gz"


def add_html_to_repo(path: Path, html: str) -> None:
    with open(path, "wb") as html_file:
        html_file.write(gzip.compress(bytes(html, "utf-8")))

    subprocess.call(["git", "add", path], stdout=subprocess.PIPE)


def add_article_to_ground_truth(key: str, new_article: Article) -> None:

    entry = {
        "body": list(new_article.body.as_text_sequence()) if new_article.body else [],
        "url": new_article.html.responded_url,
        "crawl_date": str(new_article.html.crawl_date),
    }

    ground_truth[key] = entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="add-publisher",
        description=(
            "script to automatically scrawl <n> (default: 5) articles, save the HTML files under eval/html and add "
            "auto-parsed paragraphs to ground_truth.json. caution, this will overwrite existing files"
        ),
    )

    subparser = parser.add_subparsers(dest="sub_mode")

    # add sub-modes
    parser_add = subparser.add_parser("add", help="add -n articles for specified publisher to the evaluation")
    parser_replace = subparser.add_parser(
        "replace", help="replace article at -id of specified publisher with article taken from -url"
    )

    # add canonical arguments
    parser.add_argument("publisher", metavar="P", type=str, help="publisher to add to evaluation")
    parser.add_argument(
        "-p",
        dest="eval_dir",
        metavar="Path",
        type=str,
        help="path to evaluation dictionary; default is <root-dir>/eval",
    )

    # add arguments for sub-mode <add>
    parser_add.add_argument(
        "-n",
        dest="number_of_articles",
        metavar="Number",
        type=int,
        default=5,
        help="number of articles to add to the evaluation",
    )

    # add arguments for sub-mode <replace>
    parser_replace.add_argument(
        "-id",
        dest="id",
        metavar="Index",
        type=int,
        help="article id within publisher set in ground_truth.json",
    )
    parser_replace.add_argument(
        "-url",
        dest="url",
        metavar="URL",
        type=str,
        help="URL from where to download the replacement article",
    )

    args = parser.parse_args()

    publisher = PublisherCollection[args.publisher]  # type: ignore

    eval_dir = Path(args.eval_dir) if args.eval_dir is not None else root_path / "eval"
    html_dir = eval_dir / "html"
    ground_truth_file_path = eval_dir / "ground_truth.json"
    html_dir.mkdir(parents=True, exist_ok=True)

    if not ground_truth_file_path.exists():
        ground_truth = {}
    else:
        with open(ground_truth_file_path, "r", encoding="utf-8") as ground_truth_file:
            ground_truth = json.load(ground_truth_file)

    class Task(NamedTuple):
        file_name: str
        article: Article

    tasks: List[Task] = []
    crawler: BaseCrawler

    if args.sub_mode == "add":
        crawler = Crawler(publisher)

        for idx, article in enumerate(crawler.crawl(only_complete=False, max_articles=args.number_of_articles)):
            tasks.append(Task(create_file_name(idx), article))

    elif args.sub_mode == "replace":
        source = FundusSource([args.url], publisher=publisher.publisher_name)
        scraper = Scraper(source, parser=publisher.parser)
        crawler = BaseCrawler(scraper)

        if (next_article := next(crawler.crawl(only_complete=False), None)) is None:
            raise ValueError("Could not crawl the specified article")

        file_name = create_file_name(args.id)
        tasks.append(Task(file_name, next_article))

    else:
        raise NotImplemented

    # process tasks
    for task in tasks:
        html_file_path = html_dir / task.file_name
        add_html_to_repo(html_file_path, task.article.html.content)
        add_article_to_ground_truth(task.file_name, task.article)

    ground_truth = dict(sorted(ground_truth.items()))

    with open(ground_truth_file_path, "w", encoding="utf-8") as ground_truth_file:
        test = json.dumps(ground_truth, indent=4, ensure_ascii=False)
        ground_truth_file.write(test)
