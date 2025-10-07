import scrapy
import json
import math
import random
import time

class ZillowSpider(scrapy.Spider):
    name = "zillow"
    allowed_domains = ["zillow.com"]

    # Fresh cookies
    cookies = {
        "zguid": "24|%241c7c7415-9068-4626-82d9-292c747e57ba",
        "_pxvid": "d68b4294-a09c-11f0-b96e-aac88f2b553e",
        "AWSALB": "BXSb6KHX0vRgj1XMELTC5p7+H1p2auuGF0/4SS2DQ1QXA3qTMu9emLVAT6NkhEOeRSdlR0MmAvRkPtY2jHIFIviSaeMzXuC+NZYgMaqCPjhaeDhfGWvOEiysa/ZA",
        "AWSALBCORS": "BXSb6KHX0vRgj1XMELTC5p7+H1p2auuGF0/4SS2DQ1QXA3qTMu9emLVAT6NkhEOeRSdlR0MmAvRkPtY2jHIFIviSaeMzXuC+NZYgMaqCPjhaeDhfGWvOEiysa/ZA",
        "_gcl_au": "1.1.693369558.1759525597",
        "datagrail_consent_id": "7e84c9ce-057e-4c91-87ef-56e6d4914637.8a5be87f-23f5-46f4-9998-5b4d6525540d",
        "_scid": "pVhWDYhJiM6vr4NBthJTwaRtEo4wbMlD",
        "_sctr": "1|1759518000000",
        "g_state": '{"i_p":1759532827901,"i_l":1}',
        "search": "6|1762166176794|rect=34.624441198922916,-116.9011123828125,33.4133795516805,-119.9223526171875&rid=12447&disp=map&mdm=auto&p=1&listPriceActive=1&fs=1",
        "pxcts": "d68b4aee-a09c-11f0-b96e-452d411220fa",
        "_ga": "GA1.2.910916406.1759525592",
        "_gid": "GA1.2.1199002895.1759525592",
        "_clsk": "1b15fpv^1759575169086^3^0^n.clarity.ms/collect"
    }

    # Base URL
    base_url = "https://www.zillow.com/async-create-search-page-state"

    # Default city (can override via terminal argument)
    start_city = "Los Angeles, CA"

    # Map bounds for city (can adjust for other cities)
    city_bounds = {
        "west": -118.67,
        "east": -118.15,
        "south": 33.70,
        "north": 34.34
    }

    grid_size = 0.05  # smaller = more tiles

    # User-Agent pool
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0"
    ]

    def __init__(self, city=None, *args, **kwargs):
        super(ZillowSpider, self).__init__(*args, **kwargs)
        if city:
            self.start_city = city
            # TODO: Update self.city_bounds for other cities if needed
            self.logger.info(f"Scraping city: {self.start_city}")

    def start_requests(self):
        west, east = self.city_bounds["west"], self.city_bounds["east"]
        south, north = self.city_bounds["south"], self.city_bounds["north"]
        x_tiles = math.ceil((east - west) / self.grid_size)
        y_tiles = math.ceil((north - south) / self.grid_size)
        self.logger.info(f"City split into {x_tiles} x {y_tiles} = {x_tiles * y_tiles} tiles")

        for i in range(x_tiles):
            for j in range(y_tiles):
                bounds = {
                    "west": west + i * self.grid_size,
                    "east": min(west + (i + 1) * self.grid_size, east),
                    "south": south + j * self.grid_size,
                    "north": min(south + (j + 1) * self.grid_size, north)
                }
                yield from self.fetch_page(1, bounds)

    def fetch_page(self, page, bounds):
        payload = {
            "searchQueryState": {
                "pagination": {"currentPage": page},
                "usersSearchTerm": self.start_city,
                "mapBounds": bounds,
                "isMapVisible": True,
                "filterState": {},
                "isListVisible": True
            },
            "wants": {"cat1": ["listResults", "mapResults"]},
            "requestId": page
        }

        ua = random.choice(self.user_agents)
        time.sleep(random.uniform(1, 3))

        yield scrapy.Request(
            url=self.base_url,
            method="PUT",
            cookies=self.cookies,
            headers={
                "User-Agent": ua,
                "Content-Type": "application/json",
            },
            body=json.dumps(payload),
            callback=self.parse,
            meta={"page": page, "bounds": bounds}
        )

    def parse(self, response):
        try:
            data = json.loads(response.text)
            properties = data.get("cat1", {}).get("searchResults", {}).get("listResults", [])
            self.logger.info(f"Tile {response.meta['bounds']} page {response.meta['page']} - {len(properties)} items")

            for prop in properties:
                yield {
                    "address": prop.get("address"),
                    "price": prop.get("unformattedPrice"),
                    "beds": prop.get("beds"),
                    "baths": prop.get("baths"),
                    "area": prop.get("area"),
                    "zpid": prop.get("zpid"),
                    "statusType": prop.get("statusType"),
                    "statusText": prop.get("statusText")
                }

            if len(properties) > 0:
                next_page = response.meta["page"] + 1
                yield from self.fetch_page(next_page, response.meta["bounds"])

        except Exception as e:
            self.logger.error(f"Failed to parse page {response.meta['page']} bounds {response.meta['bounds']}: {e}")
