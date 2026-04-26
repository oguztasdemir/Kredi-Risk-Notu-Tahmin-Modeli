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
test_file = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik", "Test_Datasi.xlsx")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "6_Final_Model", "champion_hybrid_final.joblib")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "7_Final_Tahminleme")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "7_Final_Tahminleme")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def run_final_inference_347():
    print("\n" + "="*60)
    print("ADIM 7: 50.000 KAYIT İÇİN NİHAİ TAHMİNLEME")
    print("="*60)

    setup_folders()

    # 1. Veri ve Model Yükleme
    if not os.path.exists(test_file):
        print(f"HATA: Test datası bulunamadı: {test_file}")
        return
    
    if not os.path.exists(model_path):
        print("HATA: Şampiyon model bulunamadı! Lütfen önce Adım 6'yı çalıştırın.")
        return

    print("> 50.000 kişilik test datası yükleniyor...")
    df_test = pd.read_excel(test_file, engine='openpyxl')
    
    print("> Şampiyon Hibrit Model yükleniyor...")
    champion = joblib.load(model_path)

    # 2. Tahminleme
    print("> Yapay zeka tahminleri gerçekleştiriyor (Lütfen bekleyin)...")
    X_test = df_test.drop(columns=["İsim", "Kredi Skoru"], errors='ignore')
    
    # Model eğitimi sırasında kullanılan sütun sırasını koruyalım
    predictions = champion.predict(X_test)
    
    # 3. Sonuçları Birleştirme ve Etiketleme
    results_df = df_test[["İsim"]].copy()
    results_df["Tahmin_Edilen_Skor"] = predictions
    
    # Map (İyi, Standart, Kötü)
    label_map = {0: "İyi", 1: "Standart", 2: "Kötü"}
    results_df["Tahmin_Etiketi"] = results_df["Tahmin_Edilen_Skor"].map(label_map)

    # 4. Kayıt
    output_path = os.path.join(output_dir, "50k_Final_Tahmin_Listesi.xlsx")
    results_df.to_excel(output_path, index=False)
    print(f"\n> BAŞARILI! 50.000 kişilik liste kaydedildi: {output_path}")

    # 5. Görselleştirme: Tahmin Dağılımı
    print("> Tahmin dağılım grafikleri hazırlanıyor...")
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=results_df, x='Tahmin_Etiketi', order=['İyi', 'Standart', 'Kötü'], palette=['#2ecc71', '#f1c40f', '#e74c3c'])
    plt.title("50.000 Kişilik Tahmin Havuzu Dağılımı", fontweight='bold', fontsize=14)
    
    # Değerleri yazdır
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontweight='bold')
    
    plt.savefig(os.path.join(gorsel_dir, "Figure_7_1_Tahmin_Dagilimi.png"), dpi=300)
    plt.close()

    print("\nTÜM SÜREÇ BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    run_final_inference_347()
