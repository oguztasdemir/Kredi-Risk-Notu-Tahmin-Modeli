import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "2_Karar_Agaci")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "2_Karar_Agaci")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "2_Karar_Agaci", "decision_tree_model.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

def gorsellestir(model, X_val, y_val):
    print("> Grafikler ve Raporlar Güncelleniyor...")
    y_pred = model.predict(X_val)
    
    # 1. Karmaşıklık Matrisi
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_val, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title("Decision Tree - Confusion Matrix", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_2_1_Confusion_Matrix.png"), dpi=300)
    
    # 2. Önem Dereceleri
    plt.figure(figsize=(10, 6))
    importances = pd.Series(model.feature_importances_, index=X_val.columns).sort_values(ascending=False).head(10)
    importances.plot(kind='barh', color='teal')
    plt.title("Decision Tree - Top 10 Feature Importance", fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_2_2_Feature_Importance.png"), dpi=300)
    plt.close('all')

def run_step_2():
    print("\n" + "="*50)
    print("ADIM 2: KARAR AĞACI MODELİ")
    print("="*50)
    
    setup_folders()
    
    # Veriyi yükle
    df = pd.read_excel(input_file, engine='openpyxl')
    X = df.drop(columns=["İsim", "Kredi Skoru"])
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # AKILLI KONTROL
    mode = "1" # Varsayılan: Eğit
    if os.path.exists(model_path):
        print("\nBİLGİ: Mevcut bir model dosyası bulundu.")
        print("[1] - Yeniden Eğit (Modeli sil ve sıfırdan başla)")
        print("[2] - Mevcut Modeli Kullan (Sadece grafikleri güncelle)")
        mode = input("Seçiminiz: ").strip()

    if mode == "2":
        print("> Mevcut model yükleniyor...")
        clf = joblib.load(model_path)
    else:
        print("> Model eğitiliyor (Bu işlem biraz zaman alabilir)...")
        clf = DecisionTreeClassifier(max_depth=10, random_state=42)
        clf.fit(X_train, y_train)
        joblib.dump(clf, model_path)
        print(f"> Model kaydedildi: {model_path}")

    # Her durumda grafikleri güncelle
    gorsellestir(clf, X_val, y_val)
    
    acc = accuracy_score(y_val, clf.predict(X_val))
    print(f"\nİŞLEM TAMAMLANDI! Başarı: %{acc*100:.2f}")

if __name__ == "__main__":
    run_step_2()
