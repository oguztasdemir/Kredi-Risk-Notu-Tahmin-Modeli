import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Proje ana dizini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Yollar
input_file = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "3_Wrapper_Metodu", "3_wrapper_sonrasi_veri.xlsx")
output_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "4_PCA_Analizi")
gorsel_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "4_PCA_Analizi")

import shutil

def setup_folders():
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def pca_analizi():
    print("\n" + "="*60)
    print("FAZ 2 - ADIM 2.4: BOYUT İNDİRGEME (PCA - TEMEL BİLEŞEN ANALİZİ)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    df = pd.read_excel(input_file)
    X = df.drop(columns=["Kredi Skoru"])
    y = df["Kredi Skoru"]
    
    # PCA öncesi standartlaştırma şarttır
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. PCA Uygulama
    pca = PCA()
    pca.fit(X_scaled)
    
    # Varyans Açıklama Oranları
    exp_var_ratio = pca.explained_variance_ratio_
    cum_var_ratio = np.cumsum(exp_var_ratio)

    # %90 varyansı açıklayan bileşen sayısını bul
    n_components_90 = np.searchsorted(cum_var_ratio, 0.90) + 1
    print(f"> Bilginin %90'ını korumak için {n_components_90} adet temel bileşen yeterlidir.")

    # 3. Görselleştirme
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Figure 6: Scree Plot (Varyans Açıklama)
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(1, 11), exp_var_ratio[:10], alpha=0.5, align='center', label='Bireysel Varyans')
    plt.step(range(1, 11), cum_var_ratio[:10], where='mid', label='Kümülatif Varyans', color='red')
    
    # İlk 5 bileşen için değerleri ekle
    for i, bar in enumerate(bars[:5]):
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 0.01, f'%{h*100:.1f}', ha='center', fontweight='bold', fontsize=8)

    plt.axhline(y=0.90, color='r', linestyle='--')
    plt.title("Figür 2-6: İlk 10 PCA Bileşeni Varyans Oranları", fontweight='bold')
    plt.xlabel("Temel Bileşen İndeksi")
    plt.ylabel("Açıklanan Varyans Oranı")
    
    # Not Ekle
    plt.text(0.6, 0.2, f"Bilginin %90'ı için:\n{n_components_90} Bileşen Yeterli", 
             transform=plt.gca().transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    
    plt.legend(loc='best')
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_PCA_Varyans.png"), dpi=300)
    plt.close()

    # Figure 7: 2D PCA Projeksiyonu
    plt.figure(figsize=(10, 8))
    X_pca = pca.transform(X_scaled)
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=y, palette='viridis', alpha=0.6)
    plt.title("Figür 2-7: Verilerin 2D PCA Düzlemindeki Dağılımı", fontweight='bold')
    plt.xlabel("PC1 (En Yüksek Varyans)")
    plt.ylabel("PC2 (İkinci Yüksek Varyans)")
    
    # Not
    plt.text(0.5, -0.1, "Bu grafik, verilerin 2 boyutta ne kadar iyi kümelendiğini gösterir.\nAyrık kümeler, modelin öğrenme kolaylığını işaret eder.", 
             ha='center', transform=plt.gca().transAxes, fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_7_PCA_2D_Projeksiyon.png"), dpi=300)
    plt.close()

    # 4. Kayıt
    pca_results = pd.DataFrame(pca.transform(X_scaled)[:, :n_components_90], 
                               columns=[f"PC{i+1}" for i in range(n_components_90)])
    pca_results.to_excel(os.path.join(output_dir, "4_pca_sonrasi_veri.xlsx"), index=False)

    print(f"\n> BAŞARILI! PCA analizi tamamlandı.")

if __name__ == "__main__":
    pca_analizi()
