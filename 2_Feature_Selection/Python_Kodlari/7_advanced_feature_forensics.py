import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.feature_selection import mutual_info_classif

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "7_Advanced_Forensics")
os.makedirs(gorsel_dir, exist_ok=True)

def advanced_forensics():
    print("\n" + "="*60)
    print("PHASE 2 - ADIM 7: İLERİ SEVİYE ÖZELLİK ADLİ ANALİZİ (FORENSICS)")
    print("="*60)
    
    df = pd.read_excel(input_file)
    # Sadece etiketli verileri (Kredi Skoru olanları) kullan
    df = df[df["Kredi Skoru"].notna()].sample(min(2000, len(df[df["Kredi Skoru"].notna()])), random_state=42)
    
    X = df.drop(columns=["İsim", "Kredi Skoru"], errors='ignore')
    y = df["Kredi Skoru"]
    
    # 1. Mutual Information (Doğrusal Olmayan İlişkiler)
    print("> Mutual Information hesaplanıyor...")
    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    
    # 2. Permutation Importance (Modelden Bağımsız Önem)
    print("> Permutation Importance hesaplanıyor (Bu işlem zaman alabilir)...")
    rf = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    perm_importance = permutation_importance(rf, X, y, n_repeats=5, random_state=42)
    perm_series = pd.Series(perm_importance.importances_mean, index=X.columns).sort_values(ascending=False)
    
    # GÖRSELLEŞTİRME
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # MI Plot
    sns.barplot(x=mi_series.head(15).values, y=mi_series.head(15).index, ax=ax1, palette="flare")
    ax1.set_title("1. Mutual Information (Bilgi Kazancı)", fontsize=14, fontweight='bold', color='#e74c3c')
    
    # Permutation Plot
    sns.barplot(x=perm_series.head(15).values, y=perm_series.head(15).index, ax=ax2, palette="crest")
    ax2.set_title("2. Permutation Importance (Model Kararlılığı)", fontsize=14, fontweight='bold', color='#2ecc71')
    
    plt.suptitle("İLERİ SEVİYE ÖZELLİK SEÇİMİ VE DOĞRULAMA MATRİSİ", fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Advanced_Feature_Forensics.png"), dpi=300)
    plt.close()
    
    print(f"\n> İleri seviye analiz tamamlandı! Görsel kaydedildi: {gorsel_dir}")

if __name__ == "__main__":
    advanced_forensics()
