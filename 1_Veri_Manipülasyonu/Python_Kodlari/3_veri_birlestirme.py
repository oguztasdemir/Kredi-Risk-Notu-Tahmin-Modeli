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
    
    # --- AKADEMİK GÖRSELLEŞTİRME PANELİ ---
    print("Akademik analiz raporu oluşturuluyor...")
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2)

    # 1. Ay Bazlı Dağılım (Line + Bar Hybrid)
    ax1 = fig.add_subplot(gs[0, 0])
    ay_counts = birlesik_df['Ay'].value_counts().reindex(ay_sirasi.keys())
    sns.barplot(x=ay_counts.index, y=ay_counts.values, palette="Blues_d", ax=ax1, hue=ay_counts.index, legend=False)
    ax1.plot(range(len(ay_counts)), ay_counts.values, color='#c0392b', marker='o', linewidth=2, label='Trend')
    ax1.set_title("Şekil 3.1: Kronolojik Veri Yoğunluğu (Aylık)")
    ax1.set_xticklabels(ay_counts.index, rotation=45)

    # 2. Kredi Skoru (Donut)
    ax2 = fig.add_subplot(gs[0, 1])
    skor_counts = birlesik_df['Kredi Skoru'].value_counts()
    ax2.pie(skor_counts, labels=skor_counts.index, autopct='%1.1f%%', startangle=140, 
            colors=['#27ae60', '#f1c40f', '#e67e22'], wedgeprops={'width': 0.4, 'edgecolor': 'white'})
    ax2.set_title("Şekil 3.2: Hedef Etiket (Kredi Skoru) Dağılımı")

    # 3. Veri Devamlılığı (Histogram)
    ax3 = fig.add_subplot(gs[1, 0])
    musteri_ay_sayisi = birlesik_df.groupby('Müşteri ID')['Ay'].count()
    sns.histplot(musteri_ay_sayisi, bins=range(1, 14), color='#2980b9', ax=ax3, kde=True)
    ax3.set_title("Şekil 3.3: Müşteri Başına Veri Devamlılığı")
    ax3.set_xlabel("Takip Edilen Ay Sayısı")

    # 4. Veri Seti İstatistik Tablosu
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    stats_data = [
        ["Parametre", "Değer"],
        ["Toplam Gözlem", len(birlesik_df)],
        ["Eğitim Payı", f"{(len(egitim)/len(birlesik_df))*100:.1f}%"],
        ["Test Payı", f"{(len(test)/len(birlesik_df))*100:.1f}%"],
        ["Eşsiz Müşteri", len(musteri_ay_sayisi)],
        ["Ortalama Kayıt/Müşteri", f"{musteri_ay_sayisi.mean():.2f}"]
    ]
    tab = ax4.table(cellText=stats_data, loc='center', cellLoc='center', colWidths=[0.5, 0.4])
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 2.5)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white', fontweight='bold')
        else: cell.set_facecolor('#f8f9fa')
    ax4.set_title("Tablo 3.1: Birleşik Veri Seti Betimsel İstatistikleri")

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_3_Konsolide_Rapor.png"))
    plt.close()
    print("Analiz raporu başarıyla oluşturuldu.")

if __name__ == "__main__":
    birlestir_ve_sirala()
