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
    st.info(f"Mevcut Kitap Sayısı: {l
