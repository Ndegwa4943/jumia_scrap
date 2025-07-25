import scrapy

class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.co.ke"]
    start_urls = ["https://www.jumia.co.ke/smartphones/"]

    page_count = 1
    max_pages = 3  # Change this as needed

    def parse(self, response):
        self.logger.info(f"Scraping page {self.page_count}")

        products = response.css('article.prd')
        for product in products:
            yield {
                'title': product.css('h3.name::text').get(default='No title available'),
                'price': product.css('div.prc::text').get(default='No price listed'),
                'link': response.urljoin(product.css('a::attr(href)').get(default='#'))
            }

        if self.page_count < self.max_pages:
            # Select the correct "Next" button
            next_page = response.css('a.pg[aria-label="Next"]::attr(href)').get()

            if next_page:
                self.page_count += 1
                yield response.follow(next_page, callback=self.parse)

