import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import mutual_info_classif
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestClassifier

# Proje ana dizini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

import shutil

# Yollar
input_file = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "1_Filtre_Metodu", "1_filter_sonrasi_veri.xlsx")
gorsel_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "6_Ozellik_Adli_Tip")

def setup_folders():
    for folder in [gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def adli_tip_dogrulama():
    print("\n" + "="*60)
    print("FAZ 2 - ADIM 2.6: ÖZELLİK ADLİ TIP DOĞRULAMA (MUTUAL INFO & PERMUTATION)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    df = pd.read_excel(input_file)
    df_train = df[df["Kredi Skoru"].notna()].copy()
    
    # Hız için örneklem
    sample_size = min(3000, len(df_train))
    df_sample = df_train.sample(n=sample_size, random_state=42)
    
    X = df_sample.drop(columns=["Kredi Skoru"])
    y = df_sample["Kredi Skoru"]

    # 2. Mutual Information
    print("> Mutual Information (Karşılıklı Bilgi) hesaplanıyor...")
    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)

    # 3. Permutation Importance
    print("> Permutation Importance hesaplanıyor (Bu işlem zaman alabilir)...")
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    perm_importance = permutation_importance(rf, X, y, n_repeats=5, random_state=42, n_jobs=-1)
    perm_series = pd.Series(perm_importance.importances_mean, index=X.columns).sort_values(ascending=False)

    # 4. Görselleştirme (Akademik Panel)
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    
    # 2.6.1 Mutual Info
    sns.barplot(x=mi_series.values, y=mi_series.index, ax=axes[0], palette="flare")
    axes[0].set_title("Şekil 2.6.1: Mutual Information (Bilgi Kazanımı)", pad=20)
    
    # 2.6.2 Permutation
    sns.barplot(x=perm_series.values, y=perm_series.index, ax=axes[1], palette="crest")
    axes[1].set_title("Şekil 2.6.2: Permutation Importance (Doğrulama)", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_2_6_Dogrulama_Paneli.png"), dpi=300)
    plt.close()

    print(f"\n> BAŞARILI! Özellik adli tıp analizi ve doğrulama tamamlandı.")

if __name__ == "__main__":
    adli_tip_dogrulama()
