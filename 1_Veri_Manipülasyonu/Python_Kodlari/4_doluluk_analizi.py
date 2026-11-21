import pandas as pd
import os
import shutil
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme", "birlesik_veri_türkçe.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "4_Doluluk_Analizi")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "4_Doluluk_Analizi")

def clear_outputs(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

clear_outputs(output_dir)
clear_outputs(gorsel_dir)

def analiz_et():
    print("Sütun bazlı doluluk analizi başlatılıyor (Adım 4)...")
    df = pd.read_excel(input_file)
    
    null_counts = df.isnull().sum()
    null_rates = (null_counts / len(df)) * 100
    full_rates = 100 - null_rates
    
    fullness_df = pd.DataFrame({
        'Sütun': full_rates.index,
        'Doluluk_Oranı': full_rates.values
    }).sort_values(by='Doluluk_Oranı', ascending=True)

    # --- AKADEMİK GÖRSELLEŞTİRME PANELİ ---
    print("Akademik analiz raporu oluşturuluyor...")
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2)

    # 1. Sütun Bazlı Doluluk (Barh)
    ax1 = fig.add_subplot(gs[:, 0])
    sns.barplot(x='Doluluk_Oranı', y='Sütun', data=fullness_df, palette='RdYlGn', ax=ax1, hue='Sütun', legend=False)
    ax1.set_title("Şekil 4.1: Özellik Bazlı Veri Doluluk Spektrumu (%)")
    ax1.set_xlim(0, 110)
    for p in ax1.patches:
        ax1.annotate(f'%{p.get_width():.1f}', (p.get_width() + 1, p.get_y() + p.get_height()/2), va='center', fontsize=9)

    # 2. Doluluk Dağılımı (Histogram)
    ax2 = fig.add_subplot(gs[0, 1])
    sns.histplot(fullness_df['Doluluk_Oranı'], bins=10, color='#2980b9', ax=ax2, kde=True)
    ax2.set_title("Şekil 4.2: Değişken Doluluk Oranı Frekans Dağılımı")

    # 3. Kritik Sütun Durum Tablosu
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')
    low_fill = fullness_df[fullness_df['Doluluk_Oranı'] < 90].sort_values(by='Doluluk_Oranı')
    table_data = [["Kritik Sütun", "Doluluk %", "Durum"]] + \
                 [[row['Sütun'], f"{row['Doluluk_Oranı']:.1f}%", "İyileştirilmeli"] for _, row in low_fill.head(10).iterrows()]
    if len(table_data) == 1: table_data.append(["Tüm Sütunlar", ">%90", "İyi"])
    
    tab = ax3.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.5, 0.2, 0.3])
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 2.5)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#c0392b'); cell.set_text_props(color='white', fontweight='bold')
        else: cell.set_facecolor('#fdf2f2')
    ax3.set_title("Tablo 4.1: Eksik Veri Bakımından Riskli Alanlar")

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_4_Konsolide_Rapor.png"))
    plt.close()
    print(f"Analiz tamamlandı. Akademik rapor oluşturuldu: {gorsel_dir}")

if __name__ == "__main__":
    analiz_et()
