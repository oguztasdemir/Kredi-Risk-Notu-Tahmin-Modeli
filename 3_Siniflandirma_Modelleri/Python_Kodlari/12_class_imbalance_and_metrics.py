import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score, classification_report
from sklearn.preprocessing import label_binarize
from imblearn.over_sampling import SMOTE
import joblib

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "12_Imbalance_Metrics")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "12_Imbalance_Metrics")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def run_imbalance_analysis_312():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 12: SINIF DENGESİZLİĞİ (SMOTE) VE İLERİ METRİKLER (ROC/PR)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    print("> Veri yükleniyor...")
    df = pd.read_excel(input_file)
    df = df[df["Kredi Skoru"].notna()].copy()
    
    # KÖPRÜ: Adım 8'de seçilen temiz özellikleri yükle
    bridge_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "selected_features.joblib")
    if os.path.exists(bridge_path):
        selected_features = joblib.load(bridge_path)
        print(f"> KÖPRÜ BAĞLANTISI: Adım 8'den gelen {len(selected_features)} özellik seçildi.")
        X = df[selected_features]
    else:
        print("> UYARI: Özellik köprüsü bulunamadı, manuel eleme yapılıyor.")
        X = df.drop(columns=["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"], errors='ignore')
        
    y = df["Kredi Skoru"]
    classes = [0, 1, 2] # İyi, Standart, Kötü

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 2. SMOTE Uygulama (Rubrik Madde: Sınıf Dengelenmesi)
    print(f"> SMOTE uygulanıyor (Eski dağılım: {dict(pd.Series(y_train).value_counts())})...")
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
    print(f"  - Yeni dağılım: {dict(pd.Series(y_train_smote).value_counts())}")

    # 3. Model Eğitimi (Dengelenmiş veri ile)
    print("> Model (Random Forest) SMOTE'lu veri ile eğitiliyor...")
    model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    model.fit(X_train_smote, y_train_smote)
    
    y_score = model.predict_proba(X_val)
    y_val_bin = label_binarize(y_val, classes=classes)
    n_classes = y_val_bin.shape[1]

    # 4. ROC EĞRİLERİ (Rubrik Zorunlu)
    print("> ROC Eğrileri hazırlanıyor...")
    plt.figure(figsize=(10, 8))
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    colors = ['green', 'orange', 'red']
    labels = ['İyi', 'Standart', 'Kötü']

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_val_bin[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], color=colors[i], lw=2,
                 label=f'{labels[i]} (AUC = {roc_auc[i]:.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Figür 12-1: Multiclass ROC Eğrileri (SMOTE Sonrası)', fontweight='bold')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(gorsel_dir, "1_Multiclass_ROC_Curves.png"), dpi=300)
    plt.close()

    # 5. PRECISION-RECALL EĞRİLERİ (Rubrik Zorunlu)
    print("> Precision-Recall Eğrileri hazırlanıyor...")
    plt.figure(figsize=(10, 8))
    precision = dict()
    recall = dict()
    average_precision = dict()

    for i in range(n_classes):
        precision[i], recall[i], _ = precision_recall_curve(y_val_bin[:, i], y_score[:, i])
        average_precision[i] = average_precision_score(y_val_bin[:, i], y_score[:, i])
        plt.plot(recall[i], precision[i], color=colors[i], lw=2,
                 label=f'{labels[i]} (AP = {average_precision[i]:.2f})')

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Figür 12-2: Multiclass Precision-Recall Eğrileri', fontweight='bold')
    plt.legend(loc="lower left")
    plt.savefig(os.path.join(gorsel_dir, "2_Precision_Recall_Curves.png"), dpi=300)
    plt.close()

    print(f"\n> BAŞARILI! SMOTE analizi ve zorunlu grafikler (ROC/PR) hazır.")

if __name__ == "__main__":
    run_imbalance_analysis_312()
