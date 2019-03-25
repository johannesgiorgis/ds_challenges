'''
Packt Pub Scrapy Spider
'''

import scrapy
import sys


def get_page(rows=12, data_offset=0):
	'''
	doesn't seem to work within the class
	-> moved outside
	'''
	#print("\tRows:", rows)
	#print("\tData Offset:", data_offset)
	page = 'https://www.packtpub.com/all?'\
		f'search=&availability_list%5BAvailable%5D=Available&offset={data_offset}&rows={rows}&sort='
	return page



class PacktPubSpider(scrapy.Spider):
	name = 'packtpub'

	def start_requests(self):
		data_offset = 0
		rows = 50
		urls = [
			get_page(rows=rows, data_offset=data_offset)
		]

		print("URLs:", urls)

		for url in urls:
			yield scrapy.Request(
				url=url,
				callback=self.parse_next_page
			)


	def get_next_page(rows=12, data_offset=0):
		'''
		deprecated 
		didn't work within the class
		-> moved outside as get_page
		-> wonder why?
		got below error:
		Traceback (most recent call last):
		File "/home/johannes/anaconda3/envs/dsc/lib/python3.7/site-packages/twisted/internet/defer.py", line 654, in _runCallbacks
		current.result = callback(current.result, *args, **kw)
		File "/home/johannes/Documents/projects/ds_challenges/02_web_scraping/scrape_packtpub/scrape_packtpub/spiders/packtpub_spider.py", line 46, in parse_next_page
		next_page = self.get_next_page(rows=num_rows, data_offset=data_offset)
		TypeError: get_next_page() got multiple values for argument 'rows'
		'''
		print("\tRows:", rows)
		print("\tData Offset:", data_offset)
		next_page = f'''
		https://www.packtpub.com/all?search=&availability_list%5BAvailable%5D=Available&offset={data_offset}&rows={rows}&sort=
		'''
		return next_page


	def parse_next_page(self, response):
		'''navigate across all pages'''
		num_rows = 50
		data_offset = response.css('.solr-page-page-selector-page')[-1].attrib['data-offset']

		print(f"Data Offset:{data_offset}|Rows:{num_rows}")
		next_page = get_page(rows=num_rows, data_offset=data_offset)
		print("Next Page:", next_page)

		yield scrapy.Request(
			url=next_page,
			callback=self.parse_next_page
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

		data_offset = int(response.css('.solr-page-page-selector-page')[-1].attrib['data-offset'])


	def parse_product_page(self, response):
		'''parse invididual product page'''

		product_details = response.meta.get('product_details')
		
		product_details['author'] = response.css('.book-top-block-info-authors::text').get().strip()
		product_details['brief_description'] = response.css('.book-top-block-info-one-liner::text').getall()[-1].strip()
		product_details['release_date'] = response.css('time::text').get().strip()
		product_details['isbn'] = response.css('.book-info-isbn13 span::text').getall()[1]
		
		yield product_details



	def parse_save_to_file(self, response):
		'''save page content to local file
		used to get the html code for manual inspection and
		to aid in development'''
		page = response.url.split('/')[-2:]
		page = ''.join(page)
		filename = 'packtpub-{0}.html'.format(page)
		#print(filename)
		#sys.exit(1)

		with open(filename, 'wb') as f:
			f.write(response.body)
		self.log('Saved file {0}'.format(filename))