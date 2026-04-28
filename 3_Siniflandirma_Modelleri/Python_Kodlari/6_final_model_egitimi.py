import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
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

def gorselleri_olustur_final_5(model, X_train, y_train, X_val, y_val):
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
    bars = plt.bar(['İyi (0)', 'Standart (1)', 'Kötü (2)'], class_acc, color=['#2ecc71','#f1c40f','#e74c3c'])
    plt.ylim(0, 1)
    for i, v in enumerate(class_acc):
        plt.text(i, v + 0.02, f"%{v*100:.1f}", ha='center', fontweight='bold')
    plt.title("Figür 6-2: Sınıf Bazlı Tahmin Başarı Oranları", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_2_Sinif_Basari.png"), dpi=300)

    # 4. Figür 6-3: Gerçek vs Tahmin Dağılımı
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    y_val.value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax1,
                                            colors=['#2ecc71', '#f1c40f', '#e74c3c'], labels=['İyi', 'Standart', 'Kötü'])
    ax1.set_title("Gerçek Dağılım")
    pd.Series(y_pred).value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax2,
                                                        colors=['#2ecc71', '#f1c40f', '#e74c3c'], labels=['İyi', 'Standart', 'Kötü'])
    ax2.set_title("Modelin Tahmin Dağılımı")
    plt.suptitle("Figür 6-3: Gerçek ve Tahmin Edilen Kredi Skor Dağılımı", fontweight='bold', fontsize=14)
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_3_Dagilim_Kiyasi.png"), dpi=300)

    # 5. Figür 6-4: Feature Importance (En güçlü sub-model üzerinden)
    try:
        # VotingClassifier içindeki RF modelini al
        rf_model = model.named_estimators_['rf']
        feature_names = X_train.columns.tolist()
        importances = pd.Series(rf_model.feature_importances_, index=feature_names).sort_values(ascending=True).tail(12)
        plt.figure(figsize=(10, 7))
        importances.plot(kind='barh', color='#2c3e50')
        plt.title("Figür 6-4: En Önemli 12 Özellik (Random Forest Tabanlı)", fontweight='bold')
        plt.xlabel("Önem Skoru")
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "Figure_6_4_Feature_Importance.png"), dpi=300)
    except Exception as e:
        print(f"  Feature importance atlandı: {e}")

    plt.close('all')
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_val, y_pred)
    print(f"\n  Eğitim Doğruluğu : %{train_acc*100:.2f}")
    print(f"  Test Doğruluğu   : %{test_acc*100:.2f}")
    print(f"  Fark (Overfit)   : %{(train_acc-test_acc)*100:.2f}")

def final_training_refined_346():
    print("\n" + "="*60)
    print("ADIM 6: ŞAMPİYON HİBRİT MODEL – DENGELI REGÜLARİZASYON")
    print("="*60)

    setup_folders()

    df = pd.read_excel(input_file, engine='openpyxl')
    # Predictif olmayan sütunları çıkar
    drop_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df.drop(columns=drop_cols, errors='ignore')
    y = df["Kredi Skoru"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("> Şampiyon model DENGELI REGÜLARİZASYON ile eğitiliyor...")
    print("  Hedef: Egitim ~%86-88, Test ~%82-85 (Fark: <%5 => Overfit Yok)")

    # DENGELİ REGÜLARIZASYON:
    # - max_depth=20 (çok derin değil ama çok kısıtlı da değil)
    # - min_samples_leaf=2 (aşırı serbest değil, ama veriyi iyi öğreniyor)
    # - max_features='sqrt' (dallanmada rastgelelik → genelleme artar)
    # Bu parametreler hem ezberlemeyi engeller hem de yüksek doğruluğu korur
    et_final = ExtraTreesClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=2,
        max_features='sqrt',
        n_jobs=-1,
        random_state=42
    )
    rf_final = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_leaf=2,
        max_features='sqrt',
        n_jobs=-1,
        random_state=42
    )
    xgb_final = XGBClassifier(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric='mlogloss',
        n_jobs=-1,
        random_state=42
    )

    champion = VotingClassifier(
        estimators=[('et', et_final), ('rf', rf_final), ('xgb', xgb_final)],
        voting='soft'
    )
    champion.fit(X_train, y_train)
    joblib.dump(champion, model_path)

    gorselleri_olustur_final_5(champion, X_train, y_train, X_val, y_val)
    test_acc = accuracy_score(y_val, champion.predict(X_val))
    print(f"\nİŞLEM TAMAMLANDI! Final Test Doğruluğu: %{test_acc*100:.2f}")

if __name__ == "__main__":
    final_training_refined_346()
