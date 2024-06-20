import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import concurrent.futures
import time

def get_all_links(url):
    queue = deque([url])
    
    visited = set([url])
    
    found_links = set()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        with open('links.txt', 'w') as f:
            while queue:
                current_url = queue.popleft()
                
                try:
                    future = executor.submit(requests.get, current_url)
                    response = future.result() 
                except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema):
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link['href'].strip()
                    absolute_url = urljoin(current_url, href)
                    
                    parsed_url = urlparse(absolute_url)
                    normalized_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
                    
                    if normalized_url not in visited and parsed_url.netloc == urlparse(url).netloc:
                        visited.add(normalized_url)
                        queue.append(normalized_url)
                        found_links.add(normalized_url)
                        
                        print("Scraping:", normalized_url)
                        
                        f.write(normalized_url + '\n')
                        f.flush()  
                
                time.sleep(0.001)
    
    print("All links from the website saved to links.txt")

if __name__ == "__main__":
    website_url = input("Enter the website URL you want to scrape: ")
    get_all_links(website_url)
