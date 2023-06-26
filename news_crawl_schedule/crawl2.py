import time
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

@app.get("/crawl_news")
def crawl_news():
    url = "http://www.maritimepress.co.kr/news/articleList.html?sc_sub_section_code=S2N2&view_type=sm"
    base_url = "http://www.maritimepress.co.kr"
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, "html.parser")
    
        
    thumb_elements = soup.find_all("a", class_="thumb")
    href_list = [element["href"] for element in thumb_elements]
    
    for e in href_list:
        if e == '':
            continue
        response = requests.get(base_url + e)
        soup2 = BeautifulSoup(response.content, "html.parser")
        content_div = soup2.find(id="article-view-content-div")
        paragraphs = content_div.find_all("p")
        content_list = [p.get_text(strip=True) for p in paragraphs]
        print(content_list[0])



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