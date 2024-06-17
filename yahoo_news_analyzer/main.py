from crewai import Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import csv

from web_scraper import WebScraper

load_dotenv(".env")
llm = ChatOpenAI(model="gpt-3.5-turbo")

stock_symbol = 'AAPL'
starting_url = f"https://finance.yahoo.com/quote/{stock_symbol}/latest-news/"
web_scraper = WebScraper(stock_symbol)
summaries, final_outputs = web_scraper.scrape_a_whole_newsarticle(starting_url)
print("##################################")
for summary in summaries:
    print(summary)
print("##################################")
for final_output in final_outputs:
    print(final_output)
print("##################################")

# web_scraper = WebScraper()
# print("##################################")
# news_urls = web_scraper.scrape_news_urls(starting_url)
# print(type(news_urls), len(news_urls))
# with open('urls.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     # Write each row in the list to the CSV file
#     for url in news_urls:
#         writer.writerow([url])
# print(news_urls)
# print("##################################")
