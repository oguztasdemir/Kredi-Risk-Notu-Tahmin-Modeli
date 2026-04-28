import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import StandardScaler

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "11_SVM_Model")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "11_SVM_Model")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "11_SVM_Kernel", "svm_model.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

def train_svm_model_311():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 11: KERNEL-BASED MODEL (SVM)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    print("> Veri yükleniyor...")
    df = pd.read_excel(input_file)
    df = df[df["Kredi Skoru"].notna()].copy()
    
    # SVM çok yavaş olduğu için rubrik temsili adına 10k örneklem alalım
    df_sample = df.sample(n=10000, random_state=42)
    # KÖPRÜ: Adım 8'de seçilen temiz özellikleri yükle
    bridge_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "selected_features.joblib")
    if os.path.exists(bridge_path):
        selected_features = joblib.load(bridge_path)
        print(f"> KÖPRÜ BAĞLANTISI: Adım 8'den gelen {len(selected_features)} özellik seçildi.")
        X = df_sample[selected_features]
    else:
        print("> UYARI: Özellik köprüsü bulunamadı, manuel eleme yapılıyor.")
        X = df_sample.drop(columns=["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"], errors='ignore')
        
    y = df_sample["Kredi Skoru"]

    # SVM için Standardizasyon Şarttır
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_val, y_train, y_val = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    # 2. Model Eğitimi (RBF Kernel)
    print(f"> SVM (Kernel=RBF) eğitiliyor (Örneklem: {len(X_train)} satır)...")
    start_time = time.time()
    svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)
    duration = time.time() - start_time
    print(f"> Eğitim tamamlandı! Süre: {duration:.2f} saniye")

    # 3. Değerlendirme
    y_pred = svm_model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average='weighted')

    print(f"  Accuracy: %{acc*100:.2f}")
    print(f"  F1-Score: %{f1*100:.2f}")

    # 4. Kayıt
    joblib.dump(svm_model, model_path)
    
    report = classification_report(y_val, y_pred, output_dict=True)
    pd.DataFrame(report).transpose().to_excel(os.path.join(output_dir, "SVM_Performance_Report.xlsx"))

    # 5. Görselleştirme
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_val, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='viridis', 
                xticklabels=['İyi', 'Standart', 'Kötü'],
                yticklabels=['İyi', 'Standart', 'Kötü'])
    plt.title(f"Adım 11: SVM (Kernel) Confusion Matrix\nAccuracy: %{acc*100:.2f}", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "1_SVM_Confusion_Matrix.png"), dpi=300)
    plt.close()

    print(f"\n> BAŞARILI! SVM modeli ve raporları hazır.")

if __name__ == "__main__":
    train_svm_model_311()
