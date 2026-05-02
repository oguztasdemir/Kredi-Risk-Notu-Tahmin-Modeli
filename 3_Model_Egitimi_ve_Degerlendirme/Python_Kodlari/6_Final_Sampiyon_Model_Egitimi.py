import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import joblib
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score

# Proje ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Yollar
input_file = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "1_Veri_Hazirlik", "Egitim_Verisi_Dengelenmis.xlsx")
gorsel_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller", "6_Final_Model")
model_save_path = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "6_Uretim", "final_sampiyon_model.joblib")
hibrit_model_yolu = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "4_Hibrit_Model", "hibrit_stacking_model.joblib")

import shutil

def setup_folders():
    for folder in [gorsel_dir, os.path.dirname(model_save_path)]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def gorsel_karar_vericiler(model, X):
    print("> Karar Vericiler (Özellik Önem Sıralaması) Görselleştiriliyor...")
    # Stacking model için ilk basamağın ortalama önem skorlarını alalım
    # Not: Stacking modelde doğrudan feature_importances_ olmayabilir, bu yüzden ilk estimator'dan alıyoruz
    try:
        importance = model.estimators_[0].feature_importances_
        feature_names = X.columns
        
        feat_importances = pd.Series(importance, index=feature_names).sort_values(ascending=False).head(10)
        
        plt.figure(figsize=(12, 8))
        bars = sns.barplot(x=feat_importances.values, y=feat_importances.index, palette='viridis')
        
        # Değerleri bar yanına ekle
        for i, v in enumerate(feat_importances.values):
            plt.text(v + 0.001, i, f'{v:.4f}', color='black', va='center', fontweight='bold')

        plt.title("Model Kararını En Çok Etkileyen 10 Faktör", fontsize=15, fontweight='bold')
        plt.xlabel("Etki Puanı (Yüksek Daha Önemli)")
        plt.grid(True, axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "01_Karar_Verici_Faktorler.png"), dpi=300)
        plt.close()
    except:
        print("  - [UYARI] Özellik önem skorları bu model tipi için doğrudan alınamadı.")

def final_sampiyon_egitimi_pedagojik():
    """
    Bu final adımda, en iyi modelimizi 'üretime' hazır hale getiriyoruz.
    Ayrıca modelin hangi kriterlere göre 'İyi' veya 'Kötü' dediğini basitçe analiz ediyoruz.
    """
    print("\n" + "="*60)
    print("ADIM 3.6: NİHAİ MODEL VE KARAR ANALİZİ")
    print("="*60)

    setup_folders()

    # 1. Veri ve Model Yükleme
    if not os.path.exists(hibrit_model_yolu):
        print("HATA: Hibrit model dosyası bulunamadı!")
        return

    df = pd.read_excel(input_file)
    X = df.drop(columns=["Kredi Skoru"])
    y = df["Kredi Skoru"]
    
    model = joblib.load(hibrit_model_yolu)

    # 2. Final Başarı Analizi
    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', 
                xticklabels=['İyi', 'Standart', 'Kötü'],
                yticklabels=['İyi', 'Standart', 'Kötü'])
    plt.title("Final Tahmin Başarı Tablosu (Karmaşıklık Matrisi)", fontweight='bold')
    plt.ylabel('Gerçek Durum')
    plt.xlabel('Modelin Tahmini')
    plt.savefig(os.path.join(gorsel_dir, "02_Final_Basari_Matrisi.png"), dpi=300)
    plt.close()

    # 3. Model Neye Göre Karar Veriyor? (Özellik Önemi)
    gorsel_karar_vericiler(model, X)

    # 4. Üretim Modeli Olarak Kaydet (Sıkıştırılmış)
    if os.path.exists(model_save_path): os.remove(model_save_path)
    joblib.dump(model, model_save_path, compress=3)
    print(f"\n> TEBRİKLER! Şampiyon model üretime hazır (Sıkıştırılmış).")
    print(f"  Konum: {model_save_path}")

if __name__ == "__main__":
    final_sampiyon_egitimi_pedagojik()

