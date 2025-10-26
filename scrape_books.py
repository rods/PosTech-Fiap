import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_books():
    books = []
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    
    for page in range(1, 6):  # Scrape first 5 pages
        print(f"Scraping page {page}...")
        url = base_url.format(page)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_containers = soup.find_all('article', class_='product_pod')
            
            for i, container in enumerate(book_containers):
                # Get title
                title_element = container.find('h3').find('a')
                title = title_element.get('title')
                
                # Get price
                price_element = container.find('p', class_='price_color')
                price = price_element.text.strip()
                
                # Get rating
                rating_element = container.find('p', class_='star-rating')
                rating = rating_element.get('class')[1] if rating_element else 'Unknown'
                
                # Get availability
                availability_element = container.find('p', class_='instock availability')
                availability = availability_element.text.strip() if availability_element else 'Unknown'
                
                book = {
                    "id": len(books) + 1,
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "availability": availability,
                    "category": "general"  # Default category since not available on listing page
                }
                
                books.append(book)
                
        except requests.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            continue
            
        time.sleep(1)  # Be respectful to the server
    
    return books

if __name__ == "__main__":
    print("Starting book scraping...")
    scraped_books = scrape_books()
    
    # Save to JSON file
    with open("books_scraped.json", "w", encoding="utf-8") as f:
        json.dump(scraped_books, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(scraped_books)} books and saved to books_scraped.json")