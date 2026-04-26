import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import shutil

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "2_Embedded_Method", "2_secilmis_ozellikler.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "1_Veri_Hazirlik")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def gorsel_olustur_hazirlik(df_labeled, df_unlabeled):
    print("\n> Veri Hazırlık Görselleri Hazırlanıyor...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Figure 1: Labeled vs Unlabeled Dağılımı
    plt.figure(figsize=(10, 6))
    labels = ['Etiketli (Eğitim/Test)', 'Etiketsiz (Tahmin Bekleyen)']
    counts = [len(df_labeled), len(df_unlabeled)]
    sns.barplot(x=labels, y=counts, palette=["#3498db", "#e74c3c"])
    for i, v in enumerate(counts):
        plt.text(i, v + 500, f"{v:,}", ha='center', fontsize=12, fontweight='bold')
    plt.title("Figure 1: Veri Seti Bölünme Stratejisi (Etiket Durumu)", fontsize=14, fontweight='bold')
    plt.ylabel("Satır Sayısı")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_1_Data_Split_Status.png"), dpi=300)
    plt.close()

    # 2. Figure 2: Sütun Bazlı Doluluk Oranları (Kıyaslamalı)
    occ_labeled = df_labeled.notna().mean() * 100
    occ_unlabeled = df_unlabeled.notna().mean() * 100
    
    occ_df = pd.DataFrame({
        'Özellik': occ_labeled.index,
        'Etiketli Veri (%)': occ_labeled.values,
        'Etiketsiz Veri (%)': occ_unlabeled.values
    }).melt(id_vars='Özellik', var_name='Dataset', value_name='Doluluk')

    plt.figure(figsize=(12, 10))
    sns.barplot(data=occ_df, y='Özellik', x='Doluluk', hue='Dataset', palette="muted")
    plt.axvline(x=100, color='r', linestyle='--', alpha=0.5)
    plt.title("Figure 2: Datasetler Arası Sütun Doluluk Oranları (%)", fontsize=14, fontweight='bold')
    plt.xlim(0, 110)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_2_Column_Occupancy.png"), dpi=300)
    plt.close()

    # 3. Table 1: Hazırlık Özet Tablosu
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    col_labels = ['Dataset Tipi', 'Satır Sayısı', 'Kullanım Amacı']
    table_data = [
        ['Etiketli (Labeled)', f"{len(df_labeled):,}", 'Model Eğitimi ve Testi'],
        ['Etiketsiz (Unlabeled)', f"{len(df_unlabeled):,}", 'Gerçek Dünya Tahminleme'],
        ['Toplam', f"{len(df_labeled)+len(df_unlabeled):,}", 'Genel Popülasyon']
    ]
    the_table = plt.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 2.5)
    plt.title("Table 1: Modelleme Öncesi Veri Hazırlık Özeti", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_1_Preparation_Summary.png"), dpi=300)
    plt.close()

def veri_hazirlik_341():
    print("\n" + "="*50)
    print("CLASSIFICATION - ADIM 1: VERİ HAZIRLIK VE BÖLME")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Veriyi Yükle
    print("> Özellik seçimi tamamlanmış veri yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')

    # 2. Dataset'i 2'ye Böl (Etiketli ve Etiketsiz)
    df_labeled = df[df["Kredi Skoru"].notna()].copy()
    df_unlabeled = df[df["Kredi Skoru"].isna()].copy()

    # İsim sütununu 1. sıraya taşı
    if "İsim" in df.columns:
        cols = ["İsim"] + [c for c in df.columns if c != "İsim"]
        df_labeled = df_labeled[cols]
        df_unlabeled = df_unlabeled[cols]

    print(f"> Eğitim Datası Sayısı (Labeled): {len(df_labeled)}")
    print(f"> Test Datası Sayısı (Unlabeled): {len(df_unlabeled)}")

    # 3. Kayıt (Dosya adları sadeleştirildi)
    labeled_file = os.path.join(output_dir, "Egitim_Datasi.xlsx")
    unlabeled_file = os.path.join(output_dir, "Test_Datasi.xlsx")
    
    df_labeled.to_excel(labeled_file, index=False)
    df_unlabeled.to_excel(unlabeled_file, index=False)

    # 4. Görselleştirme
    gorsel_olustur_hazirlik(df_labeled, df_unlabeled)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    veri_hazirlik_341()
