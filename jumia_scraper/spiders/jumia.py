import scrapy
from urllib.parse import urljoin

class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.co.ke"]
    start_urls = ["https://www.jumia.co.ke/smartphones/"]

    page_count = 1
    max_pages = 3  # Change as needed
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
    }

    def parse(self, response):
        self.logger.info(f"Scraping page {self.page_count}")

        products = response.css('article.prd')

        for product in products:
            title = product.css('h3.name::text').get()
            if not title:
                continue

            price = product.css('div.prc::text').get(default='No price listed')
            rating_element = product.css('div.stars._m._al')
            
            # Improved rating extraction
            rating = 'No rating'
            if rating_element:
                rating_style = rating_element.css('::attr(style)').get()
                if rating_style and 'width' in rating_style:
                    try:
                        # Extract percentage width (e.g., "width:80%")
                        width_percent = int(rating_style.split('width:')[1].split('%')[0])
                        # Convert percentage to star rating (5-star scale)
                        rating_value = round((width_percent / 100) * 5, 1)
                        rating = f"{rating_value} stars"
                    except (IndexError, ValueError):
                        pass
            
            reviews = product.css('div.rev::text').re_first(r'\d+') or 'No reviews'
            link = response.urljoin(product.css('a.core::attr(href)').get(default='#'))

            # Follow each product link to get brand from details page
            yield response.follow(
                link,
                callback=self.parse_product_details,
                meta={
                    'title': title.strip(),
                    'price': price.strip(),
                    'rating': rating,
                    'reviews': reviews,
                    'link': link
                }
            )

        # Pagination handling
        if self.page_count < self.max_pages:
            next_page = response.css('a.pg[aria-label="Next"]::attr(href)').get()
            if next_page:
                self.page_count += 1
                yield response.follow(next_page, callback=self.parse)

    def parse_product_details(self, response):
        # Get data passed from the listing page
        item = response.meta

        # Extract brand from the breadcrumbs (most reliable)
        brand = response.css('a[aria-label*="brand"]::text').get()
        if not brand:
            # Fallback to first word of title if breadcrumb not found
            brand = item['title'].split()[0] if item['title'] else "Unknown"

        # Return data in the requested order
        yield {
            'Brand': brand.strip(),
            'Name': item['title'],
            'Price': item['price'],
            'Reviews': item['reviews'],
            'Rating': item['rating'],
            'Link': item['link']
        } 