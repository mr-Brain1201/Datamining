from urllib.parse import urljoin

HH_PAGE_XPATH = {
    "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-next"]/@href',
    "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
    'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    "vacancy_employer": '//a[@class="bloko-link HH-LinkModifier"]/@href',
    "employer": '//a[@class="bloko-link bloko-link_secondary"]/@href'
}

HH_VACANCY_XPATH = {
    "title": '//h1[@data-qa="vacancy-title"]/text()',
    "salary": '//p[@class="vacancy-salary"]/span/text()',
    "description": '//div[@data-qa="vacancy-description"]//text()',
    "skills": '//div[@class="bloko-tag-list"]//'
    'div[contains(@data-qa, "skills-element")]/'
    'span[@data-qa="bloko-tag__text"]/text()',
    "author": '//a[@data-qa="vacancy-company-name"]/@href',
}

HH_EMPLOYER_XPATH = {
    "title": '//meta[@name="description"]/@content',
    "url": '//a[@class="g-user-content"]/@href',
    "area": '//div[@data-qa="sidebar-header-color"]/following-sibling::p/text()',
    "description": '//div[@class="g-user-content"]//text()'
}

HH_EMPLOYER_VACANCY_XPATH = {
    "vacancy": '//a[@class="bloko-link HH-LinkModifier"]/@href'
}