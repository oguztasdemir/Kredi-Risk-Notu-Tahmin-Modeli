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
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

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
    
    # Doluluk (veya boşluk) oranlarını hesapla
    # Kullanıcı azdan çoğa sırala dediği için doluluk oranlarını hesaplayıp sıralıyoruz
    null_counts = df.isnull().sum()
    null_rates = (null_counts / len(df)) * 100
    full_rates = 100 - null_rates
    
    # Veriyi hazırlayalım
    fullness_df = pd.DataFrame({
        'Sütun': full_rates.index,
        'Doluluk_Oranı': full_rates.values
    }).sort_values(by='Doluluk_Oranı', ascending=True) # Azdan çoğa sıralama

    # --- GÖRSEL 1: KLASİK YATAY BAR GRAFİĞİ ---
    plt.figure(figsize=(12, 10))
    ax1 = sns.barplot(x='Doluluk_Oranı', y='Sütun', data=fullness_df, palette='RdYlGn')
    plt.title('V1: Sütun Doluluk Oranları (Klasik Yatay)', fontsize=14, fontweight='bold')
    plt.xlabel('Doluluk Oranı (%)')
    plt.xlim(0, 110)
    for p in ax1.patches:
        ax1.annotate(f'%{p.get_width():.1f}', (p.get_width() + 1, p.get_y() + p.get_height()/2),
                    va='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "v1_klasik_yatay.png"))
    plt.close()

    # --- GÖRSEL 2: RENK GRADYANLI DİKEY BAR ---
    plt.figure(figsize=(14, 8))
    ax2 = sns.barplot(x='Sütun', y='Doluluk_Oranı', data=fullness_df, hue='Sütun', palette='magma', legend=False)
    plt.title('V2: Sütun Doluluk Oranları (Gradyanlı Dikey)', fontsize=14, fontweight='bold')
    plt.ylabel('Doluluk Oranı (%)')
    plt.xticks(rotation=90)
    plt.ylim(0, 115)
    for p in ax2.patches:
        ax2.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=8, rotation=90, xytext=(0, 5), textcoords='offset points')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "v2_gradyan_dikey.png"))
    plt.close()

    # --- GÖRSEL 3: LOLLIPOP CHART (MODERN) ---
    plt.figure(figsize=(12, 10))
    plt.hlines(y=fullness_df['Sütun'], xmin=0, xmax=fullness_df['Doluluk_Oranı'], color='skyblue', alpha=0.7, linewidth=2)
    plt.plot(fullness_df['Doluluk_Oranı'], fullness_df['Sütun'], "o", markersize=8, color='blue', alpha=0.6)
    plt.title('V3: Sütun Doluluk Oranları (Modern Lollipop)', fontsize=14, fontweight='bold')
    plt.xlabel('Doluluk Oranı (%)')
    for i, row in fullness_df.iterrows():
        plt.text(row['Doluluk_Oranı'] + 1, row['Sütun'], f"%{row['Doluluk_Oranı']:.1f}", va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "v3_lollipop.png"))
    plt.close()

    # --- GÖRSEL 4: HEATMAP (EKSİK VERİ YOĞUNLUĞU) ---
    plt.figure(figsize=(15, 6))
    # Örneklem alarak heatmap çizelim (Tüm veri çok büyük)
    sns.heatmap(df.sample(min(1000, len(df))).isnull(), yticklabels=False, cbar=False, cmap='viridis')
    plt.title('V4: Eksik Veri Matrisi (Sarı Alanlar Boşlukları Temsil Eder)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "v4_eksik_veri_matrisi.png"))
    plt.close()

    # --- GÖRSEL 5: DONUT CHART (EN KRİTİK 5 SÜTUN İÇİN) ---
    plt.figure(figsize=(10, 8))
    top_empty = fullness_df.head(5) # En çok boşluğu olan (doluluğu az olan) ilk 5
    plt.pie(top_empty['Doluluk_Oranı'], labels=top_empty['Sütun'], autopct='%1.1f%%', 
            startangle=140, colors=sns.color_palette('pastel'), wedgeprops={'width': 0.4})
    plt.title('V5: En Çok Boşluk İçeren 5 Sütunun Doluluk Kıyaslaması', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "v5_donut_kritik_bes.png"))
    plt.close()

    print(f"Analiz tamamlandı. 5 farklı görsel oluşturuldu: {gorsel_dir}")

if __name__ == "__main__":
    analiz_et()
