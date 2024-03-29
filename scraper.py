import os
import scrapy
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class IMDbSpider(scrapy.Spider):
    name = "imdb_spider"
    allowed_domains = ["imdb.com", "m.imdb.com"]
    start_urls = ["https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'FEEDS': {
            'results/results.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 4,
                'item_export_kwargs': {
                   'export_empty_fields': True,
                },
            },
        },
    }

    def parse(self, response):
        # Iterate over each movie item on the webpage
        for movie in response.css('li.ipc-metadata-list-summary-item'):
            # Extract the title, IMDb ID, and rating
            title = movie.css('.ipc-title--title .ipc-title-link-wrapper h3::text').get()
            imdb_id_link = movie.css('.ipc-title-link-wrapper::attr(href)').get()
            imdb_id = imdb_id_link.split('/')[2] if imdb_id_link else None
            image_url = movie.css('.ipc-media img.ipc-image::attr(src)').get()
            new_image_url = image_url.replace("UX140_CR0,0,140,207", "UX280_CR0,0,280,414")
            rating_label = movie.css('.ipc-rating-star--imdb::attr(aria-label)').get()
            rating = rating_label.split(': ')[1] if rating_label else None

            # Generate the URL for the wallpaper page
            wallpaper_url = f"https://m.imdb.com/title/{imdb_id}/mediaviewer"

            # Yield a request to the wallpaper page, passing the extracted data for later use
            yield scrapy.Request(wallpaper_url, callback=self.parse_wallpaper, meta={'title': title, 'imdb_id': imdb_id, 'poster_image': new_image_url, 'rating': rating})

    def parse_wallpaper(self, response):
        # Extract the wallpaper image from the response
        wallpaper_image = response.css('div.cISuCS img::attr(src)').get()

        # Return the final data structure including the poster and wallpaper image
        yield {
            'Movie Title': response.meta['title'],
            'IMDb ID': response.meta['imdb_id'],
            'Poster Image': response.meta['poster_image'],
            'Rating': response.meta['rating'],
            'Wallpaper Image': wallpaper_image,
        }

# Run the spider
if __name__ == "__main__":
    results_dir = 'results'
    results_file = f'{results_dir}/results.json'
    
    # Create the results directory if it does not exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Remove the existing results file before running the spider
    if os.path.exists(results_file):
        os.remove(results_file)
    
    process = CrawlerProcess()
    process.crawl(IMDbSpider)
    process.start()
