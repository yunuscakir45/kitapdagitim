import streamlit as st
import json
import random
import os
import pandas as pd

# --- Sabitler ---
DATA_FILE = "kitap_dagitim_veri.json"
MAX_KITAP_SAYISI = 34

# --- Veriyi Yükle / Başlat ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        veri = json.load(f)
else:
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

# --- Yardımcı Fonksiyonlar ---
def kaydet():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

def get_kitap_sira_no(kitap_adi):
    if not isinstance(kitap_adi, str):
        return 999
    if kitap_adi.startswith("Kitap "):
        try:
            parcalar = kitap_adi.split(' ')
            if len(parcalar) > 1 and parcalar[1].isdigit():
                return int(parcalar[1])
        except (ValueError, IndexError):
            return 999
    return 999

st.title("📚 Kitap Dağıtım Sistemi (Gelişmiş)")
st.caption("Haftalık dönüşümlü kitap takibi, öğrenci ve kitap yönetimi dahil")

# --- Yönetim Paneli ---
st.sidebar.header("⚙️ Yönetim Paneli")
secim = st.sidebar.radio("Yönetim Seçeneği:", ["Dağıtım İşlemleri", "Öğrenciler", "Kitaplar"])

# --- Öğrenci Yönetimi ---
if secim == "Öğrenciler":
    st.header("👩‍🎓 Öğrenci Yönetimi")
    st.info(f"Mevcut Öğrenci Sayısı: {len(veri['ogrenciler'])}")

    yeni_ogr = st.text_input("Yeni öğrenci ekle:")
    if st.button("Öğrenci Ekle") and yeni_ogr.strip():
        if yeni_ogr not in veri["ogrenciler"]:
            veri["ogrenciler"].append(yeni_ogr)
            veri["kayitlar"][yeni_ogr] = []
            kaydet()
            st.success(f"'{yeni_ogr}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu isim zaten listede.")

    silinecek = st.selectbox("Silinecek öğrenci seç:", [""] + veri["ogrenciler"])
    if st.button("Öğrenciyi Sil") and silinecek:
        del veri["kayitlar"][silinecek]
        veri["ogrenciler"].remove(silinecek)
        kaydet()
        st.warning(f"'{silinecek}' silindi.")
        st.experimental_rerun()

# --- Kitap Yönetimi ---
elif secim == "Kitaplar":
    st.header("📘 Kitap Yönetimi")
    st.info(f"Mevcut Kitap Sayısı: {len(veri['kitaplar'])}")

    yeni_kitap = st.text_input("Yeni kitap ekle (Örn: Kitap 35):")
    if st.button("Kitap Ekle") and yeni_kitap.strip():
        if yeni_kitap not in veri["kitaplar"]:
            veri["kitaplar"].append(yeni_kitap)
            kaydet()
            st.success(f"'{yeni_kitap}' eklendi.")
            st.experimental_rerun()
        else:
            st.warning("Bu kitap zaten var.")

    sil_kitap = st.selectbox("Silinecek kitap:", [""] + veri["kitaplar"])
    if st.button("Kitabı Sil") and sil_kitap:
        veri["kitaplar"].remove(sil_kitap)
        kaydet()
        st.warning(f"'{sil_kitap}' silindi.")
        st.experimental_rerun()

