# data_pipeline.py (깃허브 로봇용 최종 버전)
import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
from google import genai 

# 💡 깃허브 비밀 금고에서 API 키를 안전하게 꺼내옵니다.
MY_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=MY_API_KEY) 

print("데이터 수집 및 수(Su)의 분석을 시작합니다...")

# 1. 뉴스 데이터 수집
news_keyword = "제주 신라호텔"
news_url = f"https://news.google.com/rss/search?q={news_keyword}&hl=ko&gl=KR&ceid=KR:ko"
news_soup = BeautifulSoup(requests.get(news_url).text, 'xml')
news_titles = [item.title.text for item in news_soup.find_all('item')[:3]]

# 2. 날씨 데이터 수집
weather_url = "https://wttr.in/Seogwipo?format=j1&lang=ko"
weather_data = requests.get(weather_url).json()['current_condition'][0]
condition = weather_data.get('lang_ko', [{'value': weather_data['weatherDesc'][0]['value']}])[0]['value']
weather_summary = f"기온 {weather_data['temp_C']}도, 상태 {condition}"

# 3. AI 인사이트 요약
prompt = f"""
당신은 롯데호텔 제주의 시니어 마케터입니다. 
오늘의 수집된 데이터를 바탕으로, 경영진 대시보드 최상단에 올라갈 '오늘의 마케팅 인사이트 3줄 요약'을 작성해 주세요.

[오늘의 데이터]
- 경쟁사 주요 뉴스: {news_titles}
- 제주 서귀포 날씨: {weather_summary}

[작성 조건]
- 반드시 번호를 매겨 딱 3줄로만 작성할 것.
- 날씨에 맞춰 우리 호텔(롯데호텔 제주)의 부대시설이나 프로모션 마케팅 팁을 포함할 것.
- 경쟁사 뉴스 동향을 가볍게 터치할 것.
"""

response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)

# KST(한국 시간) 기준으로 업데이트 시간 설정
kst_time = datetime.datetime.utcnow() + datetime.timedelta(hours=9)

# 4. JSON 파일 덮어쓰기
final_data = {
    "updated_at": kst_time.strftime("%Y-%m-%d %H:%M"),
    "ai_insight": response.text,
    "weather": weather_summary,
    "news": news_titles
}

with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)

print("✅ 자동 업데이트 완료!")
