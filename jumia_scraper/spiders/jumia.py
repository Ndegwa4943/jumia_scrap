import scrapy


class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.co.ke"]
    start_urls = ["https://www.jumia.co.ke/smartphones/"]

    # 👇 Add this class-level variable
    page_count = 1
    max_pages = 3  # change this to whatever limit you want

    def parse(self, response):
        self.logger.info(f"Scraping page {self.page_count}")

        products = response.css('article.prd')
        for product in products:
            yield {
                'title': product.css('h3.name::text').get(),
                'price': product.css('div.prc::text').get(),
                'link': product.css('a::attr(href)').get()
            }

        # Only continue if we haven't reached max_pages
        if self.page_count < self.max_pages:
            next_page = response.css('a.pg::attr(href)').get()

            if next_page:
                self.page_count += 1  # Increment the page counter
                yield response.follow(next_page, callback=self.parse)

