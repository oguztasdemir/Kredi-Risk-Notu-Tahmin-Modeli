import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

# Imports moved inside function for safety
UMAP_AVAILABLE = False
TSNE_AVAILABLE = False

# Proje ana dizini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

import shutil

# Yollar
input_file = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "1_Filtre_Metodu", "1_filter_sonrasi_veri.xlsx")
gorsel_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "5_Manifold_Ogrenme")

def setup_folders():
    for folder in [gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def manifold_gorsellestirme():
    global UMAP_AVAILABLE, TSNE_AVAILABLE
    try:
        # Dinamik Importlar
        try:
            import umap
            UMAP_AVAILABLE = True
        except: UMAP_AVAILABLE = False
        
        try:
            from sklearn.manifold import TSNE
            TSNE_AVAILABLE = True
        except: TSNE_AVAILABLE = False

        print("\n" + "="*60)
        print("FAZ 2 - ADIM 2.5: MANIFOLD ÖĞRENME VE KÜMELENME ANALİZİ (UMAP & t-SNE)")
        print("="*60)

        setup_folders()

        # 1. Veri Yükleme ve Hazırlık
        print("> Veriler yükleniyor ve ölçeklendiriliyor...")
        df = pd.read_excel(input_file)
        df_train = df[df["Kredi Skoru"].notna()].copy()
        
        # Hız ve görsel netlik için örneklem
        sample_size = min(2000, len(df_train))
        df_sample = df_train.sample(n=sample_size, random_state=42)
        
        X = df_sample.drop(columns=["Kredi Skoru"])
        y = df_sample["Kredi Skoru"]
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Akademik Panel Oluşturma (UMAP & t-SNE Karşılaştırmalı Analiz)
        if UMAP_AVAILABLE or TSNE_AVAILABLE:
            fig = plt.figure(figsize=(24, 16))
            gs = fig.add_gridspec(2, 3)
            
            # 1. t-SNE Perplexity Karşılaştırması (Zorunlu: 15, 30, 50)
            if TSNE_AVAILABLE:
                perplexities = [15, 30, 50]
                for i, p in enumerate(perplexities):
                    print(f"> t-SNE uygulanıyor (Perplexity={p})...")
                    tsne = TSNE(n_components=2, perplexity=p, random_state=42, init='pca', learning_rate='auto')
                    X_tsne = tsne.fit_transform(X_scaled)
                    ax = fig.add_subplot(gs[0, i])
                    sns.scatterplot(x=X_tsne[:, 0], y=X_tsne[:, 1], hue=y, palette='viridis', alpha=0.6, s=40, ax=ax)
                    ax.set_title(f"t-SNE (Perplexity={p})", fontsize=14, fontweight='bold')
            
            # 2. UMAP Parametre Karşılaştırması (n_neighbors ve min_dist)
            if UMAP_AVAILABLE:
                # Farklı kombinasyonlar
                umap_params = [
                    {'n_neighbors': 5, 'min_dist': 0.01, 'title': 'UMAP (Local: n=5, d=0.01)'},
                    {'n_neighbors': 15, 'min_dist': 0.1, 'title': 'UMAP (Default: n=15, d=0.1)'},
                    {'n_neighbors': 50, 'min_dist': 0.5, 'title': 'UMAP (Global: n=50, d=0.5)'}
                ]
                for i, p in enumerate(umap_params):
                    print(f"> UMAP uygulanıyor ({p['title']})...")
                    reducer = umap.UMAP(n_neighbors=p['n_neighbors'], min_dist=p['min_dist'], n_components=2, random_state=42)
                    X_umap = reducer.fit_transform(X_scaled)
                    ax = fig.add_subplot(gs[1, i])
                    sns.scatterplot(x=X_umap[:, 0], y=X_umap[:, 1], hue=y, palette='rocket', alpha=0.6, s=40, ax=ax)
                    ax.set_title(p['title'], fontsize=14, fontweight='bold')

            plt.suptitle("Şekil 2.5: Manifold Öğrenme Hiperparametre Karşılaştırması\n(t-SNE Perplexity ve UMAP n_neighbors/min_dist Analizi)", 
                         fontsize=20, fontweight='bold', y=0.98)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            output_path = os.path.join(gorsel_dir, "Adim_2_5_Manifold_Analiz_Paneli.png")
            plt.savefig(output_path, dpi=300)
            plt.close()

        print(f"\n> Manifold öğrenme süreci tamamlandı. Görseller: {gorsel_dir}")
    except Exception as total_e:
        print(f"\n> [KRİTİK UYARI] Manifold adımı sistem hatası nedeniyle atlandı: {total_e}")

if __name__ == "__main__":
    manifold_gorsellestirme()
