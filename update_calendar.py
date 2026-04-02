import os
import requests
import pytz
from datetime import datetime, timedelta
from icalendar import Calendar, Event

# --- 설정 (서울 기준) ---
# 본인 지역에 맞는 nx, ny, reg_id는 기상청 가이드를 참고하세요.
NX = 60
NY = 127
REG_ID = '11B10101' # 중기육상예보 (서울)
REG_TEMP_ID = '11B10101' # 중기기온예보 (서울)
API_KEY = os.environ.get('KMA_API_KEY')

def get_weather_emoji(sky, pty):
    if pty != '0':
        if pty in ['1', '4']: return "🌧️" # 비
        if pty == '2': return "🌨️" # 비/눈
        if pty == '3': return "❄️" # 눈
    else:
        if sky == '1': return "☀️" # 맑음
        if sky == '3': return "⛅" # 구름많음
        if sky == '4': return "☁️" # 흐림
    return "🌡️"

def fetch_short_term():
    """오늘~3일차 단기예보 데이터 가져오기"""
    base_date = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y%m%d')
    url = f"https://apihub.kma.go.kr/api/typ01/url/vsc_sfc_af_dtl.php?base_date={base_date}&nx={NX}&ny={NY}&authKey={API_KEY}"
    # 실제 API 허브 상세 URL 구조에 따라 파라미터는 조정될 수 있습니다.
    # 여기서는 구조적 예시를 위해 로직을 구성합니다.
    res = requests.get(url)
    return res.text # 기상청 결과 파싱 로직 필요

def generate_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Weather Calendar//KO//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', '기상청 날씨 달력')
    
    # --- [데이터 수집 및 이벤트 생성 로직] ---
    # 실제 구현시 API 응답(JSON/TEXT)을 반복문으로 돌며 이벤트를 생성합니다.
    
    # 예시 데이터 생성 (오늘부터 10일치)
    for i in range(11):
        target_date = (datetime.now(pytz.timezone('Asia/Seoul')) + timedelta(days=i)).date()
        event = Event()
        
        if i <= 2: # 단기 예보 구역
            event.add('summary', f"☀️ {i+5}° / {i+15}°")
            event.add('description', f"09:00: ☀️ 10°C\n12:00: ☀️ 14°C\n(단기예보 데이터)")
        else: # 중기 예보 구역
            event.add('summary', f"⛅ {i+4}° / {i+12}°")
            event.add('description', f"오전: 구름많음\n오후: 맑음\n(중기예보 데이터)")
            
        event.add('dtstart', target_date)
        event.add('dtend', target_date + timedelta(days=1))
        cal.add_component(event)

    with open('weather.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    generate_calendar()
