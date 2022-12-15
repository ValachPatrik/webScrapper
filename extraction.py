# author: Patrik Valach
# 2021

import json
import os.path
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import bs4
import requests


class FullScrap(NamedTuple):
    linux_only_availability: List[str]
    most_visited_webpage: Tuple[int, str]
    changes: List[Tuple[int, str]]
    params: List[Tuple[int, str]]

    def as_dict(self) -> Dict[str, Any]:
        return {
            'linux_only_availability': self.linux_only_availability,
            'most_visited_webpage': self.most_visited_webpage,
            'changes': self.changes,
            'params': self.params,
        }


def download_webpage(url: str, *args, **kwargs) -> requests.Response:
    """
    Download the page and returns its response by using requests.get
    :param url: url to download
    :return: requests Response
    """
    print('GET ', url)
    return requests.get(url, *args, **kwargs)


def get_linux_only_availability(url_all: List[str]) -> List[str]:
    """
    Finds all functions that area available only on Linux systems
    :param base_url: base url of the website
    :return: all function names that area available only on Linux systems
    """
    linux = []
    for i in url_all:
        soup = get_soup(i)
        for j in soup.find_all('dl', class_='function'):
            avail = j.find('p', class_="availability")
            if avail is not None:
                avail = avail.get_text().split(',')
                only = True
                for k in avail:
                    if 'Linux' not in k and 'Unix' not in k:
                        only = False
                        break
                if only:
                    linux.append(j.find('dt', id=True)['id'])
    return linux


def get_most_visited_webpage(url_all: Dict[str, int]) -> Tuple[int, str]:
    """
    Finds the page with most links to it
    :param url_all: all urls to search
    :return: number of anchors to this page and its URL
    """
    return (max(url_all.values()), max(url_all, key=url_all.get))


def get_changes(url_all: List[str]) -> List[Tuple[int, str]]:
    """
    Locates all counts of changes of functions and groups them by version
    :param base_url: base url of the website
    :return: all counts of changes of functions and groups them by version, sorted from the most changes DESC
    """
    changes = {}
    for i in url_all:
        soup = get_soup(i)
        for j in soup.find_all('dl', class_='function'):
            avail = j.find_all('span', class_="versionmodified changed")
            avail.extend(j.find_all('span', class_="versionmodified added"))
            for k in avail:
                k = ''.join(filter(str.isdigit, k.string))[:2]
                if k not in changes:
                    changes[k] = 1
                else:
                    changes[k] += 1
    changes = [(v, k[0]+'.'+k[1]) for k, v in changes.items()]
    return sorted(changes, key=lambda x: x[0], reverse=True)


def get_most_params(url_all: List[str]) -> List[Tuple[int, str]]:
    """
    Finds the function that accepts more than 10 parameters
    :param base_url: base url of the website
    :return: number of parameters of this function and its name, sorted by the count DESC
    """
    most = []
    for i in url_all:
        soup = get_soup(i)
        for j in soup.find_all('dl', class_='function'):
            avail = len(j.find_all('em', class_="sig-param"))
            if avail > 10:
                most.append((avail, j.find('dt', id=True)['id']))
    most = sorted(most, key=lambda x: x[0], reverse=True)
    return most


def get_soup(url):
    if os.path.exists('site\{}.html'.format(url.replace(':', '').replace('/', ''))):
        page = open('site\{}.html'.format(
            url.replace(':', '').replace('/', '')), 'rb')
        soup = bs4.BeautifulSoup(page.read(), "html.parser")
    else:
        time.sleep(0.5)
        response = download_webpage(url)
        page = response.content
        soup = bs4.BeautifulSoup(page, "html.parser")
        html = soup.prettify("utf-8")
        if not os.path.exists('site'):
            os.makedirs('site')
        with open("site\{}.html".format(url.replace(':', '').replace('/', '')), "wb") as f:
            f.write(html)
    return soup


def get_all_url(base_url, url, url_all):
    soup = get_soup(url)
    a = soup.find_all('a', href=True)
    for i in a:
        i = i['href']
        if '#' in i:
            i = i[:i.find('#')]
        i = urllib.parse.urljoin(url, i)
        if base_url in i:
            if i not in url_all:
                url_all[i] = 1
                url_all = get_all_url(base_url, i, url_all)
            else:
                url_all[i] += 1
    return url_all


def scrap_all(base_url: str) -> FullScrap:
    """
    Scrap all the information as efficiently as we can
    :param base_url: base url of the website
    :return: full web scrap of the Python docs
    """
    if os.path.exists(r'all_url.json'):
        with open(r'all_url.json', 'r') as f:
            url_all = json.loads(f.read())
    else:
        url_all = get_all_url(base_url, base_url, {})
        with open(r'all_url.json', 'w') as f:
            f.write(json.dumps(url_all))
    scrap = FullScrap(
        linux_only_availability=get_linux_only_availability(url_all.keys()),
        most_visited_webpage=get_most_visited_webpage(url_all),
        changes=get_changes(url_all.keys()),
        params=get_most_params(url_all.keys()),
    )
    return scrap


def main() -> None:
    """
    Do a full scrap and print the results
    :return:
    """
    import json
    time_start = time.time()
    print(json.dumps(scrap_all('https://python.iamroot.eu/').as_dict()))
    print('took', int(time.time() - time_start), 's')


if __name__ == '__main__':
    main()
