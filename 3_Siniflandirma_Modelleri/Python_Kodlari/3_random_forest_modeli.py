import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "3_Random_Forest")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "3_Random_Forest")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "3_Random_Forest", "random_forest_model.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

def gorsellestir(model, X_val, y_val):
    print("> Grafikler ve Raporlar Güncelleniyor...")
    y_pred = model.predict(X_val)
    
    # Feature Importance
    plt.figure(figsize=(10, 8))
    feats = pd.Series(model.feature_importances_, index=X_val.columns).sort_values(ascending=False).head(15)
    sns.barplot(x=feats.values, y=feats.index, palette='viridis')
    plt.title("Random Forest - Top 15 Feature Importance", fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_3_1_Importance.png"), dpi=300)
    plt.close('all')

def run_step_3():
    print("\n" + "="*50)
    print("ADIM 3: RANDOM FOREST MODELİ")
    print("="*50)
    
    setup_folders()
    
    df = pd.read_excel(input_file, engine='openpyxl')
    # Predictif olmayan sütunları çıkar
    drop_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df.drop(columns=drop_cols, errors='ignore')
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # AKILLI KONTROL (Otomatik Yeniden Eğitim)
    mode = "1"

    if mode == "2":
        print("> Mevcut model yükleniyor...")
        rf = joblib.load(model_path)
    else:
        print("> Model eğitiliyor (100k veri, lütfen bekleyin)...")
        rf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
        rf.fit(X_train, y_train)
        joblib.dump(rf, model_path)

    gorsellestir(rf, X_val, y_val)
    acc = accuracy_score(y_val, rf.predict(X_val))
    print(f"\nİŞLEM TAMAMLANDI! Başarı: %{acc*100:.2f}")

if __name__ == "__main__":
    run_step_3()
