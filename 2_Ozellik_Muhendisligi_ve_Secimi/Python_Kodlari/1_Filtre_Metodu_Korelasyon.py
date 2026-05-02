import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import shutil

# Global Görsel Standartları
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 14

D_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

I_FILE = os.path.join(D_PATH, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
O_DIR = os.path.join(D_PATH, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "1_Filtre_Metodu")
G_DIR = os.path.join(D_PATH, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "1_Filtre_Metodu")

def dizin_temizle():
    for f in [O_DIR, G_DIR]:
        if os.path.exists(f):
            shutil.rmtree(f)
        os.makedirs(f)

def korelasyon_analizi_premium():
    print("\n" + "="*70)
    print("FAZ 2 - ADIM 1: İSTATİSTİKSEL FİLTRELEME VE KORELASYON ANALİZİ")
    print("="*70)

    dizin_temizle()

    df = pd.read_excel(I_FILE, engine='openpyxl')
    
    # Predictif olmayan sütunların ayıklanması
    kısıtlı_sutunlar = ["ID", "Müşteri ID", "Kimlik No", "İsim", "Ay"]
    df = df.drop(columns=[c for c in kısıtlı_sutunlar if c in df.columns], errors='ignore')

    # Korelasyon Matrisi Hesaplama
    corr_matrix = df.corr()
    
    # Görselleştirme: Isı Haritası
    plt.figure(figsize=(20, 16))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=False, cmap="rocket_r", center=0, 
                linewidths=.8, cbar_kws={"shrink": .7, "label": "Pearson Katsayısı"})
    plt.title("Özellikler Arası Korelasyon Yapısı ve Çoklu Bağlantı Analizi", pad=30)
    plt.tight_layout()
    plt.savefig(os.path.join(G_DIR, "Global_Ozellik_Korelasyon_Isi_Haritasi.png"), dpi=300)

    # Hedef Değişken İlişkisi
    target_corr = corr_matrix["Kredi Skoru"].drop("Kredi Skoru").abs().sort_values(ascending=False)
    plt.figure(figsize=(12, 10))
    bars = sns.barplot(x=target_corr.values, y=target_corr.index, palette="mako")
    
    # Değerleri bar yanına (sağına) ekle
    for i, v in enumerate(target_corr.values):
        plt.text(v + 0.005, i, f'{v:.3f}', color='black', va='center', fontweight='bold', fontsize=10)

    plt.title("Özelliklerin Kredi Skoru Üzerindeki Etki Gücü (Korelasyon)", pad=20, fontsize=14, fontweight='bold')
    plt.xlabel("Mutlak Korelasyon Gücü (|r|)")
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(G_DIR, "Kredi_Skoru_Etki_Analizi_Pearson.png"), dpi=300)
    plt.close('all')

    # Yüksek Korelasyonlu Sütunların Elenmesi
    threshold = 0.90
    to_drop = set()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                to_drop.add(corr_matrix.columns[i])

    df_filtered = df.drop(columns=list(to_drop))
    df_filtered.to_excel(os.path.join(O_DIR, "1_filter_sonrasi_veri.xlsx"), index=False)
    
    print(f"> Analiz tamamlandı. {len(to_drop)} adet redundant sütun elendi.")
    print(f"> Raporlar ve görseller {G_DIR} dizinine aktarıldı.")

if __name__ == "__main__":
    korelasyon_analizi_premium()
