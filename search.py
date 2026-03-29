import yt_dlp
import os

# NOT: Artık fiziksel indirme yapmadığımız için DOWNLOAD_DIR ve os.remove işlemleri boşa çıkacak.
# Ama istersen klasör kontrolü kalsın, zarar gelmez.

def search_youtube(query):
    # 🚀 ÖNCELİK JIOSAAVN: Resmi ve kaliteli kayıt için Saavn en başa alındı.
    # 🔍 SCSEARCH5: İlk 5 sonucu getiriyoruz ki içinden en iyisini seçelim.
    engines = [
        {"name": "JioSaavn", "code": "jssearch5:"},
        {"name": "SoundCloud", "code": "scsearch5:"},
        {"name": "Bandcamp", "code": "bcsearch1:"}
    ]
    
    for engine in engines:
        search_query = f"{engine['code']}{query}"
        
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "noplaylist": True,
            "extract_flat": False,
            # ⚡ KRİTİK DEĞİŞİKLİK: İndirme kapalı, sadece linki alıyoruz.
            "skip_download": True, 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"🔍 [{engine['name']}] İnceleniyor: {query}")
                # download=False yaparak sadece metadata çekiyoruz (Saniyelik işlem)
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info and len(info['entries']) > 0:
                    # --- AKILLI FİLTRELEME BAŞLIYOR ---
                    best_entry = None
                    for entry in info['entries']:
                        duration_s = entry.get('duration', 0)
                        title = entry.get('title', '').lower()

                        # 🛑 Shorts/Snippet Engeli: 60 saniyeden kısa şarkıları pas geç
                        if duration_s < 60:
                            continue
                        
                        # 🛑 Kötü Kelime Engeli: Başlıkta bunlar varsa pas geç
                        blacklist = ["shorts", "teaser", "snippet", "fragman"]
                        if any(word in title for word in blacklist):
                            continue
                        
                        best_entry = entry
                        break # Kriterlere uyan ilk uzun şarkıyı seç ve çık
                    
                    if not best_entry:
                        best_entry = info['entries'][0] # Filtreye uyan yoksa ilkine dön
                else:
                    best_entry = info

                # SÜRE FORMATLAMA
                duration_raw = best_entry.get('duration')
                if duration_raw:
                    mins, secs = divmod(int(duration_raw), 60)
                    duration = f"{mins:02d}:{secs:02d}"
                else:
                    duration = "Bilinmiyor"

                # 💡 ÖNEMLİ: 'file_path' anahtarını bozmadım ama içine artık 'url' (online link) koyuyorum.
                # player.py bu sayede hata vermeden linki oynatacak.
                return {
                    "title": best_entry.get('title', 'Bilinmeyen Parça'),
                    "webpage_url": best_entry.get('webpage_url', ''),
                    "file_path": best_entry.get('url'), # ARTIK LİNK, SUNUCUDA YER KAPLAMAZ
                    "thumbnail": best_entry.get('thumbnail', ''),
                    "duration": duration,
                    "source": engine['name']
                }
            except Exception as e:
                print(f"⚠️ {engine['name']} hatası: {str(e)[:40]}...")
                continue

    raise Exception("❌ Aradığın kriterlerde kaliteli bir şarkı bulunamadı.")
