import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

visited_urls = set()

def write_into_json(filename, str):
    with open('filenames.txt', "a") as file:
        file.write(filename + '\n')
    scrape_irs_news(filename, str)

def scrape_irs_news(filename, str):
    # url = "https://www.irs.gov/newsroom/news-releases-for-current-month"
    # response = requests.get(url)
    soup = BeautifulSoup(str, "html.parser")

    data = []

    for div in soup.find_all("div", class_="field_pup_media_document_teaser"):
        link = div.find("a")
        heading = link.find("span").get_text(strip=True)
        href = link["href"]
        description = extract_description_from_link("https://www.irs.gov" + href)
        next_sibling = div.find_next_sibling()
        while next_sibling and next_sibling.name != "div" and "field--name-field-pup-description-abstract" not in next_sibling.get("class", []):
            next_sibling = next_sibling.find_next_sibling()
        
        if next_sibling:
            content_div = next_sibling
            content = content_div.get_text(strip=True)
        else:
            content = "No content found"
        
        data.append({"heading": heading, "link": href, "content": content, "description": description})

    # Write the data to a JSON file
    if data:
        with open(f'{filename}.json', "w") as f:
            json.dump(data, f, indent=4)

    print(f"Data scraped and saved to {filename}.json")

def valid_filename(s):
    """Generate a valid filename from a URL."""
    s = s.replace('http://', '').replace('https://', '').replace('www.', '')
    return "".join(x for x in s if x.isalnum() or x in ('-', '_')).rstrip()

def crawl(url, base_url=None):
    if base_url is None:
        base_url = url

    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            filename = valid_filename(urlparse(url).netloc + urlparse(url).path)
            write_into_json(filename, response.text)

            for link in soup.find_all('a'):
                href = link.get('href')
                if href and "multimedia-center" not in href and "irs-media-relations-office-contact-number" not in href:
                    full_url = urljoin(base_url, href)
                    if full_url.startswith(f'{base_url}'):
                        crawl(full_url, base_url)
        else:
            print("Failed to retrieve webpage. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", str(e))

def extract_description_from_link(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    description = ""
    for div in soup.find_all("div", class_="field--type-text-with-summary"):
        for tag in div.find_all():
            description += tag.get_text(strip=True) + " "
    return description.strip()

if __name__ == "__main__":
    url = 'https://www.irs.gov/newsroom'
    crawl(url)