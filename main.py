'''
目標網站: https://news.ltn.com.tw/ajax/breakingnews/world/$page

資料格式:
{
    "code: 200,
    "data": [
        {
            "no": "4873738", //新聞編號
            "title": "自由說新聞》中國又跳腳！蔡英文加拿大演說「神回」酸爆習近平", //新聞標題
            "bigphoto_flag": "0", //是否有大圖
            "photo_S": "https://img.ltn.com.tw/Upload/news/250/2024/11/24/phpsxFow4.jpg", //小圖
            "photo_L": "https://img.ltn.com.tw/Upload/news/600/2024/11/24/phpsxFow4.jpg", //大圖
            "url": "https://news.ltn.com.tw/news/world/breakingnews/4873738", //新聞連結
            "time": "16:48", //發布時間，當天新聞不會有日期，從前一天往前才會有 => time: "2024/11/23 17:59"
            "type_en": "world", //新聞類型
            "group": "breakingnews", //新聞分類
            "type_cn": "國際", //新聞類型(中文)
            "local": "", //地區
            "summary": "\r\n\r\n【更多內容  請見影片】\r\n訂閱【自由追新聞】\r\n全新的視界！新聞話題不漏接，快訂閱YouTube 【自由追新聞】，記得開啟小鈴鐺哦！", //新聞摘要
            "video": "1", //是否有影片
            "width": "800", //大圖寬度
            "height": "450", //大圖高度 
            "localUrl": "", //地區連結
            "tagUrl": "list/breakingnews/world", //新聞標籤連結
            "style": null, //樣式
            "tagText": "國際" //新聞標籤
        },
    ],
}

一個請求 20 筆資料
'''
import time

import requests
import jieba
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties as font
from wordcloud import WordCloud


class News():
    '''
    取得新聞資料格式
    '''
    def __init__(self, no: str, title: str, url: str, time: str):
        self.no = no
        self.title = title
        self.url = url
        self.time = time


def getNews(max_page: int, headers: dict, start_page: int=1, delay_time:float=1) -> list:
    news_list = []
    for i in range(start_page, max_page+1):
        url = f"https://news.ltn.com.tw/ajax/breakingnews/world/{i}"

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                raw_data = response.json()
                news_data = raw_data['data']
                news_no_list = []
                for news in news_data:
                    news_list.append(News(news_data[news]['no'], news_data[news]['title'], news_data[news]['url'], news_data[news]['time']))
            
        except Exception as e:
            raise e

        time.sleep(delay_time)
    return news_list


def getNewsContent(news: News, headers: dict) -> str:
    response = requests.get(news.url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='text boxTitle boxText')

        if content_div:
            content = []
            for paragraph in content_div.find_all('p'):
                text = paragraph.get_text(strip=True)
                # 過濾無用的段落
                if not text or "點我下載APP" in text or "按我看活動辦法" in text or "請繼續往下閱讀..." in text:
                    continue
                content.append(text)
            return " ".join(content)
        else:
            print(f"Content not found for: {news.url}")
            return ""
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}")


def processTextForWordCloud(content: str, stopwords: set) -> str:
    # 使用 jieba 進行斷詞
    words = jieba.cut(content, cut_all=False)
    filtered_words = [
        word for word in words if word not in stopwords and len(word.strip()) > 1]
    return " ".join(filtered_words)


def generateWordCloud(words: str, output_path: str = "wordcloud.png"):
    font1 = font(
        fname="./NotoSansTC-Regular.ttf")
    
    # 生成文字雲
    wordcloud = WordCloud(
        font_path="NotoSansTC-Regular.ttf",
        width=800,
        height=600,
        background_color="white",
        max_words=200,
    ).generate(words)

    # 顯示文字雲
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    # 儲存文字雲圖
    wordcloud.to_file(output_path)
    

def loadStopWords(filepath: str) -> set:
    """
    載入停用詞表
    """
    stopwords = set()
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            stopwords.add(line.strip())
    return stopwords

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    # 載入停用詞表
    stopwords = loadStopWords("stopwords.txt")
    
    print(f"Fetching news list, please wait...")
    news_list = getNews(max_page=3, headers=headers, start_page=2, delay_time=0)
    
    all_content = ""
    for news in news_list:
        print(f"Fetching content for: {news.title}, published at {news.time}")
        news_content = getNewsContent(news, headers=headers)
        all_content += news_content + " "

    # 斷詞
    print("Processing text for word cloud...")
    processed_text = processTextForWordCloud(all_content, stopwords)

    # 生成文字雲
    print("Generating word cloud...")
    generateWordCloud(processed_text, output_path="news_wordcloud.png")
