import json
from threading import Timer
import scrapy
import hashlib
import time
import numpy as np
import self as self

NONCE_LIMIT = 4000000000

zeros = 19

bitcoin_receiving_address = "bc1q8zckre9dnupcp58wmftey6jtf7sum9wmd5l4zh"


# random_scores = np.arange(stop= 4000000000,start=3000000000,step=1)
# print("random_scores",random_scores)

def mining(block_number, transactions, previous_hash):
    for nonce in range(3000000000, NONCE_LIMIT):
        base_text = str(block_number) + transactions + previous_hash + str(nonce)
        hash_find = hashlib.sha256(base_text.encode()).hexdigest()
        if hash_find.startswith('0' * zeros):
            print(f"Found Hash with nonce: {nonce}")
            return hash_find

    return -1


class BtcaddSpider(scrapy.Spider):
    name = 'btcadd'
    allowed_domains = ['www.blockchain.com']
    start_urls = ['https://www.blockchain.com/btc/blocks?page=1']
    dictionary = {}

    def parse(self, response):
        link = response.xpath('//*[@class="sc-1r996ns-0 fLwyDF sc-1tbyx6t-1 kCGMTY iklhnl-0 eEewhk"]/@href').get()
        url = "https://www.blockchain.com" + link
        yield scrapy.Request(url=url, callback=self.parse_info)

    def parse_info(self, response):
        AllList = response.xpath(
            '//*[@class="sc-1ryi78w-0 cILyoi sc-16b9dsl-1 ZwupP u3ufsr-0 eQTRKC"]/text()').extract()
        previousHash1 = response.xpath('//*[@class="sc-16b9dsl-0 hiLnJO"]/span/text()').get()

        ind = AllList.index(previousHash1)
        reqList = AllList[ind:]

        blockNumber = reqList[3]
        difficulty = reqList[5]

        self.dictionary.update({
            'previousHash': previousHash1,
            'blockNumber': blockNumber,
            'difficulty': difficulty
        })
        yield scrapy.Request(url="https://www.blockchain.com/btc/unconfirmed-transactions",
                             callback=self.parse_transaction)

    def parse_transaction(self, response):
        transaction = response.xpath(
            '//*[@class="sc-1r996ns-0 fLwyDF sc-1tbyx6t-1 kCGMTY iklhnl-0 eEewhk d53qjk-0 ctEFcK"]/text()').get()
        self.dictionary.update({
            'transaction': transaction
        })
        print("requests", self.dictionary)

    def send_data(self):
        with open('12fyE3UzpDFKqH19qY7kz2RLM6eDrNPkkD', 'w') as f:
            f.write(json.dumps(self.dictionary))
            print("requests after 2 minutes", self.dictionary)

        Timer(120, self.send_data).start()


