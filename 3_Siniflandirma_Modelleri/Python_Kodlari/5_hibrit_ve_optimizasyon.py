import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time
from itertools import combinations
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
selected_models_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "4_Mega_Benchmark", "selected_top_11_models.joblib")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "5_Hibrit_ve_Optimizasyon")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "5_Hibrit_ve_Optimizasyon")
audit_file = os.path.join(output_dir, "hybrid_audit_11c3.xlsx")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def gorsellestir(res_df):
    print("> Hibrit Görseller Güncelleniyor...")
    # Top 20
    plt.figure(figsize=(12, 10))
    sns.barplot(data=res_df.head(20), x='Accuracy', y='Combo', palette='viridis')
    plt.title("Figure 14-A: Top 20 Hybrids", fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_14_A_Top20_Hybrid.png"), dpi=300)
    plt.close('all')

def mega_hybrid_refined_11c3():
    print("\n" + "="*60)
    print("ADIM 5: 11 ŞAMPİYON İLE HİBRİT ARAMA (11C3)")
    print("="*60)

    setup_folders()

    # AKILLI KONTROL
    mode = "1"
    if os.path.exists(audit_file):
        print("\nBİLGİ: Mevcut hibrit tarama sonuçları bulundu.")
        print("[1] - Taramayı Yeniden Yap (Uzun sürer)")
        print("[2] - Mevcut Verileri Kullan (Sadece görselleri güncelle)")
        mode = input("Seçiminiz: ").strip()

    if mode == "2":
        res_df = pd.read_excel(audit_file)
        gorsellestir(res_df)
        print("\nİŞLEM TAMAMLANDI! Mevcut veriler üzerinden görseller güncellendi.")
        return

    # 1. Veri Yükle
    df = pd.read_excel(input_file, engine='openpyxl')
    df_sample = df.sample(n=5000, random_state=42)
    X = df_sample.drop(columns=["İsim", "Kredi Skoru"])
    y = df_sample["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    top_11_models = joblib.load(selected_models_file)
    all_combos = list(combinations(top_11_models, 3))
    
    print(f"\n> 165 kombinasyon taranıyor...")
    results = []
    for idx, combo in enumerate(all_combos, 1):
        names = [c[0] for c in combo]
        models = [(c[0], c[1]) for c in combo]
        vc = VotingClassifier(estimators=models, voting='hard')
        vc.fit(X_train, y_train)
        acc = accuracy_score(y_val, vc.predict(X_val))
        results.append({'Combo': "-".join(names), 'Accuracy': acc})

    res_df = pd.DataFrame(results).sort_values(by="Accuracy", ascending=False)
    res_df.to_excel(audit_file, index=False)
    gorsellestir(res_df)
    print(f"\nİŞLEM TAMAMLANDI! En İyi Hibrit: {res_df.iloc[0]['Combo']}")

if __name__ == "__main__":
    mega_hybrid_refined_11c3()
