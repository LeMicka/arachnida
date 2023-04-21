import sys
import os
import argparse
import requests
from tqdm import tqdm
import re
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

all_img_links = []
page_images = []
urls = []

def check_dir(path):
    if os.path.exists(path):
        return path
    else:
        os.mkdir(path)
    

def get_img_links(soup, url, path):
    page_images.clear()
    for image_src in soup.find_all("img"):
        src = image_src['src']
        if not str(image_src['src']).startswith('https'):
            full_link = urljoin(url, src)
        else:
            full_link = src
        img_name = full_link.split('/')[-1]
        if not full_link in all_img_links and not os.path.exists(path + img_name) and full_link.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            all_img_links.append(full_link)
            page_images.append(full_link)


def download_imgs(args, url, level, path):
    i = 0
    print(f"downloading images from {url} level {level}")
    for i in tqdm(range(len(page_images))):
        try:
            resp = requests.get(page_images[i])
        except:
            return -1
        if resp.status_code == 200:
            img_name = page_images[i].split('/')[-1]
            if not os.path.exists(path + img_name):
                with open (path + img_name, 'wb') as handler:
                    handler.write(resp.content)
        i = i + 1
    print()

    
    
def spider(args, level, url, path):
    try:
        resp = requests.get(url)
    except:
        return -1
    if level >= args.l or resp.status_code != 200:
        return -1
    try:
        soup = bs(resp.text,  features= 'html.parser')
    except:
        return -1
    get_img_links(soup, url, path)
    if len(page_images) == 0:
        print(f"images from {url} already downloaded\n")
    else:
        download_imgs(args, url, level, path)
    links = soup.find_all('a', href = True)
    for link in links:
        if link is None:
            continue
        else:
            new_link=link.get('href')
            if str(new_link).endswith('/'):
                new_link = new_link
            else:
                new_link = new_link + '/'
            if str(new_link).startswith(url) and not new_link in urls:
                urls.append(new_link)
                spider(args, new_link.count('/') - 3, new_link, path)   
                

def main():
    parser = argparse.ArgumentParser(description='The spider program will allow you to extract all the images from a website, recur-sively, by providing a url as a parameter')
    parser.add_argument('url', help = 'Url of the page',type=str,default="https://www.42malaga.com")
    parser.add_argument('-r', action = 'store_true', help = 'recursively downloads the images in a URL received as a parameter')
    parser.add_argument('-l', type = int, default = 5, 
                        help = 'indicates the maximum depth level of the recursive download.If not indicated, it will be 5.')
    parser.add_argument('-p', default = 'data',
                        help = 'indicates the path where the downloaded files will be saved. If not specified, ./data/ will be used.')
    args = parser.parse_args()
    if args.url.endswith('/'):
        url = args.url
    else:
        url = args.url + '/'
    try:
        requests.get(url)
    except:
        sys.exit("Given url not valid or not accessible")
    urls.append(url)
    path = args.p + '/'
    if not args.r and args.l:
        sys.exit("Activate recursivity [-r] to choose a depth [-l]")
    elif not args.r:
        args.l = 1
    check_dir(path)
    spider(args, 0, url, path)

if __name__ == "__main__":
    main()