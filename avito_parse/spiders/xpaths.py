AVITO_PAGE_XPATH = {
    "all_flats": '//a[@title="Все квартиры"]/@href',
    "pagination": '//a[@class="pagination-page"]/@href',
    "flat": '//a[@data-marker="item-title"]/@href',
}

AVITO_FLAT_XPATH = {
    # "url": '//meta[@property="og:url"]/@content',
    "title": '//span[@class="title-info-title-text"]/text()',
    "price": '//script[contains(text(), "window.dataLayer = ")]',
    "address": '//span[@class="item-address__string"]/text()',
    "param": '//span[@class="item-params-label"]/text()',
    "value": '//li[@class="item-params-list-item"/text()]',
    "seller_url": '//div[@data-marker="seller-info/name"]/a/@href'
}
