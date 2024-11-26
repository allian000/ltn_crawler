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
from collections import Counter
import requests
import jieba
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from matplotlib.font_manager import FontProperties as font
from wordcloud import WordCloud


class News:
    """儲存新聞資訊"""

    def __init__(self, no: str, title: str, url: str, time: str):
        self.no = no
        self.title = title
        self.url = url
        self.time = time


class NewsCrawler:
    """負責抓取新聞資料"""

    def __init__(self, headers: dict, delay_time: float = 1):
        self.headers = headers
        self.delay_time = delay_time

    def fetch_news_list(self, max_page: int, start_page: int = 1) -> list:
        """抓取新聞列表"""
        news_list = []
        for i in range(start_page, max_page + 1):
            url = f"https://news.ltn.com.tw/ajax/breakingnews/world/{i}"
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    news_data = response.json().get("data", [])
                    for news in news_data:
                        news_list.append(
                            News(
                                news["no"], news["title"], news["url"], news["time"]
                            )
                        )
                time.sleep(self.delay_time)
            except Exception as e:
                print(f"Failed to fetch news list from page {i}: {e}")
        return news_list

    def fetch_news_content(self, news: News) -> str:
        """抓取單篇新聞內容"""
        try:
            response = requests.get(news.url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                content_div = soup.find("div", class_="text boxTitle boxText")
                if content_div:
                    content = []
                    for paragraph in content_div.find_all("p"):
                        text = paragraph.get_text(strip=True)
                        if (
                            not text
                            or "點我下載APP" in text
                            or "按我看活動辦法" in text
                            or "請繼續往下閱讀..." in text
                        ):
                            continue
                        content.append(text)
                    return " ".join(content)
        except Exception as e:
            print(f"Failed to fetch content for {news.title}: {e}")
        return ""


class TextProcessor:
    """負責文本處理"""

    def __init__(self, stopwords: set):
        self.stopwords = stopwords

    def process_text(self, content: str) -> str:
        """文本斷詞並過濾停用詞"""
        words = jieba.cut(content, cut_all=False)
        filtered_words = [
            word for word in words if word not in self.stopwords and len(word.strip()) > 1
        ]
        return " ".join(filtered_words)

    def calculate_word_frequency(self, content: str) -> Counter:
        """計算詞頻"""
        words = jieba.cut(content, cut_all=False)
        filtered_words = [
            word for word in words if word not in self.stopwords and len(word.strip()) > 1
        ]
        return Counter(filtered_words)

    @staticmethod
    def load_stopwords(filepath: str) -> set:
        """載入停用詞表"""
        stopwords = set()
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                stopwords.add(line.strip())
        return stopwords


class WordCloudGenerator:
    """負責生成文字雲"""

    @staticmethod
    def generate_word_cloud(text: str, output_path: str = "wordcloud.png"):
        """生成並保存文字雲"""
        wordcloud = WordCloud(
            font_path="NotoSansTC-Regular.ttf",
            width=800,
            height=600,
            background_color="white",
            max_words=200,
        ).generate(text)

        # 顯示文字雲
        plt.figure(figsize=(10, 8))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

        # 儲存文字雲
        wordcloud.to_file(output_path)
        print(f"Word cloud saved to {output_path}")


def save_word_frequency(word_frequency: Counter, filepath: str, max_records: int = None):
    """保存詞頻表到檔案"""
    with open(filepath, "w", encoding="utf-8") as file:
        for word, freq in word_frequency.most_common(max_records):
            file.write(f"{word}: {freq}\n")
    print(f"Word frequency table saved to {filepath}")


if __name__ == "__main__":
    # 初始化設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    stopwords_file = "stopwords.txt"
    max_records = 25

    # 載入停用詞表
    stopwords = TextProcessor.load_stopwords(stopwords_file)

    # 初始化各類別
    crawler = NewsCrawler(headers=headers, delay_time=1)
    processor = TextProcessor(stopwords=stopwords)
    cloud_generator = WordCloudGenerator()

    # 爬取新聞
    print("Fetching news list...")
    news_list = crawler.fetch_news_list(max_page=3, start_page=1)

    # 爬取內容並處理
    print("Fetching and processing news content...")
    all_content = ""
    for news in news_list:
        print(f"Fetching content for: {news.title} ({news.time})")
        content = crawler.fetch_news_content(news)
        all_content += content + " "

    # 斷詞與詞頻計算
    print("Processing text for word cloud...")
    processed_text = processor.process_text(all_content)
    word_frequency = processor.calculate_word_frequency(all_content)

    # 保存詞頻表
    save_word_frequency(word_frequency, "word_frequency.txt", max_records)

    # 生成文字雲
    print("Generating word cloud...")
    cloud_generator.generate_word_cloud(
        processed_text, output_path="news_wordcloud.png")

    print("All tasks completed.")
