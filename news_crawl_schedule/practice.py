from crawl import generate_summary, crawl_news
import openai 

if __name__ == '__main__':
    article_list = crawl_news()
    article_content = ''.join(article_list[0]['content'])
    print(article_content)
    print(generate_summary(article_content))
