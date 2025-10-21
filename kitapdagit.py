import streamlit as st
import json
import random
import os
import pandas as pd

# --- Sabitler ---
MAX_KITAP_SAYISI = 34

# --- Veri Yükleme ve Başlangıç Ayarları (SESSION STATE KULLANIMI) ---

# Veri setini sadece bir kez, oturum başladığında başlatır.
if 'veri' not in st.session_state:
    st.session_state.veri = {
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
    # İlk kayıtları başlat
    st.session_state.veri["kayitlar"] = {ogr: [] for ogr in st.session_state.veri["ogrenciler"]}


# Veri setlerini Session State'den çekme
veri = st.session_state.veri
ogrenciler = veri["ogrenciler"]
kitaplar = veri["kitaplar"]
kayitlar = veri["kayitlar"]

# Session State kullandığımız için bu fonksiyon artık işlevsizdir
def kaydet():
    pass

# --- HATA DÜZELTMESİ İÇİN YARDIMCI FONKSİYON ---
def get_kitap_sira_no(kitap_adi):
    """
    Kitap adından ("Kitap 1", "Kitap 34" vb.) 
    sıralama için sayısal bir değer çıkarmaya çalışır.
    Formatı bozuksa veya kitap değilse 999 döndürür.
    """
    # Önce string mi diye kontrol et
    if not isinstance(kitap_adi, str):
        return 999

    # Değer "Kitap X" formatında mı diye bak
    if kitap_adi.startswith("Kitap "):
        try:
            parcalar = kitap_adi.split(' ')
            # parcalar[1]'in sayı olup olmadığını kontrol et
            if len(parcalar) > 1 and parcalar[1].isdigit():
                return int(parcalar[1])
        except (ValueError, IndexError):
            # Beklenmedik bir durum olursa (örn: "Kitap ")
            return 999
            
    # Eğer "Kitap " ile başlamıyorsa ("YOK", "TAMAM", "Türkçe Kitap" vb.)
    return 999
# --- DÜZELTME SONU ---


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
            # Doğrudan Session State listesini güncelle
            st.session_state.veri["ogrenciler"].append(yeni_ogr)
            st.session_state.veri["kayitlar"][yeni_ogr] = []
            
            st.success(f"'{yeni_ogr}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu isim zaten listede.")
    st.markdown("---")
    
# --- Kitap Yönetimi ---
elif secim == "Kitaplar":
    st.header("📘 Kitap Yönetimi")
    st.info(f"Mevcut Kitap Sayısı: {len(kitaplar)}")

    yeni_kitap = st.text_input("Yeni kitap ekle (Örn: Kitap 35):")
    if st.button("Kitap Ekle") and yeni_kitap.strip():
        if yeni_kitap not in kitaplar:
            # Doğrudan Session State listesini güncelle
            st.session_state.veri["kitaplar"].append(yeni_kitap)
            
            st.success(f"'{yeni_kitap}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu kitap zaten var.")
    st.markdown("---")

# --- Dağıtım İşlemleri (Ana Modül) ---
elif secim == "Dağıtım İşlemleri":
    st.header("📅 Haftalık Kitap Dağıtımı")

    # Kontrol: Kitap ve Öğrenci sayısı eşit olmalı
    if len(ogrenciler) != len(kitaplar) or len(ogrenciler) < 1:
        st.error(f"Öğrenci sayısı ({len(ogrenciler)}) ve Kitap sayısı ({len(kitaplar)}) eşit olmalıdır! Lütfen yönetim panelinden düzeltin.")
        st.stop()

    # Hafta Numarasını Belirleme
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
            random.shuffle(mevcut_kitaplar_havuzu) # SÜRPRİZ DAĞITIM için karıştır
            
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
            
            # Aktif öğrencileri en az kitap alandan başlat
            aktif_ogrenciler.sort(key=lambda o: len(kayitlar[o]))

            for ogr in aktif_ogrenciler:
                oncekiler = set([k for k in kayitlar[ogr] if k != "YOK" and k != "TAMAM"])
                
                # Bu öğrenciye atanabilecek, daha önce almadığı ve henüz dağıtılmamış kitapları bul
                alinabilir = [k for k in mevcut_kitaplar_havuzu if k not in oncekiler]
                
                if not alinabilir:
                    kayitlar[ogr].append("TAMAM") 
                    haftalik_dagitim_sonucu[f"TAMAM - Kitap kalmadı"] = ogr
                    continue
                
                # Rastgele birini seç
                secilen = random.choice(alinabilir)
                
                # Kayıtları güncelle
                kayitlar[ogr].append(secilen)
                haftalik_dagitim_sonucu[secilen] = ogr
                mevcut_kitaplar_havuzu.remove(secilen) # Kitabı havuzdan çıkar (Benzersizlik garantisi)

            # --- 4. Sonuçları Göster (Kitap 1'den Başlayarak Sıralı Çıktı) ---
            
            dagitim_gosterim = []
            for kitap, ogr in haftalik_dagitim_sonucu.items():
                dagitim_gosterim.append([kitap, ogr]) 
                
            # Pasif öğrencileri de ekle
            for ogr in pasif_ogrenciler:
                dagitim_gosterim.append(["YOK", ogr]) 
                
            df_sonuc = pd.DataFrame(dagitim_gosterim, columns=[f"Kitap", "Alan Öğrenci"])
            
            # --- BAŞLANGIÇ: HATA DÜZELTMESİ UYGULANDI ---
            # Kitap isimlerini "Kitap X" formatından alıp sayısal olarak sıralama için geçici sütun oluştur
            # Güvenli fonksiyon (get_kitap_sira_no) kullanıldı.
            df_sonuc['Sıra'] = df_sonuc["Kitap"].apply(get_kitap_sira_no)
            # --- SON: HATA DÜZELTMESİ UYGULANDI ---
            
            # Kitap numarasına göre sırala (Kitap 1'den başlasın)
            df_sonuc = df_sonuc.sort_values(by='Sıra', ascending=True).drop(columns=['Sıra'])
            
            st.success("✅ Dağıtım tamamlandı! Sonuçlar Kitap 1'den başlayarak sıralanmıştır.")
            st.dataframe(df_sonuc.set_index("Kitap")) 

            # Hata veren satır buradaydı. Session State ile artık güvenli olmalı.
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
    st.warning("Bu işlem, hafızadaki (Session State) tüm dağıtım kayıtlarını kalıcı olarak siler.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        sifirla_buton = st.button("🗑️ TÜM KAYITLARI SIFIRLA")
    with col2:
        onay = st.checkbox("Emin misiniz? Bu işlem geri alınamaz!")

    if sifirla_buton and onay:
        # Kayıt sözlüğünü boşaltıyoruz.
        st.session_state.veri["kayitlar"] = {ogr: [] for ogr in st.session_state.veri["ogrenciler"]}
        
        st.success("Tüm dağıtım kayıtları sıfırlandı.")
        # Programı yeniden başlat
        st.experimental_rerun()
