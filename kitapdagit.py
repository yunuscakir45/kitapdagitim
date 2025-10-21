import streamlit as st
import json
import random
import os

DATA_FILE = "kitap_dagitim_veri.json"

# ------------------------------
# --- Başlangıç verileri ---
# ------------------------------
varsayilan_ogrenciler = [
    "Ahmet", "Ayşe", "Mehmet", "Elif", "Ali", "Zeynep", "Hasan", "Fatma"
]

varsayilan_kitaplar = [
    "Küçük Prens", "Martı", "Simyacı", "Sefiller",
    "Suç ve Ceza", "Şeker Portakalı", "Beyaz Diş", "Pal Sokağı Çocukları"
]

# ------------------------------
# --- Veri yükleme / kaydetme ---
# ------------------------------
def veriyi_yukle():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        veri = {
            "ogrenciler": varsayilan_ogrenciler,
            "kitaplar": varsayilan_kitaplar,
            "haftalar": {},
            "okunan_kitaplar": {ogr: [] for ogr in varsayilan_ogrenciler}
        }
        # Başlangıçta her öğrenciye rastgele kitap ver
        kitaplar_kopya = veri["kitaplar"][:]
        random.shuffle(kitaplar_kopya)
        ilk_dagitim = dict(zip(veri["ogrenciler"], kitaplar_kopya))
        veri["haftalar"]["1"] = ilk_dagitim
        for ogr, kitap in ilk_dagitim.items():
            veri["okunan_kitaplar"][ogr].append(kitap)
        veriyi_kaydet(veri)
        return veri

def veriyi_kaydet(veri):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

# ------------------------------
# --- Rastgele dağıtım fonksiyonu ---
# ------------------------------
def kitap_dagit(veri, hafta_no, gelmeyenler):
    ogrenciler = veri["ogrenciler"]
    kitaplar = veri["kitaplar"]
    onceki_hafta = veri["haftalar"].get(str(hafta_no - 1), {})
    okunanlar = veri["okunan_kitaplar"]

    # Bu haftaya ait dağıtım sözlüğü
    yeni_dagitim = {}

    # 1️⃣ Önce geçen haftadan kitap sahipliklerini al
    ogrenci_kitap = onceki_hafta.copy()

    # 2️⃣ Gelmeyen öğrencilerin kitapları dağıtıma katılmaz
    gelenler = [o for o in ogrenciler if o not in gelmeyenler]
    gelen_kitaplar = [ogrenci_kitap[o] for o in gelenler if o in ogrenci_kitap]

    # 3️⃣ Uyarı kontrolü
    uyarilar = []
    for ogr in gelenler:
        okunmus = okunanlar.get(ogr, [])
        uygun_kitaplar = [k for k in gelen_kitaplar if k not in okunmus]
        if not uygun_kitaplar:
            # Okunmamış kitaplar gelmeyenlerde olabilir
            okunmayan = [k for k in kitaplar if k not in okunmus]
            okunmayan_sahipler = [o for o in ogrenciler if ogrenci_kitap.get(o) in okunmayan and o in gelmeyenler]
            if okunmayan_sahipler:
                uyarilar.append(f"⚠️ {ogr}: sınıfta bulunan tüm kitapları okumuştur. "
                                f"Okumadığı kitap(lar) şu öğrencilerde: {', '.join(okunmayan_sahipler)}")
            else:
                uyarilar.append(f"✅ {ogr}: tüm kitapları okumuştur.")

    # 4️⃣ Şimdi gelen öğrenciler arasında kitap değişimini yap
    rastgele_kitaplar = gelen_kitaplar[:]
    random.shuffle(rastgele_kitaplar)

    for ogr in gelenler:
        mevcut_kitap = ogrenci_kitap[ogr]
        okunmus = okunanlar[ogr]

        # Uygun kitap bul (daha önce okumadığı ve kendi kitabı olmayan)
        uygunlar = [k for k in rastgele_kitaplar if k not in okunmus and k != mevcut_kitap]

        if uygunlar:
            secilen = random.choice(uygunlar)
            yeni_dagitim[ogr] = secilen
            rastgele_kitaplar.remove(secilen)
        else:
            # Kitap bulamazsa mevcut kitabı kalsın
            yeni_dagitim[ogr] = mevcut_kitap

    # 5️⃣ Gelmeyenlerin kitapları sabit kalır
    for ogr in gelmeyenler:
        yeni_dagitim[ogr] = ogrenci_kitap[ogr]

    # 6️⃣ Okunan kitap listelerini güncelle
    for ogr, kitap in yeni_dagitim.items():
        if kitap not in okunanlar[ogr]:
            okunanlar[ogr].append(kitap)

    # 7️⃣ Veriyi kaydet
    veri["haftalar"][str(hafta_no)] = yeni_dagitim
    veri["okunan_kitaplar"] = okunanlar
    veriyi_kaydet(veri)

    return yeni_dagitim, uyarilar

# ------------------------------
# --- Streamlit Arayüzü ---
# ------------------------------
st.title("📚 Akıllı Kitap Dağıtım Sistemi")

veri = veriyi_yukle()
ogrenciler = veri["ogrenciler"]
haftalar = veri["haftalar"]

# Son işlenen hafta
son_hafta = max([int(h) for h in haftalar.keys()])
st.write(f"📅 Şu anda {son_hafta}. haftadasınız.")

# Gelmeyen öğrencileri seç
st.subheader("🚫 Bu hafta kitabını getirmeyen (veya gelmeyen) öğrencileri seçin:")
gelmeyenler = st.multiselect("Gelmeyen öğrenciler:", ogrenciler)

# Dağıtım başlat butonu
if st.button("📖 Dağıtımı Başlat"):
    if son_hafta >= 34:
        st.warning("✅ 34. haftaya ulaşıldı. Daha fazla dağıtım yapılmayacak.")
    else:
        yeni_hafta = son_hafta + 1
        dagitim, uyarilar = kitap_dagit(veri, yeni_hafta, gelmeyenler)
        st.success(f"✅ {yeni_hafta}. hafta kitap dağıtımı tamamlandı.")
        if uyarilar:
            st.warning("⚠️ Uyarılar:")
            for u in uyarilar:
                st.write(u)

# Haftaları görüntüle
st.subheader("📘 Geçmiş Dağıtımlar")
for hafta in sorted(haftalar.keys(), key=lambda x: int(x)):
    st.write(f"### 📅 {hafta}. Hafta")
    tablo = haftalar[hafta]
    for ogr, kitap in tablo.items():
        st.write(f"- **{ogr}** → {kitap}")
