import pandas as pd
import os
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle
import sys

# Ana dizini bul ve sys.path'e ekle (kullanici.py'yi import edebilmek için)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

input_dir = os.path.join(base_path, "0_Dataset")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "2_Musteri_ID_Kontrolu")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "2_Musteri_ID_Kontrolu")

def clear_outputs(directory):
    if os.path.exists(directory):
        print(f"Eski çıktılar siliniyor: {directory}")
        shutil.rmtree(directory)
    os.makedirs(directory)

# Klasörleri temizle
clear_outputs(output_dir)
clear_outputs(gorsel_dir)

def add_labels(ax):
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 10),
                    textcoords='offset points', fontweight='bold')

def analyze_all():
    print("Kapsamlı analiz başlatılıyor...")
    train_df = pd.read_csv(os.path.join(input_dir, "egitim_verisi.csv"), low_memory=False)
    test_df = pd.read_csv(os.path.join(input_dir, "test_verisi.csv"), low_memory=False)
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2)

    # 1. ID DOLULUK (Bar Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    train_total = len(train_df); test_total = len(test_df)
    train_null = train_df['Customer_ID'].isnull().sum(); test_null = test_df['Customer_ID'].isnull().sum()
    labels = ['Eğitim (Dolu)', 'Eğitim (Boş)', 'Test (Dolu)', 'Test (Boş)']
    values = [train_total - train_null, train_null, test_total - test_null, test_null]
    sns.barplot(x=labels, y=values, palette=['#2980b9', '#c0392b', '#3498db', '#e74c3c'], ax=ax1, hue=labels, legend=False)
    ax1.set_title("Şekil 2.1: Müşteri ID Kayıt Doluluk Oranları")
    for p in ax1.patches:
        ax1.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width()/2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 2. VENN ANALİZİ (Görselleştirilmiş Küme Çakışması)
    ax2 = fig.add_subplot(gs[0, 1])
    train_ids = set(train_df['Customer_ID'].unique()); test_ids = set(test_df['Customer_ID'].unique())
    common_ids = train_ids.intersection(test_ids)
    circle1 = Circle((-0.4, 0), 1, alpha=0.2, color='#2980b9')
    circle2 = Circle((0.4, 0), 1, alpha=0.2, color='#e67e22')
    ax2.add_patch(circle1); ax2.add_patch(circle2)
    ax2.text(-0.7, 0, f"Eğitim\n{len(train_ids)}", ha='center', fontweight='bold')
    ax2.text(0.7, 0, f"Test\n{len(test_ids)}", ha='center', fontweight='bold')
    ax2.text(0, 0, f"Ortak\n{len(common_ids)}", ha='center', fontweight='bold', color='#2c3e50')
    ax2.set_xlim(-1.8, 1.8); ax2.set_ylim(-1.2, 1.2); ax2.axis('off')
    ax2.set_title("Şekil 2.2: Veri Setleri Arası Müşteri ID Çakışma Analizi")

    # 3. ÖZET VERİ SAĞLIĞI TABLOSU
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    table_data = [
        ["Metrik Tanımı", "Eğitim Seti", "Test Seti", "Toplam / Ortak"],
        ["Toplam Satır Sayısı", train_total, test_total, train_total + test_total],
        ["Eksik ID Sayısı", train_null, test_null, train_null + test_null],
        ["Benzersiz Müşteri", len(train_ids), len(test_ids), "-"],
        ["Veri Bütünlüğü", f"{(1 - train_null/train_total)*100:.2f}%", f"{(1 - test_null/test_total)*100:.2f}%", "Kritik"]
    ]
    tab = ax3.table(cellText=table_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 2.5)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#34495e'); cell.set_text_props(color='white', fontweight='bold')
        else: cell.set_facecolor('#fdfefe')
    ax3.set_title("Tablo 2.1: Müşteri ID Denetimi ve Veri Sağlığı İndeksi", pad=30)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_2_Konsolide_Rapor.png"))
    plt.close()
    print("Analiz raporu başarıyla oluşturuldu.")

if __name__ == "__main__":
    analyze_all()
