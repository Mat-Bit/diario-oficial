import dateparser

from datetime import datetime
from scrapy import Request
from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider



class RjDuqueDeCaxias(BaseGazetteSpider):
    MUNICIPALITY_ID = '3301702'
    PDF_URL = 'http://duquedecaxias.rj.gov.br{}'

    DATE_CSS = 'span.article-date::text'
    DATE_RE = r'([\d]+)[ |]+([\w]+)[ |]+([\d]+)'
    GAZETTE_CSS = 'ul.jornal li'
    NEXT_PAGE_CSS = 'ul.pagination li.next a::attr(href)'
    PDF_HREF_CSS = 'a::attr(href)'

    allowed_domains = ['duquedecaxias.rj.gov.br']
    name = 'rj_duque_de_caxias'
    start_urls = ['http://duquedecaxias.rj.gov.br/portal/boletim-oficial.html']

    def parse(self, response):
        """
        @url http://duquedecaxias.rj.gov.br/portal/boletim-oficial.html
        @returns requests 1
        @scrapes date file_urls is_extra_edition municipality_id power scraped_at
        """

        for element in response.css(self.GAZETTE_CSS):
            url = self.extract_url(element)
            date = self.extract_date(element)

            yield Gazette(
                date=date,
                file_urls=[url],
                is_extra_edition=False,
                municipality_id=self.MUNICIPALITY_ID,
                power='executive_legislature',
                scraped_at=datetime.utcnow(),
            )

        for url in response.css(self.NEXT_PAGE_CSS).extract():
            yield Request(url)

    def extract_url(self, element):
        href = element.css(self.PDF_HREF_CSS).extract_first()
        return self.PDF_URL.format(href)

    def extract_date(self, element):
        date = element.css(self.DATE_CSS).re(self.DATE_RE)
        date = '/'.join(date)
        return dateparser.parse(date, languages=['pt']).date()
