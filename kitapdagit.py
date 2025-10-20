import streamlit as st
import json
import random
import os

DATA_FILE = "kitap_dagitim_veri.json"

# --- Veriyi yükle ---
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
        "kitaplar": [f"Kitap {i}" for i in range(1, 35)],
        "kayitlar": {}
    }
    veri["kayitlar"] = {ogr: [] for ogr in veri["ogrenciler"]}

ogrenciler = veri["ogrenciler"]
kitaplar = veri["kitaplar"]
kayitlar = veri["kayitlar"]

# --- Yardımcı Fonksiyonlar ---
def kaydet():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

st.title("📚 Kitap Dağıtım Sistemi (Gelişmiş)")
st.caption("Haftalık dönüşümlü kitap takibi, öğrenci ve kitap yönetimi dahil")

# --- Öğrenci ve Kitap Yönetimi ---
st.sidebar.header("⚙️ Yönetim Paneli")

secim = st.sidebar.radio("Yönetim Seçeneği:", ["Öğrenciler", "Kitaplar", "Dağıtım İşlemleri"])

if secim == "Öğrenciler":
    st.sidebar.subheader("👩‍🎓 Öğrenci Yönetimi")
    yeni_ogr = st.sidebar.text_input("Yeni öğrenci ekle:")
    if st.sidebar.button("Ekle") and yeni_ogr.strip():
        if yeni_ogr not in ogrenciler:
            ogrenciler.append(yeni_ogr)
            kayitlar[yeni_ogr] = []
            kaydet()
            st.sidebar.success(f"{yeni_ogr} eklendi.")
            st.experimental_rerun()
        else:
            st.sidebar.warning("Bu isim zaten listede.")

    silinecek = st.sidebar.selectbox("Silinecek öğrenci:", ["(Seç)"] + ogrenciler)
    if silinecek != "(Seç)" and st.sidebar.button("Sil"):
        ogrenciler.remove(silinecek)
        kayitlar.pop(silinecek, None)
        kaydet()
        st.sidebar.success(f"{silinecek} silindi.")
        st.experimental_rerun()

    degistirilecek = st.sidebar.selectbox("İsmini değiştir:", ["(Seç)"] + ogrenciler)
    yeni_isim = st.sidebar.text_input("Yeni isim:")
    if st.sidebar.button("Değiştir") and degistirilecek != "(Seç)" and yeni_isim.strip():
        kayitlar[yeni_isim] = kayitlar.pop(degistirilecek)
        ogrenciler[ogrenciler.index(degistirilecek)] = yeni_isim
        kaydet()
        st.sidebar.success(f"{degistirilecek} → {yeni_isim}")
        st.experimental_rerun()

elif secim == "Kitaplar":
    st.sidebar.subheader("📘 Kitap Yönetimi")
    yeni_kitap = st.sidebar.text_input("Yeni kitap ekle:")
    if st.sidebar.button("Kitap Ekle") and yeni_kitap.strip():
        if yeni_kitap not in kitaplar:
            kitaplar.append(yeni_kitap)
            kaydet()
            st.sidebar.success(f"{yeni_kitap} eklendi.")
            st.experimental_rerun()
        else:
            st.sidebar.warning("Bu kitap zaten var.")

    sil_kitap = st.sidebar.selectbox("Silinecek kitap:", ["(Seç)"] + kitaplar)
    if sil_kitap != "(Seç)" and st.sidebar.button("Kitap Sil"):
        kitaplar.remove(sil_kitap)
        kaydet()
        st.sidebar.success(f"{sil_kitap} silindi.")
        st.experimental_rerun()

    degistir_kitap = st.sidebar.selectbox("İsim değiştir:", ["(Seç)"] + kitaplar)
    yeni_ad = st.sidebar.text_input("Yeni kitap adı:")
    if st.sidebar.button("Adı Değiştir") and degistir_kitap != "(Seç)" and yeni_ad.strip():
        kitaplar[kitaplar.index(degistir_kitap)] = yeni_ad
        kaydet()
        st.sidebar.success(f"{degistir_kitap} → {yeni_ad}")
        st.experimental_rerun()

elif secim == "Dağıtım İşlemleri":
    st.header("📅 Haftalık Kitap Dağıtımı")

    yok_ogrenciler = st.multiselect("Bu hafta gelmeyen öğrenciler:", ogrenciler)
    getirmeyenler = st.multiselect("Kitabını getirmeyen öğrenciler:", [o for o in ogrenciler if o not in yok_ogrenciler])

    aktif_ogrenciler = [o for o in ogrenciler if o not in yok_ogrenciler + getirmeyenler]

    max_hafta = len(ogrenciler)
    hafta = min(max(len(kayitlar[o]) for o in aktif_ogrenciler) + 1, max_hafta)

    st.subheader(f"📖 {hafta}. Hafta Dağıtımı ({len(kitaplar)} kitap / {len(ogrenciler)} öğrenci)")

    col1, col2 = st.columns(2)
    haftalik_dagitim = {}

    with col1:
        dagitim_buton = st.button("📚 Dağıtımı Yap")

    with col2:
        geri_al_buton = st.button("↩ Geri Al")

    if dagitim_buton:
        mevcut_kitaplar = kitaplar[:]
        random.shuffle(mevcut_kitaplar)

        for ogr in aktif_ogrenciler:
            oncekiler = kayitlar[ogr]
            alinabilir = [k for k in mevcut_kitaplar if k not in oncekiler]
            if not alinabilir:
                continue
            secilen = random.choice(alinabilir)
            haftalik_dagitim[secilen] = ogr
            kayitlar[ogr].append(secilen)
            mevcut_kitaplar.remove(secilen)

        haftalik_dagitim = dict(sorted(haftalik_dagitim.items()))

        kaydet()
        st.success("✅ Dağıtım tamamlandı!")
        st.table(haftalik_dagitim.items())

    if geri_al_buton:
        for ogr in aktif_ogrenciler:
            if kayitlar[ogr]:
                kayitlar[ogr].pop()
        kaydet()
        st.warning("↩ Bu haftaki dağıtım geri alındı.")
        st.experimental_rerun()

    if st.button("📜 Geçmişi Görüntüle"):
        st.header("📘 Geçmiş Kitaplar")
        for ogr, okunan in kayitlar.items():
            st.write(f"**{ogr}** → {', '.join(okunan) if okunan else 'Henüz kitap almadı.'}")

    st.markdown("---")
    st.subheader("⚠️ Tüm Verileri Sıfırla")
    col1, col2 = st.columns([1, 2])
    with col1:
        sifirla_buton = st.button("🗑️ Sıfırla")
    with col2:
        onay = st.checkbox("Emin misin? Bu işlem geri alınamaz!")

    if sifirla_buton and onay:
        veri["kayitlar"] = {ogr: [] for ogr in ogrenciler}
        kaydet()
        st.experimental_rerun()
