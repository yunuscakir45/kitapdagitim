import streamlit as st
import json
import random
import os
import pandas as pd

# --- Dosya Sabiti ve Başlangıç Ayarları ---
DATA_FILE = "kitap_dagitim_veri.json"
MAX_KITAP_SAYISI = 34 # Başlangıçta 34 öğrenci/kitap varsayımı

# --- Veri Yükleme ---
# Bu blok, uygulamanın her başlangıcında veya yeniden çalışmasında (rerun) çalışır
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            veri = json.load(f)
    except json.JSONDecodeError:
        st.error("Veri dosyası (JSON) bozuk. Lütfen dosyayı silin ve tekrar deneyin.")
        st.stop()
else:
    # Başlangıç verisi (JSON dosyası yoksa)
    veri = {
        "ogrenciler": [
            "Ahmet Yılmaz", "Ayşe Demir", "Mehmet Korkmaz", "Elif Kaya", "Mustafa Çetin",
            "Zeynep Arslan", "Ali Koç", "Fatma Aydın", "Emre Şahin", "Hatice Doğan",
            "Yusuf Kaplan", "Esra Güneş", "Murat Yıldız", "Merve Aksoy", "Burak Taş",
            "Sevgi Özkan", "Can Eren", "Kübra Polat", "Ömer Yalçın", "Cansu Tekin",
            "Hakan Er", "Derya Bozkurt", "Ece Karaca", "Hasan Tunç", "Rabia Özdemir",
            "Serkan Bulut", "Selin Yılmaz", "Gökhan Şimşek", "Melis Çakır", "İsmail Yıldırım",
            "Tuğba Kara", "Onur Demirtaş", "Büşra Çetin", "Enes Acar"
        ],
        "kitaplar": [f"Kitap {i}" for i in range(1, MAX_KITAP_SAYISI + 1)],
        "kayitlar": {}
    }
    veri["kayitlar"] = {ogr: [] for ogr in veri["ogrenciler"]}

# Veri setlerini global değişkenlere atama
ogrenciler = veri["ogrenciler"]
kitaplar = veri["kitaplar"]
kayitlar = veri["kayitlar"]

