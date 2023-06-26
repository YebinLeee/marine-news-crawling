### Crawler

- [Base URL : 한국 해운 신문](http://www.maritimepress.co.kr/)
    - 각 분야별 기사 목록 BASE URL : http://www.maritimepress.co.kr/news/articleList.html?sc_sub_section_code=[sub section 코드]&view_type=sm
        ```
        - 해운 분야 코드
            - 외항 : S2N1
            - 내항 : S2N2
            - 정책 : S2N3
            - 선원 : S2N4
            - 여객선 : S2N5
            - 금융/보험 : S2N6
        - 항만 분야 코드
            - 하역 : S2N7
            - 정책 : S2N8
            - 개발 : S2N9
            - 국제 : S2N10
            - 지방 : S2N11
        - Cargo Korea 코드
            - 정책 : S2N12
            - 복합운송 : S2N13
            - 3PL : S2N14
            - 육상운송 : S2N15
            - 히주 : S2N16
        ```
        



### OpenAI API
- `openai` module 사용
- `ChatCompletion` api와 model `gpt-3.5-turbo` 를 사용하여 task 수행

```python
import openai
from decouple import config

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
```

## News Crawling
- `BeautifulSoup` 라이브러리를 이용하여 '해운-내항' 카테고리의 기사 목록을 크롤링한 예제
- `/crawl_news` 로 GET 요청 시, 각 기사의 title, 기사 contents, 링크 리스트들을 전달

```python

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import json

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
```

### Example Output
```
[
    {
        "title":"희양장학재단, 한국해대에 장학금 전달",
        "link":"/news/articleView.html?idxno=315702",
        "content":[
            "희양장학재단(이사장 김수금)이 한국해양대학교에 장학금 1천만원을 전달했다.",
            "한국해양대학교(총장 도덕희)는 6월 15일 대학본부에서 희양장학재단 장학금 전달식을 개최했다고 밝혔다. 희양장학재단은 한국해대생 5명을 장학생으로 선발해 각각 200만 원씩 총 1천만 원의 장학금을 전달했다.",
            "희양장학재단은 대륙상운 김수금 명예회장이 해양산업 발전의 토대를 만들고 적극적인 해양 인재 육성을 위해 설립한 재단으로 후학 양성을 위해 한국해양대에 장학금을 꾸준히 전달해 오고 있다. 특히 코로나19로 어려운 시기에도 장학금을 잇따라 전달하며 지역사회의 귀감이 되기도 했다.",
            "이날 자리에는 한국해양대 도덕희 총장, 희양장학재단 조규성 부사장과 김성철 사무국장, 최석윤 교무처장, 김홍승 학생처장, 김진권 해사대학장 등 대내·외 주요 인사가 참석했다.",
            "도덕희 한국해양대 총장은 “이 장학금이 학생들의 학업 수행과 목표 실현의 계기가 되기를 바란다. 우리 대학 학생들을 위하여 노력해 주시는 희양장학재단 관계자 분께 감사의 말씀을 드린다”고 말했다.",""
        ]
    },
]
```