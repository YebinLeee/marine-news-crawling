from crawl import generate_summary, crawl_news
import openai 

if __name__ == '__main__':
    article_list = crawl_news()
    article_conent = ''.join(content_list[0]['content'])
    print(article_contents)
    print(generate_summary(article_conent))
