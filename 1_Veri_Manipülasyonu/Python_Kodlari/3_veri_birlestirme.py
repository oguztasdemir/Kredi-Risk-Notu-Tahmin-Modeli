import pandas as pd
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Ana dizini bul ve sys.path'e ekle (kullanici.py'yi import edebilmek için)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Adım 1'deki TÜRKÇE Excel dosyalarını kullanıyoruz
input_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "1_Format_ve_Ceviri")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "3_Veri_Birlestirme")

def clear_outputs(directory):
    if os.path.exists(directory):
        print(f"Eski çıktılar siliniyor: {directory}")
        shutil.rmtree(directory)
    os.makedirs(directory)

# Klasörleri temizle
clear_outputs(output_dir)
clear_outputs(gorsel_dir)

# Türkçe Ay sıralaması
ay_sirasi = {
    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4,
    "Mayıs": 5, "Haziran": 6, "Temmuz": 7, "Ağustos": 8,
    "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
}

def autolabel(rects, ax):
    """Sütunların üzerine değerlerini yazar"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

def birlestir_ve_sirala():
    print("Türkçe veriler okunuyor...")
    egitim = pd.read_excel(os.path.join(input_dir, "egitim_verisi.xlsx"))
    test = pd.read_excel(os.path.join(input_dir, "test_verisi.xlsx"))
    
    print(f"Eğitim satır sayısı: {len(egitim)}")
    print(f"Test satır sayısı: {len(test)}")
    
    # 1. Birleştirme
    birlesik_df = pd.concat([egitim, test], ignore_index=True)
    
    # 2. Ay Sıralaması için sayısal sütun
    birlesik_df['Ay_No'] = birlesik_df['Ay'].map(ay_sirasi)
    
    # 3. Müşteri ID ve Ay No'ya göre sırala
    print("Kronolojik sıralama yapılıyor...")
    birlesik_df.sort_values(by=['Müşteri ID', 'Ay_No'], inplace=True)
    birlesik_df.drop(columns=['Ay_No'], inplace=True)
    
    # 4. Kaydet
    output_yolu = os.path.join(output_dir, "birlesik_veri_türkçe.xlsx")
    print(f"Birleşik dosya kaydediliyor: {output_yolu}")
    birlesik_df.to_excel(output_yolu, index=False)
    
    # --- GÖRSELLEŞTİRMELER ---
    print("Pedagojik görseller oluşturuluyor...")
    sns.set_style("whitegrid")
    
    # Görsel 1: Ay Bazlı Kayıt Sayısı (Bar Chart)
    plt.figure(figsize=(14, 7))
    ay_counts = birlesik_df['Ay'].value_counts().reindex(ay_sirasi.keys())
    ax1 = sns.barplot(x=ay_counts.index, y=ay_counts.values, palette="coolwarm", hue=ay_counts.index, legend=False)
    autolabel(ax1.patches, ax1)
    plt.title('Birleşik Veri Seti: Aylık Kayıt Dağılımı', fontsize=16, pad=20)
    plt.xlabel('Aylar', fontsize=12)
    plt.ylabel('Kayıt Sayısı', fontsize=12)
    plt.ylim(0, ay_counts.max() * 1.15) # Tepe değerlerin sığması için pay bırak
    plt.xticks(rotation=0) # Yatay metinler
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_aylik_dagilim.png"), dpi=150)
    plt.close()

    # Görsel 2: Kredi Skoru Dağılımı (Donut Chart)
    plt.figure(figsize=(10, 7))
    skor_counts = birlesik_df['Kredi Skoru'].value_counts()
    plt.pie(skor_counts, labels=skor_counts.index, autopct='%1.1f%%', startangle=140, 
            colors=sns.color_palette("pastel"), wedgeprops={'width': 0.4})
    plt.title('Genel Kredi Skoru Dağılımı', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "2_kredi_skoru_donut.png"), dpi=150)
    plt.close()

    # Görsel 3: Müşteri Başına Veri Devamlılığı (Pedagojik Histogram)
    plt.figure(figsize=(12, 6))
    musteri_ay_sayisi = birlesik_df.groupby('Müşteri ID')['Ay'].count()
    ax3 = sns.histplot(musteri_ay_sayisi, bins=range(1, 14), color='skyblue', kde=False)
    plt.title('Veri Devamlılığı: Her Müşteri İçin Kaç Aylık Veri Var?', fontsize=16)
    plt.xlabel('Toplam Ay Sayısı', fontsize=12)
    plt.ylabel('Müşteri Sayısı', fontsize=12)
    plt.xticks(range(1, 13))
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "3_veri_devamliligi.png"), dpi=150)
    plt.close()

    print("Tüm görseller başarıyla oluşturuldu.")

if __name__ == "__main__":
    birlestir_ve_sirala()
