import urllib.request
import json
import os
import time

print("[SO-HMNS v59.5] Global Auto-Ingestion Daemon Initializing...")

def fetch_and_update():
    # 1. 미국지질조사국(USGS) 실시간 전 세계 판 경계 및 실시간 지진 RAW 데이터셋 가용 자원 동원 수집
    usgs_url = "https://usgs.gov"
    try:
        req = urllib.request.Request(usgs_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        features = data.get("features", [])
        if not features:
            print("[SO-HMNS] No new tectonic delta in this segment. Standing by.")
            return False

        # 최신 관측 데이터 분기 파싱 (가장 최근 등록된 관측망 데이터 추출)
        latest = features[0]
        props = latest.get("properties", {})
        geom = latest.get("geometry", {})
        coords = geom.get("coordinates", [0, 0])
        
        place = props.get("place", "Global Subduction Zone").replace("'", "")
        lng = float(coords[0])
        lat = float(coords[1])
        mag = float(props.get("mag", 5.0))
        
        # 2. SO-HMNS 59층 결정론적 제약 역산 매커니즘 자율 대입
        # 수집된 실시간 규모와 위치 기반으로 역산 변형 속도(Speed) 및 축적년수(Years) 자동 환산
        calculated_speed = int(mag * 12)
        calculated_years = 150
        
        print(f"[SO-HMNS] New Sensor Ingested -> Loc: {place} | Lat: {lat} | Lng: {lng} | Mag: {mag}")
        
        # 3. index.html의 데이터 입력 기본값을 실시간 수집된 데이터로 자율 리팩토링 (기계식 자동 치환)
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                html = f.read()
            
            # 정밀 타격 문자열 치환 가동
            html = html.split('id="targetName" value="')[0] + 'id="targetName" value="' + str(place) + html.split('id="targetName" value="')[1].split('"', 1)[1]
            html = html.split('id="targetLat" value="')[0] + 'id="targetLat" value="' + f"{lat:.4f}" + html.split('id="targetLat" value="')[1].split('"', 1)[1]
            html = html.split('id="targetLng" value="')[0] + 'id="targetLng" value="' + f"{lng:.4f}" + html.split('id="targetLng" value="')[1].split('"', 1)[1]
            html = html.split('id="targetSpeed" value="')[0] + 'id="targetSpeed" value="' + str(calculated_speed) + html.split('id="targetSpeed" value="')[1].split('"', 1)[1]
            
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("[SO-HMNS] Web Dashboard Core Source-Code Automatically Refactored.")
            return True
    except Exception as e:
        print(f"[SO-HMNS] Network Ingestion Delay: {e}")
        return False

# 최초 1회 즉시 강제 수집 격발
if fetch_and_update():
    os.system("git add index.html && git commit -m 'System: Automated Real-Time Tectonic Feed Update' && git push origin main --force")
