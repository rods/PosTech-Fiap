import requests
from bs4 import BeautifulSoup
import csv
import boto3
import os
from io import StringIO
from datetime import datetime


def get_book_category(book_url):
    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        breadcrumb = soup.find('ul', class_='breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) >= 3:
                category = links[2].text.strip()
                return category
        
        return "general"
    except:
        return "general"


def lambda_handler(event, context):
    books = []
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    
    for page in range(1, 6):
        print(f"Scraping page {page}...")
        url = base_url.format(page)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_containers = soup.find_all('article', class_='product_pod')
            
            for container in book_containers:
                title_element = container.find('h3').find('a')
                title = title_element.get('title')
                book_url = 'https://books.toscrape.com/catalogue/' + title_element.get('href')
                
                price_element = container.find('p', class_='price_color')
                price_text = price_element.text.strip() if price_element else '£0.00'
                price = float(price_text.replace('£', ''))
                
                rating_element = container.find('p', class_='star-rating')
                rating_text = rating_element.get('class')[1] if rating_element else None
                rating = rating_map.get(rating_text, 0)
                
                availability_element = container.find('p', class_='instock availability')
                availability = availability_element.text.strip() if availability_element else 'Unknown'
                
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
                
        except requests.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            continue
    
    # Convert to CSV
    csv_buffer = StringIO()
    fieldnames = ['id', 'title', 'price', 'rating', 'availability', 'category']
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(books)
    
    # Upload to S3
    s3 = boto3.client('s3')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"books_general_{timestamp}.csv"
    
    bucket_name = os.environ.get('BUCKET_NAME', 'scrape-output')
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    return {
        'statusCode': 200,
        'body': f'Scraped {len(books)} books and saved to s3://{bucket_name}/{key}'
    }