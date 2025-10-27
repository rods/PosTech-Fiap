output "bucket_name" {
  value = aws_s3_bucket.scrape_output.bucket
}

output "scrape_books_function_arn" {
  value = aws_lambda_function.scrape_books.arn
}

output "scrape_books_with_categories_function_arn" {
  value = aws_lambda_function.scrape_books_with_categories.arn
}
