import time
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import json
import mysql.connector
import schedule
import openai 
from decouple import config

app = FastAPI()

@app.get("/crawl_news")
def crawl_news():
    url = "http://www.maritimepress.co.kr/news/articleList.html?sc_sub_section_code=S2N2&view_type=sm"
    base_url = "http://www.maritimepress.co.kr"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")
    
    # hrefs
    thumb_elements = soup.find_all("a", class_="thumb")
    href_list = [element["href"] for element in thumb_elements]
    
    # titles
    titles = soup.find_all("h4", class_="titles")
    title_list = []
    for title in titles:
        link = title.find("a")
        title_content = link.get_text(strip=TabError) if link else ""
        title_list.append(title_content)
    
    # contents
    content_list = []
    for e in href_list:
        if e == '':
            continue

        response = requests.get(base_url + e)
        soup2 = BeautifulSoup(response.content, "html.parser")

        content_div = soup2.find(id="article-view-content-div")
        paragraphs = content_div.find_all("p")
    
        # all contents
        content = [p.get_text(strip=True) for p in paragraphs]
        content_list.append(content)
        
    crawled_articles = []
    for title, link, content in zip(title_list, href_list, content_list):
        data = {"title": title, "link": link, "content": content}
        crawled_articles.append(data)
        
    return crawled_articles

def save_summary(summary):
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host= config('db-host'),
        user="admin",
        password="admin1234",
        database="smart"
    )
    
    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()
    
    # Insert the summary into the database
    insert_query = "INSERT INTO summaries (summary_text) VALUES (%s)"
    for sentence in summary:
        cursor.execute(insert_query, (sentence,))
    
    # Commit the changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()


def generate_summary(content):
    openai.api_key = config('key')
    
    task = "다음 해운 관련 기사를 세 문장으로 요약해주세요: "

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": task + content
            }])
    return completion.choices[0].message.content

def crawl_and_summarize():
    # Your crawling and summarization code here
    # ...

    # Schedule the task to run every 1 minute
    schedule.every(1).minutes.do(crawl_and_summarize)

    # Run the scheduled tasks indefinitely
    while True:
        schedule.run_pending()
        time.sleep(1)


def is_article_crawled(article_title):
    # Implement your own logic to check if the article has been crawled before
    # You can use a database or any other data store for this purpose
    # Return True if the article has been crawled, False otherwise
    return False


if __name__ == "__main__":
    while True:
        # Run the FastAPI server
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
        # Wait for 10 minutes before crawling again
        time.sleep(600)