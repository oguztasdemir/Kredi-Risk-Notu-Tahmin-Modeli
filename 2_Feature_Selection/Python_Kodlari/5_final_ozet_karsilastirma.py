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
raw_data_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
filter_report = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "1_Filter_Method", "1_filter_korelasyon_raporu.xlsx")
embedded_report = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "2_Embedded_Method", "2_ozellik_onem_siralamasi.xlsx")
final_data_file = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "2_Embedded_Method", "2_secilmis_ozellikler.xlsx")

output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "5_Final_Comparison")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "5_Final_Comparison")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def gorsel_olustur_akademik(stats, dropped_df):
    print("\n> Akademik Karşılaştırma Görselleri Hazırlanıyor (Figure 9 & Table 5)...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Figure 9: Özellik Sayısı Değişimi
    plt.figure(figsize=(10, 6))
    labels = ['Başlangıç (Raw)', 'Seçilen (Selected)']
    counts = [stats['raw_count'], stats['final_count']]
    sns.barplot(x=labels, y=counts, palette="mako")
    for i, v in enumerate(counts):
        plt.text(i, v + 0.5, str(v), ha='center', fontsize=12, fontweight='bold')
    plt.title("Figure 9: Özellik Seçimi Öncesi ve Sonrası Sütun Sayıları", fontsize=14, fontweight='bold')
    plt.ylabel("Sütun Sayısı")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_9_Feature_Count_Reduction.png"), dpi=300)
    plt.close()

    # 2. Table 5: Elenen Özellikler Karar Matrisi
    plt.figure(figsize=(12, 10))
    plt.axis('off')
    col_labels = ['Sütun Adı', 'Eleme Nedeni', 'Detay/Skor']
    table_data = dropped_df.values.tolist()
    
    # Çok uzunsa sadece ilk 25'i gösterelim (Rapor formatı için)
    the_table = plt.table(cellText=table_data[:30], colLabels=col_labels, loc='center', cellLoc='left')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(9)
    the_table.scale(1, 1.5)
    plt.title("Table 5: Elenen Özellikler ve Karar Gerekçeleri (Audit Trail)", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_5_Dropped_Features_Audit.png"), dpi=300)
    plt.close()

def final_comparison_fs5():
    print("\n" + "="*50)
    print("FEATURE SELECTION - ADIM 5: FINAL KARŞILAŞTIRMA")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Verileri Oku
    df_raw = pd.read_excel(raw_data_file, engine='openpyxl')
    df_final = pd.read_excel(final_data_file, engine='openpyxl')
    
    df_filter_rep = pd.read_excel(filter_report, sheet_name='Elenen_Sutunlar')
    df_imp_rep = pd.read_excel(embedded_report)

    # 2. Sütun Kıyaslama
    raw_cols = list(df_raw.columns)
    final_cols = list(df_final.columns)
    
    stats = {
        'raw_count': len(raw_cols),
        'final_count': len(final_cols)
    }

    # 3. Elenenlerin Gerekçelerini Belirle
    dropped_cols = [c for c in raw_cols if c not in final_cols]
    dropped_data = []

    filter_dropped = set(df_filter_rep['Elenen'].values)
    
    for col in raw_cols:
        if col in final_cols:
            continue # Atla, elenmedi
            
        if col in filter_dropped:
            rel = df_filter_rep[df_filter_rep['Elenen'] == col]['İlişkili'].values[0]
            reason = "Redundant (Korelasyon)"
            detail = f"İlişkili: {rel}"
        elif col == "İsim":
            reason = "Korunan Kimlik"
            detail = "Analiz İçin Saklandı"
            continue # İsim aslında elenmedi, final_cols içinde olmalı
        elif any(x in col for x in ["ID", "Kimlik"]):
            reason = "Teknik Sütun"
            detail = "Model Dışı"
        else:
            reason = "Düşük Önem Skoru"
            if col in df_imp_rep['Özellik'].values:
                score = df_imp_rep[df_imp_rep['Özellik'] == col]['Önem Skoru'].values[0]
                detail = f"Skor: {score:.4f}"
            else:
                detail = "N/A"
        
        dropped_data.append([col, reason, detail])

    df_dropped = pd.DataFrame(dropped_data, columns=['Sütun Adı', 'Eleme Nedeni', 'Detay'])

    # 4. Kayıt
    output_file = os.path.join(output_dir, "feature_selection_final_denetim.xlsx")
    df_dropped.to_excel(output_file, index=False)

    # 5. Görselleştirme
    gorsel_olustur_akademik(stats, df_dropped)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    final_comparison_fs5()