# --- Dağıtım İşlemleri ---
elif secim == "Dağıtım İşlemleri":
    st.header("📅 Haftalık Kitap Dağıtımı")

    ogrenciler = veri["ogrenciler"]
    kitaplar = veri["kitaplar"]
    kayitlar = veri["kayitlar"]

    if len(ogrenciler) != len(kitaplar) or len(ogrenciler) < 1:
        st.error(f"Öğrenci sayısı ({len(ogrenciler)}) ve kitap sayısı ({len(kitaplar)}) eşit olmalıdır!")
        st.stop()

    max_hafta = max((len(kayitlar[o]) for o in ogrenciler), default=0)
    hafta = max_hafta + 1

    st.subheader(f"📖 {hafta}. Hafta Dağıtımı")

    # --- Gelmeyen öğrenciler seçimi ---
    yok_ogrenciler = st.multiselect("Bu hafta kitabını getirmeyen (veya gelmeyen) öğrenciler:", ogrenciler)
    aktif_ogrenciler = [o for o in ogrenciler if o not in yok_ogrenciler]

    # --- Dağıtım Öncesi Denetim ---
    st.markdown("### 🔍 Dağıtım Öncesi Kontrol")
    sorun_var = False
    for ogr in aktif_ogrenciler:
        oncekiler = set([k for k in kayitlar[ogr] if k != "YOK"])
        mevcut_kitaplar = [kayitlar[o][-1] for o in aktif_ogrenciler if kayitlar[o]]  # sınıfta bulunan kitaplar
        mevcut_kitaplar = [k for k in mevcut_kitaplar if k not in oncekiler and k != "YOK"]
        if not mevcut_kitaplar:
            # Eğer öğrencinin okuyabileceği kitap yoksa uyarı ver
            okunmamis = [kayitlar[o][-1] for o in yok_ogrenciler if kayitlar[o]]
            if okunmamis:
                st.warning(f"⚠️ {ogr} öğrencisinin okuyabileceği kitap sınıfta yok. Okumadığı kitap şu öğrencilerde: {', '.join(yok_ogrenciler)}")
            else:
                st.error(f"⚠️ {ogr} öğrencisinin sınıfta okuyabileceği kitap kalmadı!")
            sorun_var = True

    if sorun_var:
        st.info("Dağıtıma devam etmeden önce yukarıdaki durumları kontrol edin.")

    col1, col2 = st.columns(2)
    with col1:
        dagitim = st.button("📚 Dağıtımı Yap")
    with col2:
        geri_al = st.button("↩ Son Haftayı Geri Al")

    if dagitim:
        haftalik_dagitim_sonucu = {}

        # Pasif öğrencilerin kitapları bu hafta dağıtıma katılmaz
        mevcut_havuz = []
        for ogr in aktif_ogrenciler:
            if kayitlar[ogr]:
                mevcut_havuz.append(kayitlar[ogr][-1])
        random.shuffle(mevcut_havuz)

        for ogr in yok_ogrenciler:
            kayitlar[ogr].append("YOK")

        for ogr in aktif_ogrenciler:
            oncekiler = set([k for k in kayitlar[ogr] if k != "YOK"])
            alinabilir = [k for k in mevcut_havuz if k not in oncekiler]
            if not alinabilir:
                kayitlar[ogr].append("YOK")
                haftalik_dagitim_sonucu["YOK"] = ogr
            else:
                secilen = random.choice(alinabilir)
                kayitlar[ogr].append(secilen)
                mevcut_havuz.remove(secilen)
                haftalik_dagitim_sonucu[secilen] = ogr

        kaydet()
        st.success("✅ Dağıtım tamamlandı!")

        df = pd.DataFrame(list(haftalik_dagitim_sonucu.items()), columns=["Kitap", "Alan Öğrenci"])
        df['Sıra'] = df["Kitap"].apply(get_kitap_sira_no)
        df = df.sort_values(by='Sıra', ascending=True).drop(columns=['Sıra'])
        st.dataframe(df.set_index("Kitap"))

    if geri_al:
        if max_hafta <= 0:
            st.warning("Daha geriye alınacak hafta yok.")
        else:
            for ogr in ogrenciler:
                if len(kayitlar[ogr]) == max_hafta:
                    kayitlar[ogr].pop()
            kaydet()
            st.warning(f"{max_hafta}. hafta geri alındı.")
            st.experimental_rerun()

    # --- Geçmiş Tablo Görünümü ---
    if st.button("📜 Tüm Geçmişi Görüntüle"):
        max_len = max((len(kayitlar[o]) for o in ogrenciler), default=0)
        gecmis_data = {}
        for ogr in ogrenciler:
            temp = kayitlar[ogr] + ["-"] * (max_len - len(kayitlar[ogr]))
            gecmis_data[ogr] = temp
        df_gecmis = pd.DataFrame(gecmis_data).transpose()
        df_gecmis.columns = [f"{i}. Hafta" for i in range(1, max_len + 1)]
        st.dataframe(df_gecmis)

    # --- Sıfırlama ---
    st.markdown("---")
    st.subheader("⚠️ Tüm Verileri Sıfırla")
    onay = st.checkbox("Emin misiniz? Bu işlem geri alınamaz!")
    if st.button("🗑️ TÜM KAYITLARI SIFIRLA") and onay:
        veri["kayitlar"] = {ogr: [] for ogr in veri["ogrenciler"]}
        kaydet()
        st.success("Tüm kayıtlar sıfırlandı.")
        st.experimental_rerun()
