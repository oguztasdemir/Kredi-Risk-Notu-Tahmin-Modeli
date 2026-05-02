import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

# Proje ana dizinini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Yollar
input_file = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "2_Gomulu_Metot", "2_embedded_sonrasi_veri.xlsx")
output_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "3_Wrapper_Metodu")
gorsel_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "3_Wrapper_Metodu")

import shutil

def setup_folders():
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def rfe_analizi():
    print("\n" + "="*60)
    print("FAZ 2 - ADIM 2.3: WRAPPER METHOD - RFE (RECURSIVE FEATURE ELIMINATION)")
    print("="*60)

    setup_folders()

    # 1. Veri Yükleme
    print("> Filtrelenmiş veri yükleniyor...")
    df = pd.read_excel(input_file)
    df_train = df[df["Kredi Skoru"].notna()].copy()
    
    # Hız için örneklem alalım
    sample_size = min(5000, len(df_train))
    df_sample = df_train.sample(n=sample_size, random_state=42)
    
    X = df_sample.drop(columns=["Kredi Skoru"])
    y = df_sample["Kredi Skoru"]

    print(f"> Örneklem Boyutu: {len(X)} | Başlangıç Özellik Sayısı: {X.shape[1]}")

    # 2. RFE Uygulama
    print("> RFE süreci başlatılıyor (Hassas özellik eleme)...")
    estimator = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    selector = RFE(estimator, n_features_to_select=15, step=2)
    selector = selector.fit(X, y)

    # 3. Sonuçları Çıkar
    selected_features = X.columns[selector.support_].tolist()
    ranking = pd.DataFrame({'Ozellik': X.columns, 'Siralama': selector.ranking_}).sort_values('Siralama')

    print(f"\n> SEÇİLEN EN İYİ 15 ÖZELLİK (RFE):")
    for i, feat in enumerate(selected_features, 1):
        print(f"  {i}. {feat}")

    # 4. Kayıt
    ranking.to_excel(os.path.join(output_dir, "RFE_Ozellik_Siralamasi.xlsx"), index=False)
    df[selected_features + ["Kredi Skoru"]].to_excel(os.path.join(output_dir, "3_wrapper_sonrasi_veri.xlsx"), index=False)
    joblib.dump(selected_features, os.path.join(output_dir, "3_wrapper_secilmis_ozellikler.joblib"))
    
    # 5. Görselleştirme
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 10))
    bars = sns.barplot(data=ranking, x='Siralama', y='Ozellik', palette='mako')
    
    # Sıralama numaralarını bar yanına (sağına) ekle
    for i, v in enumerate(ranking['Siralama']):
        plt.text(v + 0.1, i, f'#{v}', color='black', va='center', fontweight='bold', fontsize=10)

    plt.title("RFE (Recursive Feature Elimination) Özellik Sıralaması", fontweight='bold', fontsize=14)
    plt.xlabel("Öncelik Sıralaması (1: En Önemli)")
    plt.savefig(os.path.join(gorsel_dir, "Figure_5_RFE_Siralamasi.png"), dpi=300)
    plt.close()

    # Figure 6: RFE Seçim Özeti (Pie)
    plt.figure(figsize=(8, 8))
    labels_pie = ['Seçilen (VIP)', 'Elenen (Gürültü)']
    sizes_pie = [len(selected_features), X.shape[1] - len(selected_features)]
    plt.pie(sizes_pie, labels=labels_pie, autopct='%1.1f%%', colors=['#27ae60', '#95a5a6'], startangle=140, explode=(0.1, 0))
    plt.title("RFE Süreci: Özellik Eleme Oranı", fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Figure_6_RFE_Secim_Ozeti.png"), dpi=300)
    plt.close()

    print(f"\n> BAŞARILI! RFE sonuçları kaydedildi.")

if __name__ == "__main__":
    rfe_analizi()
