import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# CSS를 이용한 기본 스타일 (https://techurls.com/ 참고)
st.markdown(
    """
    <style>
    body {
      background-color: #f4f4f4;
      font-family: 'Helvetica Neue', sans-serif;
    }
    .article {
      background-color: #fff;
      padding: 10px 15px;
      margin-bottom: 10px;
      border-radius: 5px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .article a {
      text-decoration: none;
      color: #333;
      font-weight: bold;
    }
    .article span {
      font-size: 0.8em;
      color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("뉴스 모음 웹앱")
st.write("새로운 기사들의 업로드 시각과 제목을 확인하세요. 제목을 클릭하면 해당 기사로 이동합니다.")

# --- 크롤링 함수들 ---
def get_hackernews_articles():
    articles = []
    try:
        res = requests.get("https://news.ycombinator.com/")
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find_all("tr", class_="athing")
        for item in items:
            title_tag = item.find("a", class_="storylink")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = title_tag.get("href")
            # 업로드 시간은 바로 아래 형제 tr의 subtext에서 추출
            subtext = item.find_next_sibling("tr").find("td", class_="subtext")
            time_text = ""
            if subtext:
                age = subtext.find("span", class_="age")
                if age:
                    time_text = age.get_text(strip=True)
            articles.append({
                "title": title,
                "time": time_text,
                "url": url,
                "source": "Hacker News"
            })
    except Exception as e:
        st.error(f"Hacker News 크롤링 에러: {e}")
    return articles

def get_theverge_articles():
    articles = []
    try:
        res = requests.get("https://www.theverge.com/")
        soup = BeautifulSoup(res.text, "html.parser")
        # The Verge의 기사들은 c-entry-box--compact 클래스 내에 있음
        boxes = soup.find_all("div", class_="c-entry-box--compact")
        for box in boxes:
            title_tag = box.find("h2", class_="c-entry-box--compact__title")
            if title_tag:
                a_tag = title_tag.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    url = a_tag.get("href")
                else:
                    continue
            else:
                continue
            # 시간은 <time> 태그에서 추출 (datetime 속성 또는 텍스트)
            time_tag = box.find("time")
            time_text = time_tag.get("datetime") if time_tag and time_tag.has_attr("datetime") else (time_tag.get_text(strip=True) if time_tag else "")
            articles.append({
                "title": title,
                "time": time_text,
                "url": url,
                "source": "The Verge"
            })
    except Exception as e:
        st.error(f"The Verge 크롤링 에러: {e}")
    return articles

def get_techcrunch_articles():
    articles = []
    try:
        res = requests.get("https://techcrunch.com/")
        soup = BeautifulSoup(res.text, "html.parser")
        # TechCrunch 기사는 <article> 태그로 구분됨
        for article in soup.find_all("article"):
            header = article.find("header", class_="post-block__header")
            if not header:
                continue
            a_tag = header.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            url = a_tag.get("href")
            time_tag = article.find("time")
            time_text = time_tag.get("datetime") if time_tag and time_tag.has_attr("datetime") else (time_tag.get_text(strip=True) if time_tag else "")
            articles.append({
                "title": title,
                "time": time_text,
                "url": url,
                "source": "TechCrunch"
            })
    except Exception as e:
        st.error(f"TechCrunch 크롤링 에러: {e}")
    return articles

def get_arstechnica_articles():
    articles = []
    try:
        res = requests.get("https://arstechnica.com/")
        soup = BeautifulSoup(res.text, "html.parser")
        # Ars Technica 기사는 보통 "li.tease" 클래스에 있음
        for li in soup.find_all("li", class_="tease"):
            title_tag = li.find("h2", class_="tease-title")
            if title_tag:
                a_tag = title_tag.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    url = a_tag.get("href")
                else:
                    continue
            else:
                continue
            time_tag = li.find("time")
            time_text = time_tag.get_text(strip=True) if time_tag else ""
            articles.append({
                "title": title,
                "time": time_text,
                "url": url,
                "source": "Ars Technica"
            })
    except Exception as e:
        st.error(f"Ars Technica 크롤링 에러: {e}")
    return articles

def fetch_all_articles():
    articles = []
    articles.extend(get_hackernews_articles())
    articles.extend(get_theverge_articles())
    articles.extend(get_techcrunch_articles())
    articles.extend(get_arstechnica_articles())
    return articles

# 자동 새로고침 버튼 (또는 st.experimental_rerun을 사용할 수도 있음)
if st.button("새로고침"):
    st.experimental_rerun()

# 기사 크롤링
with st.spinner("기사를 불러오는 중..."):
    articles = fetch_all_articles()

# 각 기사 출력
for art in articles:
    st.markdown(
        f"""
        <div class="article">
            <a href="{art['url']}" target="_blank">{art['title']}</a>
            <br>
            <span>{art['time']} | {art['source']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("※ 이 앱은 주기적으로 최신 기사를 크롤링합니다.")

# 배포 추천 안내
st.info("앱 배포는 [Streamlit Cloud](https://streamlit.io/cloud), Heroku, Render 등과 같은 서비스를 추천합니다.")
