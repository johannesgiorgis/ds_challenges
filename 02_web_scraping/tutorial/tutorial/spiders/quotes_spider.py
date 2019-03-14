import scrapy

class QuotesSpider(scrapy.Spider):
	name = 'quotes'

	def start_requests(self):
		urls = [
			'http://quotes.toscrape.com/page/1/',
			'http://quotes.toscrape.com/page/2/'
		]

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)


	def parse(self, response):
		'''extract quote information and 
		follow link to next page'''
		for quote in response.css('div.quote'):
			yield {
				'text': quote.css('span.text::text').get(),
				'author': quote.css('small.author::text').get(),
				'tags': quote.css('div.tags a.tag::text').getall(),
			}

		next_page = response.css('li.next a::attr(href)').get()
		if next_page is not None:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)


	def parse_two(self, response):
		'''extract quote information'''
		for quote in response.css('div.quote'):
			yield {
				'text': quote.css('span.text::text').get(),
				'author': quote.css('small.author::text').get(),
				'tags': quote.css('div.tags a.tag::text').getall(),
			}



	def parse_one(self, response):
		'''save page content to local file'''
		page = response.url.split('/')[-2]
		filename = 'quotes-{0}.html'.format(page)

		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log('Saved file {0}'.format(filename))