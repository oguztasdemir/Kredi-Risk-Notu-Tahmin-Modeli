import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "2_Embedded_Method", "2_secilmis_ozellikler.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "3_PCA_Analizi")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "3_PCA_Analizi")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def gorsel_olustur_akademik(pca, X_pca, n_comp, y):
    print("\n> Akademik Görseller Hazırlanıyor (Figure 5 & 6)...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Figure 5: Açıklanan Varyans Oranı (Scree Plot)
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), 
             np.cumsum(pca.explained_variance_ratio_), marker='o', linestyle='--', color='#16a085')
    plt.axhline(y=0.90, color='r', linestyle=':', label='%90 Varyans Sınırı')
    plt.title("Figure 5: PCA Kümülatif Açıklanan Varyans Oranı", fontsize=14, fontweight='bold')
    plt.xlabel("Bileşen Sayısı (Components)")
    plt.ylabel("Kümülatif Açıklanan Varyans")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_5_PCA_Variance_Ratio.png"), dpi=300)
    plt.close()

    # 2. Figure 6: PCA 2D İzdüşüm (PCA 1 vs PCA 2)
    plt.figure(figsize=(10, 8))
    # Renklendirme için Kredi Skoru'nu kullanalım
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', alpha=0.5, s=2)
    plt.colorbar(scatter, label='Kredi Skoru (Sayısal)')
    plt.title("Figure 6: Veri Setinin İlk İki Temel Bileşen (PCA) Üzerindeki Dağılımı", fontsize=12, fontweight='bold')
    plt.xlabel(f"Temel Bileşen 1 (%{pca.explained_variance_ratio_[0]*100:.1f})")
    plt.ylabel(f"Temel Bileşen 2 (%{pca.explained_variance_ratio_[1]*100:.1f})")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_PCA_2D_Projection.png"), dpi=300)
    plt.close()

    # 3. Table 3: PCA Özet İstatistikleri
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    col_labels = ['Metrik', 'Değer']
    table_data = [
        ['Uygulanan Yöntem', 'Temel Bileşen Analizi (PCA)'],
        ['Girdi Özellik Sayısı', str(pca.n_features_in_)],
        ['Seçilen Bileşen Sayısı (%90 Varyans)', str(n_comp)],
        ['Veri Sıkıştırma Oranı', f"%{((1 - n_comp/pca.n_features_in_)*100):.1f}"],
        ['Toplam Açıklanan Varyans', f"%{np.sum(pca.explained_variance_ratio_)*100:.2f}"]
    ]
    the_table = plt.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 2.5)
    plt.title("Table 3: PCA Boyut Düşürme Analizi Özeti", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_3_PCA_Summary.png"), dpi=300)
    plt.close()

def pca_analizi_fs3():
    print("\n" + "="*50)
    print("FEATURE SELECTION - ADIM 3: PCA ANALZ")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Veriyi Yükle
    print("> Seçilmiş özellikler yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')

    # 2. X ve y Ayır, Standardizasyon yap
    X = df.drop(columns=["Kredi Skoru"])
    y = df["Kredi Skoru"]
    
    # PCA için verilerin NaN içermemesi gerekir. 
    # Zaten önceki adımlarda doldurulmuş olmalı ama garantiye alalım.
    X = X.fillna(X.mean())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. PCA Uygula (%90 varyansı koru)
    print("> PCA hesaplanıyor...")
    pca_temp = PCA(n_components=0.90, svd_solver='full')
    X_pca = pca_temp.fit_transform(X_scaled)
    n_components = X_pca.shape[1]
    
    print(f"> Bilginin %90'ını korumak için {n_components} bileşen yeterli bulundu.")

    # 4. Kayıt
    output_file = os.path.join(output_dir, "3_pca_verisi.xlsx")
    report_file = os.path.join(output_dir, "3_pca_varyans_raporu.xlsx")
    
    pca_cols = [f"Bilesen_{i+1}" for i in range(n_components)]
    df_pca = pd.DataFrame(X_pca, columns=pca_cols)
    df_pca["Kredi Skoru"] = y.values
    
    if "İsim" in df.columns:
        df_pca["İsim"] = df["İsim"].values
    
    df_pca.to_excel(output_file, index=False)
    
    varyans_df = pd.DataFrame({
        "Bileşen": pca_cols,
        "Açıklanan Varyans": pca_temp.explained_variance_ratio_,
        "Kümülatif Varyans": np.cumsum(pca_temp.explained_variance_ratio_)
    })
    varyans_df.to_excel(report_file, index=False)

    # 5. Görselleştirme
    gorsel_olustur_akademik(pca_temp, X_pca, n_components, y)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    pca_analizi_fs3()
