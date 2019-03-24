'''
Packt Pub Scrapy Spider
'''

import scrapy
import sys

class PacktPubSpider(scrapy.Spider):
	name = 'packtpub'


	def __init__(self):
		scrapy.Spider.__init__()
		self.rows = 50

	def start_requests(self):
		urls = [
			'https://packtpub.com/all'
		]

		for url in urls:
			yield scrapy.Request(
				url=url,
				callback=self.parse_products
			)

	def parse_products(self, response):
		'''get all products information'''

		for product_info in response.css('div.book-block-outer'):
			product_page_link = response.urljoin(
					product_info.css('div .book-block-overlay a').attrib['href'])

			product_details = {
				'title': product_info.css('.book-block-title::text').get().strip(),
				'full_price': product_info.css('.book-block-price-full::text').get().strip(),
				'discounted_price': product_info.css('.book-block-price-discounted::text').getall()[-1].strip(),
				'product_length': product_info.css('.book-block-overlay-product-length::text').get(),
				'product_page': response.urljoin(
					product_info.css('div .book-block-overlay a').attrib['href']),
				'product_category': product_info.css('div .book-block-overlay a').attrib['href'].split('/')[1].replace('-', ' '),
			}

			yield scrapy.Request(url=product_page_link, 
				callback=self.parse_product_page, 
				meta={'product_details': product_details}
			)


	def parse_product_page(self, response):
		'''parse product page'''

		product_details = response.meta.get('product_details')
		
		product_details['author'] = response.css('.book-top-block-info-authors::text').get().strip()
		product_details['brief_description'] = response.css('.book-top-block-info-one-liner::text').getall()[-1].strip()
		product_details['release_date'] = response.css('time::text').get().strip()
		product_details['isbn'] = response.css('.book-info-isbn13 span::text').getall()[1]
		
		yield product_details



	def parse_save_to_file(self, response):
		'''save page content to local file'''
		page = response.url.split('/')[-2:]
		page = ''.join(page)
		filename = 'packtpub-{0}.html'.format(page)
		#print(filename)
		#sys.exit(1)

		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log('Saved file {0}'.format(filename))