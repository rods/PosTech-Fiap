#!/bin/bash

# Create deployment packages for Lambda functions
mkdir -p lambda-packages

# Package for scrape_books
mkdir -p lambda-packages/scrape_books
cp scrape_books.py lambda-packages/scrape_books/
pip install -r requirements.txt -t lambda-packages/scrape_books/
cd lambda-packages/scrape_books
zip -r ../scrape_books.zip .
cd ../..

# Package for scrape_books_with_categories  
mkdir -p lambda-packages/scrape_books_with_categories
cp scrape_books_with_categories.py lambda-packages/scrape_books_with_categories/
pip install -r requirements.txt -t lambda-packages/scrape_books_with_categories/
cd lambda-packages/scrape_books_with_categories
zip -r ../scrape_books_with_categories.zip .
cd ../..

echo "Deployment packages created:"
echo "- lambda-packages/scrape_books.zip"
echo "- lambda-packages/scrape_books_with_categories.zip"
