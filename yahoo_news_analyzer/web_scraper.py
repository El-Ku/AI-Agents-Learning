import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from crewai import Agent, Task

import csv

class WebScraper():
        
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        
    def remove_duplicates(self, input_list):
        seen = set()
        result = []
        for item in input_list:
            if item not in seen:
                result.append(item)
                seen.add(item)
        return result

    # @tool("Scrape the yahoo page for news article urls")
    def scrape_news_urls(self,url):
        """Useful to scrape the website and extract the urls of news articles"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        webpage_content = response.content
        soup = BeautifulSoup(webpage_content, 'html.parser')
        articles = soup.find_all(class_='stream-item')
        links = []
        for article in articles:
            temp = article.find_all(class_='subtle-link')
            temp = BeautifulSoup(str(temp), 'html.parser')
            a_tags = temp.find_all('a')
            for a_tag in a_tags:
                link = a_tag.get('href')
                links.append(link)
        # print(links)
        # print("%%%%%%%%%%%%4")
        # print(self.remove_duplicates(links))
        # print("%%%%%%%%%%%%4")
        return self.remove_duplicates(links)
    
    # @tool("scrape the webpage")
    def scrape_a_whole_newsarticle(self, url):
        """Useful to scrape and return the content pointed by an url"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        urls = self.scrape_news_urls(url)
        print(urls)
        print("#############################")
        summaries = []
        final_outputs = []
        for url in urls:      
            print('News URL  : ',url)      
            response = requests.get(url, headers=headers)
            webpage_content = response.content
            # print(len(webpage_content))
            soup = BeautifulSoup(webpage_content, 'html.parser')
            full_article = soup.find_all(class_='caas-body')
            # print(len(full_article))
            # print(full_article)
            agent = Agent(
                role='News article summarizer',
                goal='Read a news article, understand it well, and rewrite it in at most 10 sentences',
                backstory="""You have in depth knowledge in the field of finance and can understand any news in the field of finance. 
                You have the ability to read any news article and summarize them without loosing any relevant information shared in the 
                original article""",
                allow_delegation=False)
            task = Task(
                agent=agent,
                description=f"""Analyze and summarize the content below, make sure to include the most relevant information in the summary, 
                return only the summary nothing else. Please remember that this summary will be used by a trader to judge
                whether the original news article will cause the price of the stock to go down or up. So do not loose any relevenat details in 
                the rewritten paragraph. \n\nCONTENT\n----------\n{full_article}""",
                expected_output=f"""A single paragraph of 10 sentences or more, containing the summary of an article followed by the 'Summary :' tag.
                Example output format is given below:
                    Summary   : Adobe's stock price rose nearly 15% after the company reported strong earnings for the second quarter 
                                of fiscal 2024. Despite beating analyst expectations in revenue and earnings, the stock is still down 12% for 
                                the year. Adobe's growth has slowed in recent years due to challenges in its digital media and digital experience 
                                divisions, as well as competition from newer players in the market. The company is trying to boost sales with its 
                                generative AI platform Firefly, but so far, it hasn't had a significant impact. Looking ahead, Adobe expects its 
                                revenue and earnings to grow, but investors should be wary of potential challenges such as regulatory scrutiny and 
                                competition. While Adobe's stock is trading at a reasonable valuation compared to its peers, it may struggle to match
                                the market cap of larger tech companies like Apple in the long run.
                """,
                verbose=False
            )
            summary = task.execute()
            summaries.append(summary)
            print(summary,'\n')
            agent = Agent(
                role='Stock market guru',
                goal=f'Read the summary of a news article and give an impact score to it based on how it will affect the price of {self.stock_symbol}',
                backstory="""You are an excellent trader and understands how stock markets work. You know how different news articles can
                affect market sentiments and can cause the price of a particular stock to go up or down. """,
                allow_delegation=False)
            task = Task(
                agent=agent,
                description=f"""Read the summary of a news article given below and give an impact score to it, ranging from -10 to +10.
                -10 means this news have a high probability to cause the price of {self.stock_symbol} to go down and 
                +10 means it will cause the price to go up. \n\nCONTENT\n----------\n{summary}""",
                expected_output=f"""Impact score and a short reasoning behind the particular score
                Example output format is given below:
                    Impact score : +8
                    Reasoning    :  The news article highlights Apple's strong performance over the past decade, but also points out concerns such 
                                    as its high valuation and limited growth prospects. This may lead to investors becoming cautious and potentially selling 
                                    off their AAPL shares, causing the price to go down.
                """,
                verbose=False
            )
            final_output = task.execute()
            final_outputs.append(final_output)
            print(final_output,'\n\n\n')
        return summaries, final_outputs
        