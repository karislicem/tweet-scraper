import streamlit as st
import pandas as pd
import json
import time
import re
import html
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Sayfa ayarları
st.set_page_config(
    page_title="Twitter Scraper",
    page_icon="🐦",
    layout="wide"
)

def create_driver():
    """Chrome driver oluştur - Streamlit Cloud uyumlu"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-in-process-stack-traces')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--output=/dev/null')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Streamlit Cloud için Chrome driver yolu
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        # Eğer Chrome driver yüklenemezse, sistem yolunu dene
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_latest_tweets(username, count=10):
    """Son tweet'leri çek"""
    driver = create_driver()
    tweets = []
    
    try:
        # Sadece ana sayfa - son tweet'ler için
        driver.get(f"https://x.com/{username}")
        time.sleep(5)
        
        # Minimal scroll - sadece en üstteki tweet'leri almak için
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(3)
        
        # Tweet'leri bul
        tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        
        if not tweet_elements:
            st.error(f"Tweet bulunamadı: {username}")
            return []
        
        # Son 30 gün sınırı
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for tweet in tweet_elements[:count*3]:  # Daha fazla kontrol et
            try:
                # Tweet metni - Türkçe karakterler ve özel simgeler için optimize edilmiş
                text = ""
                try:
                    text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    # innerHTML kullanarak daha doğru metin al
                    text = text_element.get_attribute('innerHTML')
                    if text:
                        # HTML tag'larını temizle
                        text = re.sub(r'<[^>]+>', '', text)
                        # HTML entity'leri düzelt
                        text = html.unescape(text)
                        # Ekstra temizlik
                        text = text.replace('&amp;', '&')
                        text = text.replace('&lt;', '<')
                        text = text.replace('&gt;', '>')
                        text = text.replace('&quot;', '"')
                        text = text.replace('&#39;', "'")
                        # Boşlukları düzelt
                        text = ' '.join(text.split())
                    else:
                        text = text_element.text
                except:
                    try:
                        # Fallback: genel tweet text'i
                        text = tweet.text[:200] if tweet.text else "Tweet metni alınamadı"
                    except:
                        text = "Tweet metni alınamadı"
                
                # Zaman
                timestamp = ""
                try:
                    time_element = tweet.find_element(By.CSS_SELECTOR, 'time')
                    timestamp = time_element.get_attribute('datetime')
                except:
                    timestamp = datetime.now().isoformat()
                
                # Tarih kontrol et
                if timestamp:
                    try:
                        tweet_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if tweet_date < cutoff_date:
                            continue
                    except:
                        pass
                
                if text and text != "Tweet metni alınamadı":
                    tweets.append({
                        'username': username,
                        'text': text,
                        'timestamp': timestamp,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    if len(tweets) >= count:
                        break
                        
            except Exception as e:
                continue
                
    except Exception as e:
        st.error(f"Hata: {username} - {str(e)}")
        
    finally:
        driver.quit()
    
    return tweets

def main():
    st.title("🐦 Twitter Scraper")
    st.write("Son tweet'leri çekin (son 30 gün)")
    
    # Kullanıcı adı girme
    st.subheader("👤 Kullanıcılar")
    usernames_input = st.text_input(
        "Kullanıcı adları (virgülle ayırın):",
        value="elonmusk",
        help="Örnek: elonmusk, sundarpichai"
    )
    
    # Tweet sayısı
    st.subheader("📊 Ayarlar")
    tweet_count = st.slider("Her kullanıcı için tweet sayısı:", 1, 10, 3)
    
    # Tweet çekme butonu
    if st.button("🚀 Son Tweet'leri Çek", type="primary"):
        if not usernames_input:
            st.error("Lütfen kullanıcı adı girin!")
            return
        
        usernames = [u.strip().replace('@', '') for u in usernames_input.split(',') if u.strip()]
        
        all_tweets = []
        progress_bar = st.progress(0)
        
        for i, username in enumerate(usernames):
            st.write(f"📥 {username} son tweet'leri çekiliyor...")
            tweets = get_latest_tweets(username, tweet_count)
            all_tweets.extend(tweets)
            
            progress_bar.progress((i + 1) / len(usernames))
        
        progress_bar.empty()
        
        if all_tweets:
            # Tarihe göre sırala (en yeni önce)
            all_tweets.sort(key=lambda x: x['timestamp'], reverse=True)
            
            st.success(f"✅ {len(all_tweets)} son tweet çekildi!")
            
            # Sonuçları göster
            st.subheader("📋 Son Tweet'ler")
            
            for i, tweet in enumerate(all_tweets, 1):
                with st.expander(f"Tweet {i} - @{tweet['username']} - {tweet['timestamp'][:10]}"):
                    st.write(f"**Metin:** {tweet['text']}")
                    st.write(f"**Zaman:** {tweet['timestamp']}")
            
            # İndirme seçenekleri
            st.subheader("💾 İndir")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON indirme
                json_data = json.dumps(all_tweets, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📄 JSON İndir",
                    data=json_data,
                    file_name=f"latest_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV indirme
                df = pd.DataFrame(all_tweets)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📊 CSV İndir",
                    data=csv_data,
                    file_name=f"latest_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.error("❌ Hiç tweet çekilemedi!")

if __name__ == "__main__":
    main() 