import streamlit as st
import json
import random
import os
import pandas as pd

# --- Dosya Sabiti ---
DATA_FILE = "kitap_dagitim_veri.json"
MAX_KITAP_SAYISI = 34 # Başlangıçta 34 öğrenci/kitap varsayımı

# --- Veri Yükleme ve Başlangıç Ayarları ---
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            veri = json.load(f)
    except json.JSONDecodeError:
        st.error("Veri dosyası (JSON) bozuk. Lütfen dosyayı silin ve tekrar deneyin.")
        st.stop()
else:
    # Başlangıç verisi
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

ogrenciler = veri["ogrenciler"]
kitaplar = veri["kitaplar"]
kayitlar = veri["kayitlar"]

def kaydet():
    """Veriyi JSON dosyasına kaydeder."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

st.title("📚 Kitap Dağıtım Sistemi (Gelişmiş)")
st.caption("Haftalık dönüşümlü kitap takibi, öğrenci ve kitap yönetimi dahil")

# --- Öğrenci ve Kitap Yönetimi (Sidebar) ---
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
    
    # Silme ve Değiştirme kısımları kod fazlalığı olmaması için çıkarılmıştır.
    # Kullanıcı isterse bu kısımları yeniden ekleyebilir.

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
    
    # Silme ve Değiştirme kısımları kod fazlalığı olmaması için çıkarılmıştır.

# --- Dağıtım İşlemleri ---
elif secim == "Dağıtım İşlemleri":
    st.header("📅 Haftalık Kitap Dağıtımı")

    # Kontrol: Kitap ve Öğrenci sayısı eşit olmalı
    if len(ogrenciler) != len(kitaplar) or len(ogrenciler) < 1:
        st.error(f"Öğrenci sayısı ({len(ogrenciler)}) ve Kitap sayısı ({len(kitaplar)}) eşit olmalıdır!")
        st.stop()

    # Kontrol: Bir öğrencinin aldığı en fazla kitap sayısını bul
    max_alınan = max((len(kayitlar[o]) for o in ogrenciler), default=0)
    
    # Hafta numarasını tüm öğrencilerin aldığı maksimum kitap sayısına göre belirle (Doğru Hafta Takibi)
    hafta = 1 + max_alınan 
    
    # Döngü Bitti mi?
    if hafta > len(kitaplar):
        st.success(f"Tebrikler! {len(kitaplar)} haftalık tüm kitap döngüsü tamamlanmıştır.")
        hafta = len(kitaplar) # Son hafta gösterimi için
        
    st.subheader(f"📖 {hafta}. Hafta Dağıtımı ({len(kitaplar)} kitap / {len(ogrenciler)} öğrenci)")

    # Kullanıcıdan Durum Girişi
    yok_ogrenciler = st.multiselect("Bu hafta gelmeyen öğrenciler (Devamsız):", ogrenciler)
    getirmeyenler = st.multiselect("Kitabını getirmeyen öğrenciler:", [o for o in ogrenciler if o not in yok_ogrenciler])
    
    # Yeni kitap almaya uygun olanlar
    aktif_ogrenciler = [o for o in ogrenciler if o not in yok_ogrenciler + getirmeyenler]
    
    # Yeni kitap alamayacak olanlar (Boşluk/YOK işareti alacaklar)
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
            # --- 1. Kitap Havuzu ve Ön Hazırlık ---
            mevcut_kitaplar_havuzu = kitaplar[:] 
            random.shuffle(mevcut_kitaplar_havuzu) # Kitapların dağıtım sırasını karıştır
            
            haftalik_dagitim_sonucu = {}
            
            # --- 2. Pasif Öğrencilerin Kaydını Güncelle (BOŞLUK/YOK İŞARETİ) ---
            for ogr in pasif_ogrenciler:
                # Kayıtlar geride kaldıysa, o haftaya kadar 'YOK' ekle
                while len(kayitlar[ogr]) < max_alınan:
                    kayitlar[ogr].append("YOK")

                # Bu haftaya BOŞLUK işareti koy
                kayitlar[ogr].append("YOK")
                
                if ogr in getirmeyenler:
                    st.info(f"Öğrenci **{ogr}** kitabını getirmedi. Bu hafta yeni kitap almadı.")
                else:
                    st.info(f"Öğrenci **{ogr}** devamsız. Bu hafta yeni kitap almadı.")

            # --- 3. Aktif Öğrencilere Kitap Dağıtımı (Benzersiz ve Rastgele) ---
            
            # Aktif öğrencileri en az kitap alandan başlat
            aktif_ogrenciler.sort(key=lambda o: len(kayitlar[o]))

            for ogr in aktif_ogrenciler:
                oncekiler = set([k for k in kayitlar[ogr] if k != "YOK"]) # Daha önce aldığı kitaplar
                
                # Bu öğrenciye atanabilecek, daha önce almadığı ve henüz dağıtılmamış kitapları bul
                alinabilir = [k for k in mevcut_kitaplar_havuzu if k not in oncekiler]
                
                if not alinabilir:
                    # Tüm kitapları okumuş ve alabileceği kitap kalmamış
                    kayitlar[ogr].append("TAMAM") 
                    haftalik_dagitim_sonucu[f"TAMAM - Kitap kalmadı"] = ogr
                    continue
                
                # Rastgele birini seç (SÜRPRİZLİ DAĞITIM)
                secilen = random.choice(alinabilir)
                
                # Seçimi kaydet
                haftalik_dagitim_sonucu[secilen] = ogr
                kayitlar[ogr].append(secilen)
                mevcut_kitaplar_havuzu.remove(secilen) # Kitabı havuzdan çıkar (Bu hafta bir daha dağıtılamaz)

            # --- 4. Sonuçları Göster ve Kaydet (Kitap 1'den Başlayarak Sıralı Görüntü) ---
            
            dagitim_gosterim = []
            for kitap, ogr in haftalik_dagitim_sonucu.items():
                dagitim_gosterim.append([kitap, ogr]) # Kitap, Öğrenci sırasıyla ekle
                
            # Pasif öğrencileri de ekle
            for ogr in pasif_ogrenciler:
                dagitim_gosterim.append(["YOK", ogr]) 
                
            df_sonuc = pd.DataFrame(dagitim_gosterim, columns=[f"{hafta}. Hafta Kitabı", "Alan Öğrenci"])
            
            # Kitap isimlerini "Kitap X" formatından alıp sayısal olarak sıralama için geçici sütun oluştur
            df_sonuc['Sıra'] = df_sonuc[f"{hafta}. Hafta Kitabı"].apply(
                lambda x: int(x.split(' ')[1]) if "Kitap" in x else 999
            )
            
            # Kitap numarasına göre sırala (Kitap 1'den başlasın)
            df_sonuc = df_sonuc.sort_values(by='Sıra', ascending=True).drop(columns=['Sıra'])
            
            # Sütun başlıklarını sadeleştir ve tabloyu göster
            df_sonuc.columns = ["Kitap", "Alan Öğrenci"]
            
            st.success("✅ Dağıtım tamamlandı! Sonuçlar Kitap 1'den başlayarak sıralanmıştır.")
            st.dataframe(df_sonuc.set_index("Kitap")) 

            kaydet()
            st.experimental_rerun()
            
    if geri_al_buton:
        # Geri alma işlemini tüm öğrencilerin son kaydını silerek yap
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
    col1, col2 = st.columns([1, 2])
    with col1:
        sifirla_buton = st.button("🗑️ TÜM VERİYİ SIFIRLA")
    with col2:
        onay = st.checkbox("Emin misiniz? Öğrenci ve kitap geçmişi silinir!")

    if sifirla_buton and onay:
        veri["kayitlar"] = {ogr: [] for ogr in ogrenciler}
        kaydet()
        st.success("Tüm dağıtım kayıtları sıfırlandı.")
        st.experimental_rerun()
