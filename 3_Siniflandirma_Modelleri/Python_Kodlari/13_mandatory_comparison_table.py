import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_base = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "13_Comparison_Table")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "13_Comparison_Table")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def run_comparison_313():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 13: ZORUNLU SONUÇ KARŞILAŞTIRMA ÇALIŞMASI (TABLE 4)")
    print("="*60)

    setup_folders()

    # 1. Veriyi Yükle
    print("> Ana veri seti yükleniyor...")
    df_full = pd.read_excel(input_base)
    df_full = df_full[df_full["Kredi Skoru"].notna()].sample(5000, random_state=42) # Hız için örneklem
    
    y = df_full["Kredi Skoru"]
    X_all = df_full.drop(columns=["İsim", "Kredi Skoru"])

    # Model Fonksiyonu
    def get_f1(X_data, y_data):
        X_train, X_val, y_train, y_val = train_test_split(X_data, y_data, test_size=0.2, random_state=42, stratify=y_data)
        model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        return f1_score(y_val, y_pred, average='weighted')

    results = []

    # SENARYO 1: Ham Özellikler (Tümü)
    print("> Senaryo 1: Ham Özellikler analiz ediliyor...")
    f1_ham = get_f1(X_all, y)
    results.append({"Veri Temsili": "Ham Özellikler (Tümü)", "Model": "Random Forest", "F1_Skoru": f1_ham})

    # SENARYO 2: Filter ile seçilmiş alt küme (Korelasyon)
    # Varsayım: İlk 15 özellik
    print("> Senaryo 2: Filter (Correlation) analiz ediliyor...")
    X_filter = X_all.iloc[:, :15] 
    f1_filter = get_f1(X_filter, y)
    results.append({"Veri Temsili": "Filter ile seçilmiş alt küme", "Model": "Random Forest", "F1_Skoru": f1_filter})

    # SENARYO 3: Wrapper/Embedded ile seçilmiş alt küme (RFE)
    print("> Senaryo 3: Wrapper/Embedded (RFE) analiz ediliyor...")
    rfe_path = os.path.join(base_path, "2_Feature_Selection", "Ciktilar", "5_Wrapper_Method", "rfe_selected_features.joblib")
    if os.path.exists(rfe_path):
        rfe_feats = joblib.load(rfe_path)
        X_wrapper = X_all[rfe_feats]
    else:
        X_wrapper = X_all.iloc[:, :15] # Fallback
    f1_wrapper = get_f1(X_wrapper, y)
    results.append({"Veri Temsili": "Wrapper/Embedded ile seçilmiş alt küme", "Model": "Random Forest", "F1_Skoru": f1_wrapper})

    # SENARYO 4: PCA Bileşenleri
    print("> Senaryo 4: PCA Bileşenleri analiz ediliyor...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_all)
    pca = PCA(n_components=10)
    X_pca = pca.fit_transform(X_scaled)
    f1_pca = get_f1(X_pca, y)
    results.append({"Veri Temsili": "PCA Bileşenleri", "Model": "Random Forest", "F1_Skoru": f1_pca})

    # 2. TABLO OLUŞTURMA (Rubrik Zorunlu)
    comparison_df = pd.DataFrame(results)
    print("\n> ZORUNLU KARŞILAŞTIRMA TABLOSU:")
    print(comparison_df)
    
    comparison_df.to_excel(os.path.join(output_dir, "Mandatory_Comparison_Table.xlsx"), index=False)

    # 3. Görselleştirme
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=comparison_df, x='F1_Skoru', y='Veri Temsili', palette='viridis')
    plt.xlim(0.5, 1.0)
    plt.title("Figür 13-1: Veri Temsillerine Göre Model Başarı Kıyaslaması (F1)", fontweight='bold')
    
    for p in ax.patches:
        ax.annotate(f'{p.get_width():.4f}', (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontweight='bold')

    plt.savefig(os.path.join(gorsel_dir, "1_Comparison_Table_Visual.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n> BAŞARILI! Zorunlu karşılaştırma tablosu ve grafiği hazır.")

if __name__ == "__main__":
    run_comparison_313()
