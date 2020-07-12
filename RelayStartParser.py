from base import Base
from bs4 import BeautifulSoup as bs
import requests


class RelayStartParser(Base):
    _identifier = 'relay-start'
    _base_url = 'http://relay-start.ru/products/'

    def _get_links(self, url) -> list:
        resp = requests.get(url)
        soup = bs(resp.content, 'html.parser')
        curr = soup.select('#app > section > div.uk-container.uk-margin-medium-bottom > div > '
                           'div.catalogue-menu__wrap.uk-position-relative.catalogue-'
                           'menu__wrap--small > div.catalogue-menu__wrap')
        links = []
        for link in curr[0].find_all('a'):
            if link['href'].startswith('/products/rele') and link['href'][len('/products/rele'):].count('/') > 1:
                curr_link = 'http://relay-start.ru{}'.format(link['href'])
                curr_code = requests.get(curr_link).content
                links.append((curr_link, curr_code))

        return links

    def _parse_by_link(self, url) -> dict:
        link = url[0]
        code = url[1]
        soup = bs(code, 'html.parser')
        d = {
            'Артикул': '',
            'Название продукции': '',
            'Классификация': '',
            'Ссылка': link,
            'Изображения': '',
            'Цена производителя': ''
        }
        keys = ([key.text.strip() for key in soup.find_all('div', {'class': 'product-field__label'})])
        values = ([value.text.strip() for value in soup.find_all('div', {'class': 'product-field__value'})])
        d.update(dict((list(zip(keys, values)))))
        classification = ''
        try:
            dv = soup.find('div', {'class': 'pathway uk-flex uk-flex-wrap uk-flex-middle'})
            keywords = [item['title'].strip() for item in dv.find_all('a')] + [dv.find('span').text.strip()]
            classification = '|'.join(keywords)
        except Exception as e:
            print('Excepted {} on {}'.format(e, link))
        finally:
            d['Классификация'] = classification

        try:
            slider = soup.find_all('div', {'class': 'uk-slider-container product-slider__container'})
            img_items = slider[0].find_all('li', {'class': 'product-slider__item uk-position-relative'})
            img_items.append(slider[0].find('li', {'class': 'product-slider__item uk-position-relative uk-active'}))
            images = '|'.join(['http://relay-start.ru{}'.format(item.a['href']) for item in img_items])
        except Exception as e:
            print('Excepted {} on {}'.format(e, link))
        finally:
            d['Изображения'] = images
        return d
