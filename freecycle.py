from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests

import models


@dataclass
class Offer:

    id: str
    title: str
    url: str
    region: str

    def ack(self):
        with models.session_scope() as session:
            freecycle_entry = session.query(models.FreecycleOffer).filter(
                models.FreecycleOffer.id == self.id
            ).first()
            freecycle_entry.notified = True


class FreecycleChecker:

    def __init__(self):
        self.base_url = f"https://groups.freecycle.org/group/"

    @property
    def regions(self):
        return []

    def scan_freecycle(self):
        self.scan_regions()
        self.alert_listeners()

    def scan_regions(self):
        for region in self.regions:
            self.scan_region(region)

    def scan_region(self, region):
        pass

    def alert_listeners(self):
        pass

    def get_freecycle_offers(self, region):
        raw_table_rows = self.get_raw_table_rows(region)
        self.parse_raw_freecycle_data(raw_table_rows, region)
        with models.session_scope() as session:
            query = session.query(models.FreecycleOffer).filter(
                models.FreecycleOffer.notified.is_(False),
                models.FreecycleOffer.region == region,
            )
            new_offers = [Offer(result.title, result.id, result.url, region) for result in query.all()]
        return new_offers

    def get_new_offers(self, region=None):
        region = region if region is not None else 'CambridgeUK'
        new_offers = self.get_freecycle_offers(region)
        return new_offers

    def get_raw_table_rows(self, region):
        response = requests.get(f"{self.base_url}{region}/posts/offer", verify=False)
        soup = BeautifulSoup(response.text, features="html.parser")
        raw_table_rows = soup.find_all('tr')
        return raw_table_rows

    def parse_raw_freecycle_data(self, raw_table_rows, region):
        for row in raw_table_rows:
            columns = row.find_all('td')
            offer_title = columns[1].text.split('\n')[1].strip()
            offer_id = int(columns[1].find('a', href=True)['href'].split('/')[6])
            new_offer = models.FreecycleOffer(id=offer_id, title=offer_title, region=region)
            models.session.merge(new_offer)
            models.session.commit()
