import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "8_Final_Secim")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "8_Final_Secim")
model_bridge_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "selected_features.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_bridge_path), exist_ok=True)

def final_feature_selection_bridge():
    print("\n" + "="*60)
    print("PHASE 2 - ADIM 8: NİHAİ ÖZELLİK SEÇİMİ VE ENTEGRASYON KÖPRÜSÜ")
    print("="*60)
    
    setup_folders()
    
    df = pd.read_excel(input_file, engine='openpyxl')
    # Sadece etiketli verileri kullan (Y içinde NaN olmamalı)
    df = df[df["Kredi Skoru"].notna()].copy()
    
    # Predictif olmayan (sadece kimlik belirten) sütunları ve hedef değişkeni çıkar
    drop_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df.drop(columns=drop_cols, errors='ignore')
    y = df["Kredi Skoru"]
    
    # 1. En İyi Özellikleri Belirle (Random Forest Tabanlı Önem Sırası)
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    feature_importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    
    # En iyi 20 Özelliği Seçelim
    top_20_features = feature_importances.head(20).index.tolist()
    
    print(f"\n> Analiz Tamamlandı. En Etkili 20 Özellik Belirlendi:")
    for i, feat in enumerate(top_20_features, 1):
        print(f"  {i}. {feat}")
    
    # 2. ENTEGRASYON: Seçilen Özellikleri Kaydet (Phase 3 burayı okuyacak)
    joblib.dump(top_20_features, model_bridge_path)
    print(f"\n> KÖPRÜ KURULDU: Seçilen özellikler şuraya kaydedildi: {model_bridge_path}")
    
    # 3. Görselleştirme: Nihai Önem Tablosu
    plt.figure(figsize=(12, 10))
    sns.barplot(x=feature_importances.head(20).values, y=feature_importances.head(20).index, palette='magma')
    plt.title("Figure 10: Nihai Model İçin Seçilen En Önemli 20 Özellik", fontweight='bold', fontsize=14)
    plt.xlabel("Göreceli Önem Puanı")
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_10_Final_Features.png"), dpi=300)
    
    # 4. Veri Setini Sadeleştir ve Kaydet
    final_df = df[["İsim", "Kredi Skoru"] + top_20_features]
    final_df.to_excel(os.path.join(output_dir, "model_hazir_sade_veri.xlsx"), index=False)
    print(f"> Sadeleştirilmiş model verisi kaydedildi: {output_dir}")

if __name__ == "__main__":
    final_feature_selection_bridge()
