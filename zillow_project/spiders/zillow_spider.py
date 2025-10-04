import scrapy
import json
import math
import random
import time

class ZillowSpider(scrapy.Spider):
    name = "zillow"
    allowed_domains = ["zillow.com"]

    # Cookies
    cookies = {
        "zguid": "24|%241c7c7415-9068-4626-82d9-292c747e57ba",
        "_pxvid": "d68b4294-a09c-11f0-b96e-aac88f2b553e",
        "AWSALB": "BXSb6KHX0vRgj1XMELTC5p7+H1p2auuGF0/4SS2DQ1QXA3qTMu9emLVAT6NkhEOeRSdlR0MmAvRkPtY2jHIFIviSaeMzXuC+NZYgMaqCPjhaeDhfGWvOEiysa/ZA",
        "AWSALBCORS": "BXSb6KHX0vRgj1XMELTC5p7+H1p2auuGF0/4SS2DQ1QXA3qTMu9emLVAT6NkhEOeRSdlR0MmAvRkPtY2jHIFIviSaeMzXuC+NZYgMaqCPjhaeDhfGWvOEiysa/ZA",
        "_gcl_au": "1.1.693369558.1759525597",
        "datagrail_consent_id": "7e84c9ce-057e-4c91-87ef-56e6d4914637.8a5be87f-23f5-46f4-9998-5b4d6525540d",
        "datagrail_consent_id_s": "7e84c9ce-057e-4c91-87ef-56e6d4914637.fef4f887-94ad-4f74-a850-dfb3ef7c084d",
        "_scid": "pVhWDYhJiM6vr4NBthJTwaRtEo4wbMlD",
        "_sctr": "1|1759518000000",
        "g_state": '{"i_p":1759532827901,"i_l":1}',
        "search": "6|1762166176794|rect=34.624441198922916,-116.9011123828125,33.4133795516805,-119.9223526171875&rid=12447&disp=map&mdm=auto&p=1&listPriceActive=1&fs=1&fr=0&mmm=0&rs=0&singlestory=0&housing-connector=0&parking-spots=null-&abo=0&garage=0&pool=0&ac=0&waterfront=0&finished=0&unfinished=0&cityview=0&mountainview=0&parkview=0&waterview=0&hoadata=1&zillow-owned=0&3dhome=0&showcase=0&featuredMultiFamilyBuilding=0&onlyRentalStudentHousingType=0&onlyRentalIncomeRestrictedHousingType=0&onlyRentalMilitaryHousingType=0&onlyRentalDisabledHousingType=0&onlyRentalSeniorHousingType=0&commuteMode=driving&commuteTimeOfDay=now",
        "pxcts": "d68b4aee-a09c-11f0-b96e-452d411220fa",
        "DoubleClickSession": "true",
        "_clck": "r22jnp^2^fzv^0^2102",
        "web-platform-data": '{"wp-dd-rum-session":{"doNotTrack":true}}',
        "zjs_anonymous_id": "1c7c7415-9068-4626-82d9-292c747e57ba",
        "zjs_user_id": "null",
        "zjs_user_id_type": '"encoded_zuid"',
        "zg_anonymous_id": "0b792b39-251d-40a5-ba3d-63ddce2e825c",
        "_ga": "GA1.2.910916406.1759525592",
        "_gid": "GA1.2.1199002895.1759525592",
        "_pin_unauth": "dWlkPU4yUmhaRGswTlRndFlXVTRaQzAwT0RBNExUbGlORFl0WkRaa05qYzFaRFJoWkRVeQ",
        "_rdt_uuid": "1759525600769.9038d054-f65a-420b-999f-d623507a43dc",
        "_scid_r": "v9hWDYhJiM6vr4NBthJTwaRtEo4wbMlDcQpgAQ",
        "_uetsid": "dc0ca390a09c11f0b01ceff65044b1ae",
        "_uetvid": "dc0ce5a0a09c11f0957ea7de4a7ac097",
        "_fbp": "fb.1.1759525601521.963015616451735157",
        "_tt_enable_cookie": "1",
        "_ttp": "01K6NYC0JM899Y9XXB28Y6KRPA_.tt.1",
        "ttcsid": "1759574157670::Pd36LQBLecb66IBVkRce.2.1759574191481.0",
        "ttcsid_CN5P33RC77UF9CBTPH9G": "1759574157668::nKeLg6gSvznWtuQJwXF-.2.1759574191482.0",
        "__gads": "ID=e90db578eba3a6c7:T=1759526861:RT=1759574193:S=ALNI_MbdD1aSsCA6OS-O-BFl5HbpFS6A2A",
        "__gpi": "UID=0000124cfaf805aa:T=1759526861:RT=1759574193:S=ALNI_Ma3dX0DDIAach7IPWmU-1gESbWUrg",
        "__eoi": "ID=712767c031828e96:T=1759526861:RT=1759574193:S=AA-AfjZFI-KWhdkcBp8u3n0gu7qK",
        "tfpsi": "5a0036e2-a859-4f3b-9880-f15f5bc4e974",
        "_px3": "f99095e148876f8e3bcdce5f6ffd4d676785ce363a6f83fbcf9950aa004e19d1:YRmrcJrN3wM69q22K8iOPnlZ2BCqeDRiOxV9SXTpVAj1ITQr75qh9GnIPX8vA/a52HlcCyhFOuuSO7TT/XEUjg==:1000:8JorX0frK+Ob3iBMsF8WaP7ZUuBiVTMCbNjS/rhT0EjhlvUT5vpbe8VLokQghZzwZRdEnp1PK/yGtFxrPi6G0Igy0Lf9/q3kiwrBgRgsAFStuTWy366zNevaEfzE/8JhNOx+vNXCpIOmXlhaGDd0mUJe59Nhg/gIEhwOT++QJDaUkNgIKC9CizjBqmNtBOs49V4Jugm+BK2hqUaU/JBqdoG0zHHhkWag/w/LpUxji08=",
        "_clsk": "1b15fpv^1759575169086^3^0^n.clarity.ms/collect"
    }

    start_city = "Los Angeles, CA"
    base_url = "https://www.zillow.com/async-create-search-page-state"

    city_bounds = {
        "west": -118.67,
        "east": -118.15,
        "south": 33.70,
        "north": 34.34
    }

    grid_size = 0.05  # smaller tiles = more requests

    # User-Agent pool
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0"
    ]

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

        # Random User-Agent
        ua = random.choice(self.user_agents)

        # Random sleep to mimic human behavior
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
