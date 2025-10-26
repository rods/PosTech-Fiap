import requests
from bs4 import BeautifulSoup
import json
import time

def get_book_category(book_url):
    """Get category from individual book page breadcrumb"""
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find breadcrumb navigation
        breadcrumb = soup.find('ul', class_='breadcrumb')
        if breadcrumb:
            # Get all breadcrumb links
            links = breadcrumb.find_all('a')
            if len(links) >= 3:  # Home > Books > Category > Book
                category = links[2].text.strip()
                return category
        
        return "general"
    except:
        return "general"

def scrape_books_with_categories():
    books = []
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    
    for page in range(1, 3):  # Scrape first 2 pages for faster execution
        print(f"Scraping page {page}...")
        url = base_url.format(page)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_containers = soup.find_all('article', class_='product_pod')
            
            for container in book_containers:
                # Get title and book URL
                title_element = container.find('h3').find('a')
                title = title_element.get('title')
                book_relative_url = title_element.get('href')
                book_url = f"https://books.toscrape.com/catalogue/{book_relative_url}"
                
                # Get price
                price_element = container.find('p', class_='price_color')
                price = price_element.text.strip()
                
                # Get rating
                rating_element = container.find('p', class_='star-rating')
                rating = rating_element.get('class')[1] if rating_element else 'Unknown'
                
                # Get availability
                availability_element = container.find('p', class_='instock availability')
                availability = availability_element.text.strip() if availability_element else 'Unknown'
                
                # Get category from individual book page
                print(f"  Getting category for: {title}")
                category = get_book_category(book_url)
                
                book = {
                    "id": len(books) + 1,
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "availability": availability,
                    "category": category
                }
                
                books.append(book)
                time.sleep(0.5)  # Be respectful to the server
                
        except requests.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            continue
    
    return books

if __name__ == "__main__":
    print("Starting book scraping with categories...")
    scraped_books = scrape_books_with_categories()
    
    # Save to JSON file
    with open("books.json", "w", encoding="utf-8") as f:
        json.dump(scraped_books, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(scraped_books)} books with real categories and saved to books.json")