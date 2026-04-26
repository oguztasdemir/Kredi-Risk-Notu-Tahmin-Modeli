import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "6_Final_Model_Egitimi")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "6_Final_Model", "champion_hybrid_final.joblib")

def setup_folders():
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

def gorselleri_olustur_final_5(model, X_val, y_val):
    print("> 5 Adet Final Görseli Hazırlanıyor...")
    plt.style.use('seaborn-v0_8-whitegrid')
    y_pred = model.predict(X_val)
    
    # 1. Tablo 9: Performans Metrikleri (Heatmap)
    report = classification_report(y_val, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_df = report_df.rename(index={
        '0': 'İyi (0)', '1': 'Standart (1)', '2': 'Kötü (2)',
        'accuracy': 'Doğruluk', 'macro avg': 'Makro Ort.', 'weighted avg': 'Ağırlıklı Ort.'
    }, columns={
        'precision': 'Hassasiyet', 'recall': 'Duyarlılık', 'f1-score': 'F1-Skoru', 'support': 'Destek'
    })
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(report_df.iloc[:3, :3], annot=True, cmap='YlGnBu', fmt='.3f', cbar=False)
    plt.title("Tablo 9: Şampiyon Model Nihai Performans Metrikleri", fontweight='bold', pad=20)
    plt.savefig(os.path.join(gorsel_dir, "Table_9_Metrikler.png"), dpi=300)

    # 2. Figür 6-1: Karmaşıklık Matrisi (Confusion Matrix)
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_val, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['İyi', 'Standart', 'Kötü'], 
                yticklabels=['İyi', 'Standart', 'Kötü'])
    plt.ylabel('Gerçek Değerler')
    plt.xlabel('Tahmin Edilenler')
    plt.title("Figür 6-1: Karmaşıklık Matrisi (Hata Analizi)", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_1_Confusion_Matrix.png"), dpi=300)

    # 3. Figür 6-2: Sınıf Bazlı Başarı Oranları
    plt.figure(figsize=(10, 6))
    class_acc = cm.diagonal() / cm.sum(axis=1)
    sns.barplot(x=['İyi (0)', 'Standart (1)', 'Kötü (2)'], y=class_acc, palette='viridis')
    plt.ylim(0, 1)
    for i, v in enumerate(class_acc):
        plt.text(i, v + 0.02, f"%{v*100:.1f}", ha='center', fontweight='bold')
    plt.title("Figür 6-2: Sınıf Bazlı Tahmin Başarı Oranları", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_2_Sinif_Basari.png"), dpi=300)

    # 4. Figür 6-3: Gerçek vs Tahmin Dağılımı (Pie/Donut)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    y_val.value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax1, colors=['#2ecc71', '#f1c40f', '#e74c3c'], labels=['İyi', 'Standart', 'Kötü'])
    ax1.set_title("Gerçek Dağılım")
    pd.Series(y_pred).value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax2, colors=['#2ecc71', '#f1c40f', '#e74c3c'], labels=['İyi', 'Standart', 'Kötü'])
    ax2.set_title("Modelin Tahmin Dağılımı")
    plt.suptitle("Figür 6-3: Gerçek ve Tahmin Edilen Kredi Skor Dağılımı", fontweight='bold', fontsize=14)
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_3_Dagilim_Kiyasi.png"), dpi=300)

    # 5. Figür 6-4: Şampiyon Model Kararlılık Analizi
    plt.figure(figsize=(10, 6))
    errors = np.abs(y_val - y_pred)
    sns.countplot(x=errors, palette='magma')
    plt.xticks([0, 1, 2], ['Tam İsabet (Hata: 0)', 'Yakın Tahmin (Hata: 1)', 'Uzak Tahmin (Hata: 2)'])
    plt.title("Figür 6-4: Tahmin Sapma ve Kararlılık Analizi", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_4_Kararlilik.png"), dpi=300)
    plt.close('all')

def final_training_refined_346():
    print("\n" + "="*60)
    print("ADIM 6: ŞAMPİYON MODEL FİNAL RAPORLAMA")
    print("="*60)

    setup_folders()

    df = pd.read_excel(input_file, engine='openpyxl')
    X = df.drop(columns=["İsim", "Kredi Skoru"])
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # AKILLI KONTROL
    mode = "1"
    if os.path.exists(model_path):
        print("\nBİLGİ: Şampiyon model dosyası bulundu.")
        print("[1] - Şampiyonu Yeniden Eğit")
        print("[2] - Mevcut Şampiyonu Kullan (Sadece 5 adet görseli güncelle)")
        mode = input("Seçiminiz: ").strip()

    if mode == "2":
        print("> Şampiyon model yükleniyor...")
        champion = joblib.load(model_path)
    else:
        print("> Şampiyon model eğitiliyor...")
        et_final = ExtraTreesClassifier(n_estimators=200, n_jobs=-1, random_state=42)
        rf_final = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
        xgb_final = XGBClassifier(n_estimators=100, learning_rate=0.1, eval_metric='mlogloss', random_state=42)
        champion = VotingClassifier(estimators=[('et', et_final), ('rf', rf_final), ('xgb', xgb_final)], voting='soft')
        champion.fit(X_train, y_train)
        joblib.dump(champion, model_path)

    gorselleri_olustur_final_5(champion, X_val, y_val)
    acc = accuracy_score(y_val, champion.predict(X_val))
    print(f"\nİŞLEM TAMAMLANDI! Şampiyon Doğruluk Oranı: %{acc*100:.2f}")

if __name__ == "__main__":
    final_training_refined_346()
