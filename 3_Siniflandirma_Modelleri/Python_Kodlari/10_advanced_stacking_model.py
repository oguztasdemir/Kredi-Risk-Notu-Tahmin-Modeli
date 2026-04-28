import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, StackingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Datasi.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "10_Stacking_Model")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "10_Stacking_Model")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "10_Stacking_Model", "champion_stacking_final.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

def gorsellestirme_gelismis_3410(model, X_val, y_val, y_pred, acc, f1):
    print("> Gelişmiş görselleştirmeler hazırlanıyor...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Karmaşıklık Matrisi (Normalize edilmiş ve Renkli)
    plt.figure(figsize=(10, 8))
    cm = confusion_matrix(y_val, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['İyi', 'Standart', 'Kötü'],
                yticklabels=['İyi', 'Standart', 'Kötü'],
                annot_kws={"size": 14, "weight": "bold"})
    
    for i in range(len(cm)):
        for j in range(len(cm[0])):
            plt.text(j+0.5, i+0.7, f"({cm_norm[i, j]*100:.1f}%)", 
                     ha='center', va='center', color='black', fontsize=10)

    plt.title(f"Figür 10-1: Stacking Model Karmaşıklık Matrisi\nGenel Doğruluk: %{acc*100:.2f}", fontweight='bold', fontsize=15, pad=20)
    plt.ylabel('Gerçek Değerler', fontweight='bold')
    plt.xlabel('Tahmin Edilenler', fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "Figure_10_1_Confusion_Matrix.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Sınıf Bazlı Başarı Bar Grafiği
    report = classification_report(y_val, y_pred, output_dict=True)
    classes = ['0', '1', '2']
    class_names = ['İyi', 'Standart', 'Kötü']
    metrics = ['precision', 'recall', 'f1-score']
    
    data = []
    for cls in classes:
        for metric in metrics:
            data.append({
                'Sınıf': class_names[int(cls)],
                'Metrik': metric.capitalize(),
                'Skor': report[cls][metric]
            })
    
    metric_df = pd.DataFrame(data)
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=metric_df, x='Sınıf', y='Skor', hue='Metrik', palette='viridis')
    plt.ylim(0, 1.1)
    plt.title("Figür 10-2: Sınıf Bazlı Performans Metrikleri", fontweight='bold', fontsize=14)
    
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontweight='bold')
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(os.path.join(gorsel_dir, "Figure_10_2_Class_Metrics.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Model Katkıları (Meta-Model Katsayıları - FIX)
    try:
        meta_lr = model.final_estimator_
        coefs = np.abs(meta_lr.coef_) 
        
        n_models = 3
        n_classes = 3
        
        model_contributions = []
        model_names = ['Extra Trees', 'Random Forest', 'XGBoost']
        
        for i in range(n_models):
            start_idx = i * n_classes
            end_idx = start_idx + n_classes
            model_importance = np.mean(coefs[:, start_idx:end_idx])
            model_contributions.append(model_importance)
            
        plt.figure(figsize=(10, 6))
        colors = ['#2c3e50', '#2980b9', '#16a085']
        sns.barplot(x=model_names, y=model_contributions, palette=colors)
        plt.title("Figür 10-3: Meta-Model Kararlarında Baz Modellerin Etki Ağırlığı", fontweight='bold', fontsize=14)
        plt.ylabel("Katsayı Şiddeti (Önem)")
        plt.savefig(os.path.join(gorsel_dir, "Figure_10_3_Model_Contributions.png"), dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"  Katkı grafiği hatası: {e}")

    # 4. Tahmin Dağılımı Kıyaslaması (Pie Charts)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    colors = ['#2ecc71', '#f1c40f', '#e74c3c']
    labels = ['İyi', 'Standart', 'Kötü']
    
    y_val.value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax1, colors=colors, labels=labels, startangle=140)
    ax1.set_title("Gerçek Sınıf Dağılımı", fontweight='bold')
    ax1.set_ylabel('')
    
    pd.Series(y_pred).value_counts().sort_index().plot(kind='pie', autopct='%1.1f%%', ax=ax2, colors=colors, labels=labels, startangle=140)
    ax2.set_title("Modelin Tahmin Dağılımı", fontweight='bold')
    ax2.set_ylabel('')
    
    plt.suptitle("Figür 10-4: Gerçek vs Tahmin Edilen Kredi Skor Dağılımı", fontweight='bold', fontsize=16)
    plt.savefig(os.path.join(gorsel_dir, "Figure_10_4_Distribution_Comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

def create_advanced_stacking_3410():
    print("\n" + "="*60)
    print("ADIM 10: ADVANCED STACKING (İSTİFLEME) MİMARİSİ")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    if not os.path.exists(input_file):
        print(f"HATA: Giriş dosyası bulunamadı: {input_file}")
        return

    print("> Veri yükleniyor...")
    df = pd.read_excel(input_file)
    
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
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 2. Seçenek Sun (Yeni özellikler için zorunlu eğitim)
    mode = "1" 
    if not os.path.exists(model_path):
        mode = "1"
        print("> Mevcut model bulunamadı. Eğitim başlatılacak.")
    else:
        print("\n[1] - Modeli Yeniden Eğit")
        print("[2] - Mevcut Modeli Kullan (Görselleştirmeleri Güncelle)")
        # mode = input("Seçiminiz [2]: ").strip() or "2"

    if mode == "1":
        print("\n> Baz modeller (Level 0) hazırlanıyor...")
        et_base = ExtraTreesClassifier(n_estimators=300, max_depth=35, min_samples_leaf=2, max_features='sqrt', n_jobs=-1, random_state=42)
        rf_base = RandomForestClassifier(n_estimators=300, max_depth=35, min_samples_leaf=2, max_features='sqrt', n_jobs=-1, random_state=42)
        xgb_base = XGBClassifier(n_estimators=500, max_depth=9, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric='mlogloss', n_jobs=-1, random_state=42)

        print("> Meta-Model (Level 1) olarak Logistic Regression atanıyor...")
        estimators = [('et', et_base), ('rf', rf_base), ('xgb', xgb_base)]
        stack_model = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(), cv=5, n_jobs=-1)

        print("\n> Stacking model eğitiliyor (Bu işlem vakit alabilir)...")
        start_time = time.time()
        stack_model.fit(X_train, y_train)
        duration = time.time() - start_time
        joblib.dump(stack_model, model_path)
        print(f"> Eğitim tamamlandı! Süre: {duration/60:.2f} dakika")
    else:
        print("\n> Mevcut model yükleniyor...")
        stack_model = joblib.load(model_path)
        duration = 0

    print("> Performans analizi yapılıyor...")
    y_pred = stack_model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, average='weighted')

    print(f"  Final Accuracy: %{acc*100:.2f}")
    print(f"  Final F1-Score: %{f1*100:.2f}")

    report = classification_report(y_val, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()
    report_df.to_excel(os.path.join(output_dir, "Stacking_Performance_Report.xlsx"))

    gorsellestirme_gelismis_3410(stack_model, X_val, y_val, y_pred, acc, f1)

    print(f"\n> İŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    create_advanced_stacking_3410()
