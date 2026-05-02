import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
from sklearn.ensemble import RandomForestClassifier

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.titleweight'] = 'bold'

D_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

I_FILE = os.path.join(D_PATH, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "1_Filtre_Metodu", "1_filter_sonrasi_veri.xlsx")
O_DIR = os.path.join(D_PATH, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "2_Gomulu_Metot")
G_DIR = os.path.join(D_PATH, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "2_Gomulu_Metot")

def dizin_temizle():
    for f in [O_DIR, G_DIR]:
        if os.path.exists(f):
            shutil.rmtree(f)
        os.makedirs(f)

def gomulu_metot_analizi_premium():
    print("\n" + "="*70)
    print("FAZ 2 - ADIM 2: GÖMÜLÜ METOTLAR (RANDOM FOREST IMPORTANCE)")
    print("="*70)

    dizin_temizle()

    df = pd.read_excel(I_FILE, engine='openpyxl')
    df_train = df[df["Kredi Skoru"].notna()]
    X = df_train.drop(columns=["Kredi Skoru"])
    y = df_train["Kredi Skoru"]

    print("> Rastgele Orman algoritması ile özellik önem skorları hesaplanıyor...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)

    importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    cum_sum = np.cumsum(importances.values)

    # %95 bilgi korunumu hedefi
    num_selected = np.searchsorted(cum_sum, 0.95) + 1
    top_features = importances.index[:num_selected]
    
    # Görselleştirme: Özellik Önemi
    plt.figure(figsize=(14, 12))
    bars = sns.barplot(x=importances.values, y=importances.index, palette="viridis")
    
    # Değerleri bar yanına (sağına) ekle
    for i, v in enumerate(importances.values):
        plt.text(v + 0.001, i, f'{v:.4f}', color='black', va='center', fontweight='bold', fontsize=10)

    plt.title("Özelliklerin Tahmin Gücü ve Gini Önem Katsayıları", pad=20, fontsize=15, fontweight='bold')
    plt.xlabel("Gini Önem Skoru")
    plt.tight_layout()
    plt.savefig(os.path.join(G_DIR, "Ozellik_Onem_Siralamasi_RF.png"), dpi=300)

    # Kümülatif Önem Grafiği
    plt.figure(figsize=(12, 8))
    plt.plot(range(1, len(cum_sum) + 1), cum_sum, marker='o', linestyle='-', color='#34495e', linewidth=2)
    plt.axhline(y=0.95, color='#e74c3c', linestyle='--', label='%95 Eşik Değeri')
    plt.title("Kümülatif Özellik Önemi ve Bilgi Birikimi", pad=20)
    plt.xlabel("Özellik Sayısı")
    plt.ylabel("Kümülatif Önem Skoru")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(G_DIR, "Kumulatif_Bilgi_Kazanci_Grafigi.png"), dpi=300)
    plt.close('all')

    df_selected = df[list(top_features) + ["Kredi Skoru"]]
    df_selected.to_excel(os.path.join(O_DIR, "2_embedded_sonrasi_veri.xlsx"), index=False)
    
    print(f"> Bilginin %95'ini temsil eden {num_selected} özellik seçildi.")

if __name__ == "__main__":
    gomulu_metot_analizi_premium()
