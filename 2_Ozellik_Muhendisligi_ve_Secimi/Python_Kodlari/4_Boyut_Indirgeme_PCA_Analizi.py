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
    
    # Akademik Panel Oluşturma
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(1, 2)
    
    # 2.4.1 Scree Plot
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(range(1, 11), exp_var_ratio[:10], alpha=0.5, align='center', label='Bireysel Varyans')
    ax1.step(range(1, 11), cum_var_ratio[:10], where='mid', label='Kümülatif Varyans', color='red')
    ax1.axhline(y=0.90, color='r', linestyle='--', alpha=0.3)
    ax1.set_title("Şekil 2.4.1: İlk 10 PCA Bileşeni Varyans Oranları (Scree Plot)", pad=20)
    ax1.set_xlabel("Temel Bileşen İndeksi")
    ax1.set_ylabel("Açıklanan Varyans Oranı")
    ax1.legend(loc='best')

    # 2.4.2 2D Projeksiyon
    ax2 = fig.add_subplot(gs[0, 1])
    X_pca = pca.transform(X_scaled)
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=y, palette='viridis', alpha=0.6, ax=ax2)
    ax2.set_title("Şekil 2.4.2: Verilerin 2D PCA Düzlemindeki İz düşümü", pad=20)
    ax2.set_xlabel("PC1 (En Yüksek Varyans)")
    ax2.set_ylabel("PC2 (İkinci Yüksek Varyans)")

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_2_4_PCA_Analiz_Paneli.png"), dpi=300)
    plt.close()

    # 4. Kayıt
    pca_results = pd.DataFrame(pca.transform(X_scaled)[:, :n_components_90], 
                               columns=[f"PC{i+1}" for i in range(n_components_90)])
    pca_results.to_excel(os.path.join(output_dir, "4_pca_sonrasi_veri.xlsx"), index=False)

    print(f"\n> BAŞARILI! PCA analizi tamamlandı.")

if __name__ == "__main__":
    pca_analizi()
