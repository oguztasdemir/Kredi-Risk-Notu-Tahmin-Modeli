import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "5_Wrapper_Method")
gorsel_dir = os.path.join(base_path, "2_Feature_Selection", "Gorseller", "5_Wrapper_Method")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def run_rfe_analysis_245():
    print("\n" + "="*60)
    print("PHASE 2 - ADIM 5: WRAPPER METHOD - RECURSIVE FEATURE ELIMINATION (RFE)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    print("> Veri yükleniyor...")
    df = pd.read_excel(input_file)
    
    # Sadece etiketli veriyi (Eğitim seti) kullan
    df = df[df["Kredi Skoru"].notna()].copy()
    
    # 100k satır çok yavaşlatır, RFE için örneklem alalım
    df_sample = df.sample(n=5000, random_state=42)
    X = df_sample.drop(columns=["İsim", "Kredi Skoru"])
    y = df_sample["Kredi Skoru"]

    print(f"> Örneklem Boyutu: {len(X)} | Başlangıç Özellik Sayısı: {X.shape[1]}")

    # 2. RFE Uygulama (Random Forest Estimator ile)
    print("> RFE süreci başlatılıyor (Adım adım özellik eleniyor)...")
    estimator = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    
    # Hedef: En önemli 15 özelliği seçmek (Rubrik en az 15 sütun diyor)
    selector = RFE(estimator, n_features_to_select=15, step=2)
    selector = selector.fit(X, y)

    # 3. Sonuçları Çıkar
    selected_features = X.columns[selector.support_].tolist()
    ranking = pd.DataFrame({'Özellik': X.columns, 'Sıralama': selector.ranking_}).sort_values('Sıralama')

    print(f"\n> SEÇİLEN EN İYİ 15 ÖZELLİK (RFE):")
    for i, feat in enumerate(selected_features, 1):
        print(f"  {i}. {feat}")

    # 4. Kaydet
    ranking.to_excel(os.path.join(output_dir, "RFE_Feature_Ranking.xlsx"), index=False)
    joblib.dump(selected_features, os.path.join(output_dir, "rfe_selected_features.joblib"))

    # 5. Görselleştirme: Özellik Sıralaması (Top 20)
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 8))
    sns.barplot(data=ranking.head(20), x='Sıralama', y='Özellik', palette='mako')
    plt.title("RFE (Recursive Feature Elimination) Özellik Sıralaması\n(Düşük Sıralama = Daha Önemli)", fontweight='bold')
    plt.savefig(os.path.join(gorsel_dir, "1_RFE_Ranking_Top_20.png"), dpi=300)
    plt.close()

    print(f"\n> BAŞARILI! RFE sonuçları kaydedildi.")

if __name__ == "__main__":
    run_rfe_analysis_245()
