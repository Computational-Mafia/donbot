# Thread Scraping

Donbot's `get_posts` operation can technically be used to scrape threads, but it's not the most efficient way to do so. This is because `get_posts` is designed to retrieve posts from a thread, and it does so by making a request to the thread's URL and parsing the HTML. This means that if you want to scrape a large number of threads, you'll be making a large number of requests to the same domain, which can be slow and inefficient. 

Here we provide an example of how to scrape threads using donbot and the `scrapy` library. Scrapy can scrape threads much more efficiently than donbot, because it's designed to make multiple requests in parallel, and it's also designed to be able to scrape multiple pages of a website. All this means that it can scrape threads much faster than donbot can. 

This example demonstrates the interoperability of donbot with other libraries and its usefulness for basic research activities. In this case, we use scrapy to manage requests across multiple threads and store asynchronously collected posts data, and donbot to parse the HTML and extract the posts.