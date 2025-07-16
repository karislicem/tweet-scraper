# 🐦 Twitter Scraper

Sade ve basit Twitter tweet çekme aracı.

## 🚀 Kurulum

```bash
pip install -r requirements.txt
```

## 💻 Kullanım

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın.

## 📋 Özellikler

- ✅ **Kullanıcı Adı Girme**: Bir veya birden fazla kullanıcı adı
- ✅ **Tweet Sayısı**: Her kullanıcı için kaç tweet çekileceği
- ✅ **JSON İndirme**: Sonuçları JSON formatında indir
- ✅ **CSV İndirme**: Sonuçları CSV formatında indir
- ✅ **Canlı Progress**: İşlem ilerlemesini takip et

## 🎯 Nasıl Kullanılır

1. **Kullanıcı Adları**: `elonmusk, sundarpichai, tim_cook` gibi virgülle ayırın
2. **Tweet Sayısı**: Slider ile 1-20 arası seçin
3. **Çek**: "🚀 Tweet'leri Çek" butonuna basın
4. **İndir**: JSON veya CSV formatında indirin

## 📊 Çıktı Formatı

Her tweet için:
- `username`: Kullanıcı adı
- `text`: Tweet metni
- `timestamp`: Zaman damgası
- `scraped_at`: Çekilme zamanı

## ⚠️ Uyarılar

- Sadece halka açık tweetler çekilir
- Twitter'ın kullanım şartlarına uyun
- Çok sık kullanmayın (rate limit)

---

✨ Basit ve etkili! 