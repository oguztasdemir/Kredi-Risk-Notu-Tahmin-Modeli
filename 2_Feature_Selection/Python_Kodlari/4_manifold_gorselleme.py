import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "3_PCA_Analizi", "3_pca_verisi.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "4_Manifold_Visualization")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "4_Manifold_Visualization")

def fresh_start():
    """Eski çıktıları ve görselleri temizler."""
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    print("> Temiz bir başlangıç yapıldı (Eski çıktılar silindi).")

def manifold_analizi_fs4():
    print("\n" + "="*50)
    print("FEATURE SELECTION - ADIM 4: MANIFOLD LEARNING (t-SNE)")
    print("="*50)

    # 0. Temizlik
    fresh_start()

    # 1. Veriyi Yükle
    print("> PCA verisi yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')
    
    # Performans için örnekleme (Sampling)
    sample_size = 5000
    if len(df) > sample_size:
        print(f"> Veri seti çok büyük, analiz için {sample_size} adet rastgele örnek seçiliyor...")
        df_sample = df.sample(n=sample_size, random_state=42)
    else:
        df_sample = df

    X = df_sample.drop(columns=["Kredi Skoru"])
    y = df_sample["Kredi Skoru"]

    # 2. t-SNE Uygula
    print("> t-SNE hesaplanıyor (Bu işlem birkaç dakika sürebilir)...")
    tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42, init='pca', learning_rate='auto')
    X_tsne = tsne.fit_transform(X)

    # 3. Görselleştirme (Figure 7)
    print("> Akademik Görseller Hazırlanıyor (Figure 7 & 8)...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    plt.figure(figsize=(12, 10))
    scatter = plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='coolwarm', alpha=0.6, s=10)
    plt.colorbar(scatter, label='Kredi Skoru (Hedef Sınıf)')
    plt.title("Figure 7: t-SNE Manifold Görselleştirmesi (Veri Kümeleme Analizi)", fontsize=14, fontweight='bold')
    plt.xlabel("t-SNE Boyut 1")
    plt.ylabel("t-SNE Boyut 2")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_7_tSNE_Visualization.png"), dpi=300)
    plt.close()

    # 4. Table 4: Manifold Teknik Analiz Özeti
    plt.figure(figsize=(10, 4))
    plt.axis('off')
    col_labels = ['Parametre', 'Değer']
    table_data = [
        ['Algoritma', 't-SNE'],
        ['Örneklem Sayısı', str(sample_size)],
        ['Perplexity', '30'],
        ['Yineleme (Iter)', '1000'],
        ['İlklendirme', 'PCA']
    ]
    the_table = plt.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(12)
    the_table.scale(1.2, 2.5)
    plt.title("Table 4: t-SNE Manifold Analiz Parametreleri", fontsize=14, pad=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Table_4_Manifold_Summary.png"), dpi=300)
    plt.close()

    # 5. Sonuçları Kaydet
    output_file = os.path.join(output_dir, "4_manifold_sonuclari.xlsx")
    df_tsne = pd.DataFrame(X_tsne, columns=["TSNE_1", "TSNE_2"])
    df_tsne["Kredi Skoru"] = y.values
    df_tsne.to_excel(output_file, index=False)

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Klasör: {output_dir}")

if __name__ == "__main__":
    manifold_analizi_fs4()
