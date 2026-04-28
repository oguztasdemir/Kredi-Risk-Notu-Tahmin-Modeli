import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# UMAP opsiyonel, hata verirse atlayacak şekilde kurgulayalım
UMAP_AVAILABLE = False
try:
    import umap
    UMAP_AVAILABLE = True
except Exception as e:
    print(f"BİLGİ: UMAP kütüphanesi yüklenirken hata oluştu veya kurulu değil. ({e})")

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "6_Advanced_Manifold")

def setup_folders():
    os.makedirs(gorsel_dir, exist_ok=True)

def advanced_manifold_analysis_246():
    print("\n" + "="*60)
    print("PHASE 2 - ADIM 6: İLERİ SEVİYE MANIFOLD ANALİZİ (t-SNE & UMAP)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme ve Örnekleme
    print("> Veri yükleniyor...")
    df = pd.read_excel(input_file)
    
    # Sadece etiketli veriyi kullan
    df = df[df["Kredi Skoru"].notna()].copy()
    
    df_sample = df.sample(n=2000, random_state=42)
    
    X = df_sample.drop(columns=["İsim", "Kredi Skoru"])
    y = df_sample["Kredi Skoru"]
    
    # Ölçeklendirme (Manifold için şart)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. t-SNE PERPLEXITY KARŞILAŞTIRMASI (Rubrik Zorunlu: 15, 30, 50)
    print("> t-SNE Perplexity karşılaştırması yapılıyor {15, 30, 50}...")
    perplexities = [15, 30, 50]
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    for i, p in enumerate(perplexities):
        print(f"  - t-SNE Perplexity={p} hesaplanıyor...")
        tsne = TSNE(n_components=2, perplexity=p, random_state=42)
        X_tsne = tsne.fit_transform(X_scaled)
        
        scatter = axes[i].scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='viridis', alpha=0.6, s=30)
        axes[i].set_title(f"t-SNE (Perplexity={p})", fontweight='bold')
        
    plt.colorbar(scatter, ax=axes[2], label='Kredi Skoru')
    plt.suptitle("Figür 2-6-1: t-SNE Perplexity Parametresinin Kümeleme Üzerindeki Etkisi", fontsize=16, fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "1_tSNE_Perplexity_Comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. UMAP ANALİZİ (Rubrik Zorunlu)
    if UMAP_AVAILABLE:
        try:
            print("\n> UMAP analizi yapılıyor (n_neighbors=15, min_dist=0.1)...")
            reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
            X_umap = reducer.fit_transform(X_scaled)
            
            plt.figure(figsize=(10, 8))
            plt.scatter(X_umap[:, 0], X_umap[:, 1], c=y, cmap='viridis', alpha=0.6, s=30)
            plt.title("Figür 2-6-2: UMAP Manifold Görselleştirmesi", fontweight='bold', fontsize=14)
            plt.colorbar(label='Kredi Skoru')
            plt.savefig(os.path.join(gorsel_dir, "2_UMAP_Visualization.png"), dpi=300, bbox_inches='tight')
            plt.close()
            print("  - UMAP görseli kaydedildi.")
        except Exception as e:
            print(f"  - UMAP hatası (Görsel oluşturulamadı): {e}")
    else:
        print("\n> BİLGİ: umap-learn kütüphanesi yüklü değil, UMAP adımı atlandı.")

    print(f"\n> BAŞARILI! Manifold analizleri tamamlandı.")

if __name__ == "__main__":
    advanced_manifold_analysis_246()
