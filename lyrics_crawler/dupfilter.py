import os

from scrapy.dupefilter import RFPDupeFilter


class URLFilter(RFPDupeFilter):
    def request_seen(self, request):
        if request.url in self.fingerprints:
            return True
        self.fingerprints.add(request.url)
        if self.file:
            self.file.write(request.url + os.linesep)
