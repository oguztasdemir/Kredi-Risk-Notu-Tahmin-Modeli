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
    
    # Akademik Panel Oluşturma
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1])
    
    # 2.1.1 Isı Haritası
    ax1 = fig.add_subplot(gs[0, 0])
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=False, cmap="rocket_r", center=0, 
                linewidths=.5, cbar_kws={"shrink": .5, "label": "Pearson Katsayısı"}, ax=ax1)
    ax1.set_title("Şekil 2.1.1: Özellikler Arası Global Korelasyon Matrisi", pad=20)

    # 2.1.2 Hedef Değişken İlişkisi
    ax2 = fig.add_subplot(gs[0, 1])
    target_corr = corr_matrix["Kredi Skoru"].drop("Kredi Skoru").abs().sort_values(ascending=False)
    sns.barplot(x=target_corr.values, y=target_corr.index, palette="mako", ax=ax2)
    
    for i, v in enumerate(target_corr.values):
        ax2.text(v + 0.005, i, f'{v:.3f}', color='black', va='center', fontweight='bold', fontsize=9)

    ax2.set_title("Şekil 2.1.2: Özelliklerin Hedef Değişken (Kredi Skoru) Üzerindeki Etkisi", pad=20)
    ax2.set_xlabel("Mutlak Korelasyon Gücü (|r|)")
    ax2.grid(True, axis='x', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(G_DIR, "Adim_2_1_Korelasyon_Paneli.png"), dpi=300)
    plt.close()

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