def kaydet():
    """Veriyi JSON dosyasına kaydeder."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

st.title("📚 Kitap Dağıtım Sistemi (Gelişmiş)")
st.caption("Haftalık dönüşümlü kitap takibi, öğrenci ve kitap yönetimi dahil")

# --- Yönetim Paneli (Sidebar) ---
st.sidebar.header("⚙️ Yönetim Paneli")
secim = st.sidebar.radio("Yönetim Seçeneği:", ["Dağıtım İşlemleri", "Öğrenciler", "Kitaplar"])


# --- Öğrenci Yönetimi ---
if secim == "Öğrenciler":
    st.header("👩‍🎓 Öğrenci Yönetimi")
    st.info(f"Mevcut Öğrenci Sayısı: {len(ogrenciler)}")
    
    yeni_ogr = st.text_input("Yeni öğrenci ekle:")
    if st.button("Öğrenci Ekle") and yeni_ogr.strip():
        if yeni_ogr not in ogrenciler:
            ogrenciler.append(yeni_ogr)
            kayitlar[yeni_ogr] = []
            kaydet()
            st.success(f"'{yeni_ogr}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu isim zaten listede.")
    st.markdown("---")
    # Silme/Değiştirme kısımları kod fazlalığı olmaması için basitleştirilmiştir.
    
# --- Kitap Yönetimi ---
elif secim == "Kitaplar":
    st.header("📘 Kitap Yönetimi")
    st.info(f"Mevcut Kitap Sayısı: {len(kitaplar)}")

    yeni_kitap = st.text_input("Yeni kitap ekle (Örn: Kitap 35):")
    if st.button("Kitap Ekle") and yeni_kitap.strip():
        if yeni_kitap not in kitaplar:
            kitaplar.append(yeni_kitap)
            kaydet()
            st.success(f"'{yeni_kitap}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu kitap zaten var.")
    st.markdown("---")
    # Silme/Değiştirme kısımları basitleştirilmiştir.

# --- Dağıtım İşlemleri (Ana Modül) ---
elif secim == "Dağıtım İşlemleri":
    st.header("📅 Haftalık Kitap Dağıtımı")

    # Kontrol: Kitap ve Öğrenci sayısı eşit olmalı
    if len(ogrenciler) != len(kitaplar) or len(ogrenciler) < 1:
        st.error(f"Öğrenci sayısı ({len(ogrenciler)}) ve Kitap sayısı ({len(kitaplar)}) eşit olmalıdır! Lütfen yönetim panelinden düzeltin.")
        st.stop()

    # Hafta Numarasını Belirleme (En Uzun Öğrenci Kayıt Listesine Göre)
    max_alınan = max((len(kayitlar[o]) for o in ogrenciler), default=0)
    hafta = 1 + max_alınan 
    
    # Döngü Tamamlandı Uyarısı
    if hafta > len(kitaplar):
        st.success(f"Tebrikler! {len(kitaplar)} haftalık tüm kitap döngüsü tamamlanmıştır. Yeni dönem için sıfırlama yapabilirsiniz.")
        hafta = len(kitaplar) 
        
    st.subheader(f"📖 {hafta}. Hafta Dağıtımı ({len(kitaplar)} kitap / {len(ogrenciler)} öğrenci)")

    # Kullanıcıdan Durum Girişi
    yok_ogrenciler = st.multiselect("Bu hafta gelmeyen öğrenciler (Devamsız):", ogrenciler)
    getirmeyenler = st.multiselect("Kitabını getirmeyen öğrenciler:", [o for o in ogrenciler if o not in yok_ogrenciler])
    
    # Yeni kitap almaya uygun olanlar ve pasif olanları ayırma
    aktif_ogrenciler = [o for o in ogrenciler if o not in yok_ogrenciler + getirmeyenler]
    pasif_ogrenciler = [o for o in ogrenciler if o not in aktif_ogrenciler]

    col1, col2 = st.columns(2)
    
    with col1:
        dagitim_buton = st.button("📚 Dağıtımı Yap")
    with col2:
        geri_al_buton = st.button("↩ Son Haftayı Geri Al")

    if dagitim_buton:
        if hafta > len(kitaplar):
            st.warning("Dağıtım döngüsü tamamlanmıştır.")
        else:
            # --- 1. Kitap Havuzu Hazırlığı ---
            mevcut_kitaplar_havuzu = kitaplar[:] 
            random.shuffle(mevcut_kitaplar_havuzu) # Kitapların dağıtım sırasını rastgele karıştır (SÜRPRİZ)
            
            haftalik_dagitim_sonucu = {}
            
            # --- 2. Pasif Öğrencilerin Kaydını Güncelle (BOŞLUK/YOK İŞARETİ) ---
            for ogr in pasif_ogrenciler:
                # Önceki haftalarda geri kalmışsa 'YOK' ile doldur
                while len(kayitlar[ogr]) < max_alınan:
                    kayitlar[ogr].append("YOK")

                # Bu haftaya BOŞLUK işareti koy
                kayitlar[ogr].append("YOK")
                
                if ogr in getirmeyenler:
                    st.info(f"Öğrenci **{ogr}** kitabını getirmedi. Bu hafta yeni kitap almadı.")
                else:
                    st.info(f"Öğrenci **{ogr}** devamsız. Bu hafta yeni kitap almadı.")

            # --- 3. Aktif Öğrencilere Kitap Dağıtımı (Benzersiz ve Rastgele) ---
            
            # Aktif öğrencileri en az kitap alandan başlat (Adil dağıtım önceliği)
            aktif_ogrenciler.sort(key=lambda o: len(kayitlar[o]))

            for ogr in aktif_ogrenciler:
                oncekiler = set([k for k in kayitlar[ogr] if k != "YOK"]) # Daha önce aldığı kitaplar
                
                # Bu öğrenciye atanabilecek, daha önce almadığı ve henüz dağıtılmamış kitapları bul
                alinabilir = [k for k in mevcut_kitaplar_havuzu if k not in oncekiler]
                
                if not alinabilir:
                    kayitlar[ogr].append("TAMAM") 
                    haftalik_dagitim_sonucu[f"TAMAM - Kitap kalmadı"] = ogr
                    continue
                
                # Rastgele birini seç
                secilen = random.choice(alinabilir)
                
                # Kayıtları güncelle
                haftalik_dagitim_sonucu[secilen] = ogr
                kayitlar[ogr].append(secilen)
                mevcut_kitaplar_havuzu.remove(secilen) # Kitabı havuzdan çıkar (Benzersizlik garantisi)

            # --- 4. Sonuçları Göster (Kitap 1'den Başlayarak Sıralı Çıktı) ---
            
            dagitim_gosterim = []
            for kitap, ogr in haftalik_dagitim_sonucu.items():
                dagitim_gosterim.append([kitap, ogr]) 
                
            # Pasif öğrencileri de ekle
            for ogr in pasif_ogrenciler:
                dagitim_gosterim.append(["YOK", ogr]) 
                
            df_sonuc = pd.DataFrame(dagitim_gosterim, columns=[f"Kitap", "Alan Öğrenci"])
            
            # Kitap isimlerini "Kitap X" formatından alıp sayısal olarak sıralama için geçici sütun oluştur
            df_sonuc['Sıra'] = df_sonuc["Kitap"].apply(
                lambda x: int(x.split(' ')[1]) if "Kitap" in x else 999
            )
            
            # Kitap numarasına göre sırala (Kitap 1'den başlasın)
            df_sonuc = df_sonuc.sort_values(by='Sıra', ascending=True).drop(columns=['Sıra'])
            
            st.success("✅ Dağıtım tamamlandı! Sonuçlar Kitap 1'den başlayarak sıralanmıştır.")
            st.dataframe(df_sonuc.set_index("Kitap")) 

            kaydet()
            st.experimental_rerun()
            
    if geri_al_buton:
        # Geri alma işlemini (son haftanın kaydını silme)
        silinecek_hafta = max_alınan
        
        if silinecek_hafta <= 0:
            st.warning("Daha geriye alınacak dağıtım yok.")
        else:
            for ogr in ogrenciler:
                if len(kayitlar[ogr]) == silinecek_hafta:
                    kayitlar[ogr].pop() # Son kaydı sil
            kaydet()
            st.warning(f"↩ {silinecek_hafta}. Haftadaki dağıtım geri alındı.")
            st.experimental_rerun()

    # --- Geçmiş Görüntüleme ---
    if st.button("📜 Tüm Geçmişi Görüntüle"):
        st.header("📘 Geçmiş Kitaplar")
        max_len = max((len(kayitlar[o]) for o in ogrenciler), default=0)
        
        gecmis_data = {}
        for ogr in ogrenciler:
            temp_list = kayitlar[ogr] + ["-"] * (max_len - len(kayitlar[ogr]))
            gecmis_data[ogr] = temp_list
            
        gecmis = pd.DataFrame(gecmis_data).transpose()
        gecmis.columns = [f"{i}. Hafta" for i in range(1, max_len + 1)]
        st.dataframe(gecmis)
        
    st.markdown("---")
    st.subheader("⚠️ Tüm Verileri Sıfırla")
    st.warning("Bu işlem, tüm dağıtım kayıtlarını, öğrenci/kitap geçmişini ve veri dosyasını kalıcı olarak siler.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        sifirla_buton = st.button("🗑️ TÜM VERİYİ VE DOSYAYI SIFIRLA")
    with col2:
        onay = st.checkbox("Emin misiniz? Bu işlem geri alınamaz!")

    if sifirla_buton and onay:
        # JSON dosyasını silme işlemi
        if os.path.exists(DATA_FILE):
            try:
                os.remove(DATA_FILE)
                st.success(f"Tüm dağıtım kayıtları ve veri dosyası ('{DATA_FILE}') başarıyla silindi.")
            except Exception as e:
                st.error(f"Dosya silinirken bir hata oluştu: {e}")
                
        else:
            st.warning(f"Veri dosyası ('{DATA_FILE}') zaten bulunamadı.")
            
        # Programı yeniden başlat (veri sıfırlanmış olarak tekrar yüklensin)
        st.experimental_rerun()
