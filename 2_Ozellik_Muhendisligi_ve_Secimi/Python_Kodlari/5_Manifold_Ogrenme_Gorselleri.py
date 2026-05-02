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

        # 2. UMAP Analizi (Eğer yüklüyse)
        if UMAP_AVAILABLE:
            try:
                print("> UMAP Boyut İndirgeme uygulanıyor...")
                reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
                X_umap = reducer.fit_transform(X_scaled)
                
                plt.figure(figsize=(12, 8))
                sns.scatterplot(x=X_umap[:, 0], y=X_umap[:, 1], hue=y, palette='rocket', alpha=0.7, s=60, edgecolor='w')
                plt.title("UMAP: Kredi Skoru Sınıflarının 2D Manifold Dağılım Analizi", fontsize=15, fontweight='bold')
                plt.xlabel("UMAP Bileşeni 1")
                plt.ylabel("UMAP Bileşeni 2")
                plt.legend(title="Kredi Skoru (0:İyi, 1:Standart, 2:Kötü)", bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, linestyle='--', alpha=0.3)
                
                # Not Ekle
                plt.text(0.5, -0.15, "Analiz Amacı: Veri setindeki sınıfların (İyi/Kötü) manifold uzayında ne kadar ayrıştığını gözlemlemek.\nKümeler arasındaki boşluklar, modelin tahmin başarısının temelini oluşturur.", 
                         ha='center', transform=plt.gca().transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'))

                plt.tight_layout()
                filename = "UMAP_Kredi_Skoru_Kumelenme_Analizi.png"
                plt.savefig(os.path.join(gorsel_dir, filename), dpi=300)
                plt.close()
                print(f"  - [BAŞARILI] {filename} oluşturuldu.")
            except Exception as e:
                print(f"> UYARI: UMAP çalışırken bir hata oluştu: {e}")
        else:
            print("> BİLGİ: umap-learn kütüphanesi bulunamadı, UMAP atlandı.")

        # 3. t-SNE Analizi
        if TSNE_AVAILABLE:
            try:
                print("> t-SNE Boyut İndirgeme uygulanıyor...")
                tsne = TSNE(n_components=2, perplexity=30, random_state=42, init='pca', learning_rate='auto')
                X_tsne = tsne.fit_transform(X_scaled)
                
                plt.figure(figsize=(12, 8))
                sns.scatterplot(x=X_tsne[:, 0], y=X_tsne[:, 1], hue=y, palette='viridis', alpha=0.7, s=60, edgecolor='w')
                plt.title("t-SNE: Kredi Skoru Sınıflarının Olasılıksal Komşuluk Dağılımı", fontsize=15, fontweight='bold')
                plt.xlabel("t-SNE Boyutu 1")
                plt.ylabel("t-SNE Boyutu 2")
                plt.legend(title="Kredi Skoru", bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, linestyle='--', alpha=0.3)

                # Not Ekle
                plt.text(0.5, -0.15, "Analiz Amacı: Yüksek boyutlu veriyi 2 boyuta indirgeyerek sınıf yoğunluklarını denetlemek.\nKomşuluk ilişkileri, benzer finansal profillerin bir araya toplandığını gösterir.", 
                         ha='center', transform=plt.gca().transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'))

                plt.tight_layout()
                filename = "tSNE_Kredi_Skoru_Yogunluk_Haritasi.png"
                plt.savefig(os.path.join(gorsel_dir, filename), dpi=300)
                plt.close()
                print(f"  - [BAŞARILI] {filename} oluşturuldu.")
            except Exception as e:
                print(f"> UYARI: t-SNE çalışırken bir hata oluştu: {e}")

        print(f"\n> Manifold öğrenme süreci tamamlandı. Görseller: {gorsel_dir}")
    except Exception as total_e:
        print(f"\n> [KRİTİK UYARI] Manifold adımı sistem hatası nedeniyle atlandı: {total_e}")

if __name__ == "__main__":
    manifold_gorsellestirme()
