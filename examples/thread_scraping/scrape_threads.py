import scrapy
import math
import logging
import json
from scrapy.crawler import CrawlerProcess
from lxml import html
from donbot.operations import count_posts, get_posts
from tqdm import tqdm
import os


posts_per_page = 25
archive_path = "../../data/archive.txt"
output_path = "../../data/posts.jsonl"

class PostItem(scrapy.Item):
    number = scrapy.Field()
    id = scrapy.Field()
    user = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    pagelink = scrapy.Field()
    forum = scrapy.Field()
    thread = scrapy.Field()


# The following pipeline stores all scraped items (from all spiders)
# into a single jsonl file, containing one item per line serialized
# in JSON format:
class JsonWriterPipeline(object):
    # operations performed when spider starts
    def open_spider(self, spider):
        self.file = open(output_path, "a")

    # when the spider finishes
    def close_spider(self, spider):
        self.file.close()

    # when the spider yields an item
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class MafiaScumSpider(scrapy.Spider):
    name = "mafiascum"

    # settings
    custom_settings = {
        "LOG_LEVEL": logging.WARNING,
        "ITEM_PIPELINES": {"__main__.JsonWriterPipeline": 1},
    }

    def start_requests(self):
        "Generates scrapy.Request objects for each URL in the archive file."

        with open(archive_path) as f:
            urls = [each[: each.find("\n")] for each in f.read().split("\n\n\n")]
        for url in tqdm(urls):
            yield scrapy.Request(url=url, callback=self.request_each_page)

    def request_each_page(self, response):
        "Generates scrapy.Request objects for each page of a thread."
        try:
            thread = response.url
            post_count = count_posts(html.fromstring(response.body))
            end_page_id = math.floor(post_count / posts_per_page) * posts_per_page

            for page_id in range(0, end_page_id, posts_per_page):
                yield scrapy.Request(
                    f"{thread}&start={str(page_id)}",
                    callback=self.process_posts,
                )
        except IndexError:
            return  # occurs when the requested thread doesn't exist or is empty (?)

    def process_posts(self, response):
        "Extracts post data from a page of a thread."
        thread_page_html = html.fromstring(response.body)
        posts = get_posts(thread_page_html)
        page_link = response.url
        thread = page_link[page_link.find("&t=") + 3 : page_link.find("&start")]
        forum = page_link[page_link.find("f=") + 2 : page_link.find("&t=")]
        for post in posts:
            yield PostItem(
                {"pagelink": page_link, "forum": forum, "thread": thread, **post}
            )


if __name__ == "__main__":
    # Start scraping...
    process = CrawlerProcess()
    process.crawl(MafiaScumSpider)
    process.start()

    # Separate Results into Unique Files
    posts = open("posts.jsonl")
    for post in posts:
        with open(f"posts/{json.loads(post)['thread']}.jsonl", "a") as f:
            f.write(post)

    # Clean Up Results
    # Remove duplicate entries and sort by post number for every scraped game.
    # loop through every file in directory
    for path, subdirs, files in os.walk("posts"):
        for name in files:
            # don't consider non-jsonl files
            if name[-5:] != "jsonl":
                continue

            # load as dictionary, remove redundancies, and sort by post number
            with open(f"posts/{name}") as posts_file:
                gameposts = [
                    dict(t)
                    for t in {
                        tuple(d.items())
                        for d in [json.loads(line) for line in posts_file]
                    }
                ]
                gameposts = sorted(
                    gameposts, key=lambda x: (int(x["thread"]), int(x["number"]))
                )

            # save result
            with open(f"posts/{name}", "w") as f:
                f.write("\n".join([json.dumps(post) for post in gameposts]))
