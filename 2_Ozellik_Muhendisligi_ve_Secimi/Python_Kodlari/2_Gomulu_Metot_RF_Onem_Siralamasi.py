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
    
    # Akademik Panel Oluşturma
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2)
    
    # 2.2.1 Özellik Önemi
    ax1 = fig.add_subplot(gs[:, 0])
    sns.barplot(x=importances.values, y=importances.index, palette="viridis", ax=ax1)
    for i, v in enumerate(importances.values):
        ax1.text(v + 0.001, i, f'{v:.4f}', color='black', va='center', fontweight='bold', fontsize=9)
    ax1.set_title("Şekil 2.2.1: Özelliklerin Tahmin Gücü ve Gini Önem Katsayıları", pad=20)
    ax1.set_xlabel("Gini Önem Skoru")

    # 2.2.2 Kümülatif Önem
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(range(1, len(cum_sum) + 1), cum_sum, marker='o', linestyle='-', color='#34495e', linewidth=2)
    ax2.axhline(y=0.95, color='#e74c3c', linestyle='--', label='%95 Eşik Değeri')
    ax2.set_title("Şekil 2.2.2: Kümülatif Özellik Önemi ve Bilgi Birikimi", pad=20)
    ax2.set_xlabel("Özellik Sayısı")
    ax2.set_ylabel("Kümülatif Önem Skoru")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 2.2.3 Özet Bilgi Tablosu
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis('off')
    sum_data = [
        ["Metrik", "Değer"],
        ["Toplam Özellik", len(importances)],
        ["Seçilen Özellik (%95)", num_selected],
        ["Elenen Özellik", len(importances) - num_selected],
        ["Model", "RandomForest (n=100)"]
    ]
    tab = ax3.table(cellText=sum_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 3)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        else: cell.set_facecolor('#f8f9fa')
    ax3.set_title("Tablo 2.2: Özellik Seçimi Stratejik Özeti")

    plt.tight_layout()
    plt.savefig(os.path.join(G_DIR, "Adim_2_2_RF_Onem_Paneli.png"), dpi=300)
    plt.close()

    df_selected = df[list(top_features) + ["Kredi Skoru"]]
    df_selected.to_excel(os.path.join(O_DIR, "2_embedded_sonrasi_veri.xlsx"), index=False)
    
    print(f"> Bilginin %95'ini temsil eden {num_selected} özellik seçildi.")

if __name__ == "__main__":
    gomulu_metot_analizi_premium()
