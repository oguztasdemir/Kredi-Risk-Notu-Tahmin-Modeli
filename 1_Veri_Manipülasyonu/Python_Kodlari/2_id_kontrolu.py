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
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

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
    
    # --- GÖRSEL 1: DOLULUK ANALİZİ (BAR CHART) ---
    train_total = len(train_df)
    test_total = len(test_df)
    train_null = train_df['Customer_ID'].isnull().sum()
    test_null = test_df['Customer_ID'].isnull().sum()
    
    plt.figure(figsize=(10, 6))
    labels_null = ['Eğitim (Dolu)', 'Eğitim (Boş)', 'Test (Dolu)', 'Test (Boş)']
    values_null = [train_total - train_null, train_null, test_total - test_null, test_null]
    ax1 = sns.barplot(x=labels_null, y=values_null, palette=['#2ecc71', '#e74c3c', '#2ecc71', '#e74c3c'], hue=labels_null, legend=False)
    plt.title('Görsel 1: Müşteri ID Doluluk Analizi (Satır Bazlı)', fontsize=14, fontweight='bold')
    add_labels(ax1)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_id_doluluk.png"), dpi=150)
    plt.close()

    # --- GÖRSEL 2: VERİ ÇAKIŞMA ANALİZİ (VENN - SATIR BAZLI) ---
    combined = pd.concat([train_df, test_df])
    duplicates_count = combined.duplicated().sum()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    circle1 = Circle((-0.4, 0), 1, alpha=0.3, color='skyblue', label='Eğitim')
    circle2 = Circle((0.4, 0), 1, alpha=0.3, color='salmon', label='Test')
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.text(-0.8, 0, f"{train_total}", fontsize=16, fontweight='bold', ha='center')
    ax.text(0.8, 0, f"{test_total}", fontsize=16, fontweight='bold', ha='center')
    ax.text(0, 0, f"{duplicates_count}", fontsize=20, fontweight='bold', ha='center', color='black')
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title('Görsel 2: Veri Çakışma Analizi (Satır-Satır)', fontsize=16, fontweight='bold', pad=20)
    plt.legend(handles=[circle1, circle2], loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "2_id_venn_satir.png"), dpi=150)
    plt.close()

    # --- GÖRSEL 3: MÜŞTERİ SAYISI ÖZET TABLOSU ---
    train_ids = set(train_df['Customer_ID'].unique())
    test_ids = set(test_df['Customer_ID'].unique())
    common_ids = train_ids.intersection(test_ids)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    table_data = [
        ["Kategori", "Benzersiz Müşteri Sayısı"],
        ["Eğitim Verisi", len(train_ids)],
        ["Test Verisi", len(test_ids)],
        ["Ortak (Çakışan) Müşteriler", len(common_ids)]
    ]
    table = ax.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.5, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2.5)
    for i in range(2):
        table[(0, i)].set_facecolor("#34495e")
        table[(0, i)].set_text_props(color="white", fontweight='bold')
    plt.title('Görsel 3: Müşteri Sayısı Özet Tablosu', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "3_musteri_sayisi_tablo.png"), dpi=150)
    plt.close()
    
    print("Tüm analizler başarıyla tamamlandı.")

if __name__ == "__main__":
    analyze_all()
