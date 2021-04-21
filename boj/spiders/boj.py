import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from boj.items import Article


class bojSpider(scrapy.Spider):
    name = 'boj'
    start_urls = ['https://www.boj.or.jp/en/index.htm/']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-tabbox"]/ul/li')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('./span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        bad_file_extensions = ['pdf', 'xlsx']
        extension = response.url.lower().split('.')[-1]
        if extension in bad_file_extensions:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//section[@class="left-contents"]/h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="main"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
