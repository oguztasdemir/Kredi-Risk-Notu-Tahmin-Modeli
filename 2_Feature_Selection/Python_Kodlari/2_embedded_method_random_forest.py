import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
from sklearn.ensemble import RandomForestClassifier

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "1_Filter_Method", "1_filter_sonrasi_veri.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "2_Embedded_Method")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "2_Embedded_Method")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def gorsel_olustur_akademik(feature_importances, top_features, cum_sum):
    print("\n> Akademik Görseller Hazırlanıyor (Figure 3 & 4)...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Figure 3: Özellik Önem Sıralaması (Feature Importance)
    plt.figure(figsize=(12, 10))
    sns.barplot(x=feature_importances.values, y=feature_importances.index, palette="viridis")
    plt.title("Figure 3: Rastgele Orman (Random Forest) Özellik Önem Skorları", fontsize=14, fontweight='bold')
    plt.xlabel("Gini Önem Skoru (Feature Importance)")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_3_Feature_Importance.png"), dpi=300)
    plt.close()

    # 2. Figure 4: Kümülatif Bilgi Kazancı (Cumulative Information Gain)
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(cum_sum) + 1), cum_sum, marker='o', linestyle='-', color='#2c3e50')
    plt.axhline(y=0.95, color='r', linestyle='--', label='%95 Bilgi Sınırı')
    plt.title("Figure 4: Kümülatif Bilgi Birikimi ve Seçim Eşiği", fontsize=14, fontweight='bold')
    plt.xlabel("Seçilen Özellik Sayısı")
    plt.ylabel("Kümülatif Önem (Cumulative Importance)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_4_Cumulative_Importance.png"), dpi=300)
    plt.close()

    # 3. Table 2: Seçilen Özellikler ve Önem Skorları
    plt.figure(figsize=(10, 6))
    plt.axis('off')
    col_labels = ['Sıra', 'Özellik', 'Önem Skoru']
    top_data = [[i+1, top_features[i], f"{feature_importances[top_features[i]]:.4f}"] for i in range(min(15, len(top_features)))]
    the_table = plt.table(cellText=top_data, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(11)
    the_table.scale(1.2, 1.8)
    plt.title("Table 2: En Yüksek Tahmin Gücüne Sahip Özellikler (Top 15)", fontsize=14, pad=30, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_2_Selected_Features_Summary.png"), dpi=300)
    plt.close()

def embedded_method_fs2():
    print("\n" + "="*50)
    print("FEATURE SELECTION - ADIM 2: EMBEDDED METHOD (RF)")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Veriyi Yükle
    print("> Filtrelenmiş veri seti yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')

    # 2. X ve y Ayır
    # Eğitim için sadece Kredi Skoru olan (NaN olmayan) satırları kullanmalıyız
    df_train = df[df["Kredi Skoru"].notna()]
    
    # ML modeline girmeyecek sütunlar (İsim dahil)
    drop_cols = ["ID", "Kimlik No", "Müşteri ID", "İsim", "Kredi Skoru"]
    X = df_train.drop(columns=[c for c in drop_cols if c in df_train.columns])
    y = df_train["Kredi Skoru"]

    # 3. Model Eğitimi (Önem Skoru için)
    print("> Random Forest Modeli eğitiliyor (Lütfen bekleyin)...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    # 4. Özellik Önemlerini Hesapla
    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    cum_sum = np.cumsum(importances.values)

    # 5. Özellik Seçimi (%95 kümülatif önem koruma kuralı)
    num_selected = np.searchsorted(cum_sum, 0.95) + 1
    top_features = importances.index[:num_selected]
    print(f"> Bilginin %95'ini temsil eden {num_selected} özellik seçildi.")

    # 6. Kayıt
    output_file = os.path.join(output_dir, "2_secilmis_ozellikler.xlsx")
    report_file = os.path.join(output_dir, "2_ozellik_onem_siralamasi.xlsx")
    
    # İsim sütununu analizler için koruyoruz (Zaman serisi/Kullanıcı bazlı takip için)
    final_cols_to_keep = list(top_features) + ["Kredi Skoru"]
    if "İsim" in df.columns:
        final_cols_to_keep.append("İsim")
        
    df_selected = df[final_cols_to_keep]
    df_selected.to_excel(output_file, index=False)
    
    importances_df = pd.DataFrame({"Özellik": importances.index, "Önem Skoru": importances.values})
    importances_df.to_excel(report_file, index=False)

    # 7. Görselleştirme
    gorsel_olustur_akademik(importances, top_features, cum_sum)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    embedded_method_fs2()
