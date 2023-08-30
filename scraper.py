import requests
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
import hashlib
# MongoDB Atlas connection URI with the password properly encoded
password = quote_plus("M15@2dwin0n7y")
uri = f"mongodb+srv://stevefox_linux:{password}@cluster0.cz85k.mongodb.net/?retryWrites=true&w=majority"
def is_important_element(tag):
    # Implement your logic here to determine if the tag is important
    # For example, you might check for specific classes, IDs, or other attributes.
    # Return True if the tag is important, otherwise return False.
    return True  # Replace this with your actual logic
def web_scraper(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    important_content = soup.find_all(is_important_element)

    data = []

    for element in important_content:
        image_urls = [img['src'] for img in element.find_all('img')]
        titles = [title.text for title in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        paragraphs = [p.text for p in element.find_all('p')if p.text.strip()]
        if image_urls and titles and paragraphs:
              content_data = {
                  "ImageURLs": image_urls,
                  "Titles": titles,
                  "Paragraphs": paragraphs
              }

              data.append(content_data)

    return data
def scrape(urls):
    def web_scraper(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        important_content = soup.find_all(is_important_element)

        data = []

        for element in important_content:
            try:
                image_urls = [img['src'] for img in element.find_all('img')]
            except KeyError:
                image_urls = []

            titles = []
            for title in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                try:
                    titles.append(title.text)
                except AttributeError:
                    pass

            paragraphs = []
            for p in element.find_all('p'):
                if p.text.strip():
                    try:
                        paragraphs.append(p.text)
                    except AttributeError:
                        pass

            if image_urls and titles and paragraphs:
                content_data = {
                    "ImageURLs": image_urls,
                    "Titles": titles,
                    "Paragraphs": paragraphs
                }

                data.append(content_data)


        return data

    url = urls  # Replace with the URL you want to scrape
    #print(url)
    id = hashlib.sha256(url.encode()).hexdigest()
    scraped_data_list = web_scraper(url)


    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['scrape']
    # collection = db['index_table']
    # data = {"link": url, "data_id": id}
    # collection.insert_one(data)
    # print("inserthead")

    all4_data = db['all_data']
    # index_title = db['index_title']
    # index_paragraph = db['index_paragraph']
    for scraped_data in scraped_data_list:
        print(scraped_data)
        image_urls = scraped_data['ImageURLs']
        titles = scraped_data['Titles']
        paragraphs = scraped_data['Paragraphs']
        for img, title, des in zip(image_urls, titles, paragraphs):
            all4_data.insert_one({"image": img, "title": title, "des": des, "url": url})

    print(url)
    return "";

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['crawler']
collection = db['urls']
data = collection.find({})

 
for urls in data:
    db2 = client['scrape']
    collection2 = db2['all_data']
    existing = collection2.find_one({"url": urls['url']})
    if existing:
      collection.delete_many({"url": urls['url']})
      print('delete')
    else:
      scrape(urls['url'])
      collection.delete_many({"url": urls['url']})
       