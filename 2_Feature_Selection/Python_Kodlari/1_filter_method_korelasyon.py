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
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "1_Filter_Method")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "1_Filter_Method")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def gorsel_olustur_mantiksal(df, corr_matrix, dropped_info, target_corr):
    print("\n> Mantıksal ve Akademik Görseller Hazırlanıyor...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Figure 1: Global Korelasyon Haritası (Alt Üçgen)
    # Mantık: Hangi özellikler birbirinin kopyası? Bunu görmek için matris şart.
    plt.figure(figsize=(16, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=False, cmap="coolwarm", center=0, cbar_kws={"shrink": .8})
    plt.title("Figure 1: Özellikler Arası Korelasyon Yapısı (Multicollinearity Analizi)", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_1_Correlation_Structure.png"), dpi=300)
    plt.close()

    # 2. Figure 2: Hedef Değişken (Kredi Skoru) ile İlişki Sıralaması
    # Mantık: Hangi veriler tahminde 'sinyal' taşıyor?
    plt.figure(figsize=(12, 10))
    target_data = target_corr.abs().sort_values(ascending=False)
    sns.barplot(x=target_data.values, y=target_data.index, palette="Blues_r")
    plt.title("Figure 2: Özelliklerin Kredi Skoru Üzerindeki Etki Gücü (Mutlak Değer)", fontsize=14, fontweight='bold')
    plt.xlabel("Mutlak Pearson Korelasyon Katsayısı")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_2_Feature_Importance_Pearson.png"), dpi=300)
    plt.close()

    # 3. Table 1: Özellik Eleme Karar Matrisi
    # Mantık: Ne yaptık? Kaç veri gitti? Neden?
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    col_labels = ['Kategori', 'Metrik', 'Değer']
    table_data = [
        ['Girdi', 'Başlangıç Özellik Sayısı', str(len(corr_matrix))],
        ['İşlem', 'Elenen Kopya (r > 0.90)', str(len(dropped_info))],
        ['Çıktı', 'Kalan Özellik Sayısı', str(len(df.columns))],
        ['Yöntem', 'Filter Method', 'Pearson']
    ]
    the_table = plt.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 2.5)
    plt.title("Table 1: Özellik Eleme Süreci Özet Tablosu", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_1_Selection_Summary.png"), dpi=300)
    plt.close()

def filter_method_fs1():
    print("\n" + "="*50)
    print("FEATURE SELECTION - ADIM 1: FILTER METHOD")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Veriyi Yükle
    print("> Sayısallaştırılmış veri seti yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')

    # 2. Korelasyon Hesapla
    print("> Pearson korelasyon matrisi hesaplanıyor...")
    corr_matrix = df.corr()

    # 3. Redundant Sütunları Tespit Et
    threshold = 0.90
    dropped_cols = set()
    dropped_info = []

    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                col_i = corr_matrix.columns[i]
                col_j = corr_matrix.columns[j]
                if any(x in col_i for x in ["ID", "Kimlik"]): continue
                
                dropped_cols.add(col_i)
                dropped_info.append([col_i, col_j, corr_matrix.iloc[i, j]])

    # 4. Sütunları Ele
    df_filtered = df.drop(columns=list(dropped_cols))
    print(f"> {len(dropped_cols)} adet kopya sütun elendi.")

    # 5. Hedef İlişkisi
    target_corr = corr_matrix["Kredi Skoru"].drop("Kredi Skoru") if "Kredi Skoru" in corr_matrix.columns else pd.Series()

    # 6. Kayıt
    output_file = os.path.join(output_dir, "1_filter_sonrasi_veri.xlsx")
    report_file = os.path.join(output_dir, "1_filter_korelasyon_raporu.xlsx")
    
    df_filtered.to_excel(output_file, index=False)
    with pd.ExcelWriter(report_file, engine='xlsxwriter') as writer:
        corr_matrix.to_excel(writer, sheet_name='Korelasyon_Matrisi')
        pd.DataFrame(dropped_info, columns=['Elenen', 'İlişkili', 'Katsayı']).to_excel(writer, sheet_name='Elenen_Sutunlar', index=False)

    # 7. Görselleştirme
    gorsel_olustur_mantiksal(df_filtered, corr_matrix, dropped_info, target_corr)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    filter_method_fs1()
