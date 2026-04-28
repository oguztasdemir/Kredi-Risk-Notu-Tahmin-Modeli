import pandas as pd
import numpy as np
import os
import sys
import joblib
from sklearn.model_selection import train_test_split

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "1_Veri_Hazirlik")
model_bridge_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "selected_features.joblib")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)

def integrated_data_prep_341():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 1: ENTEGRE VERİ HAZIRLIK VE BÖLME")
    print("="*60)
    
    setup_folders()
    
    # 1. Veriyi Yükle
    print(f"> Veri yükleniyor: {input_file}")
    df = pd.read_excel(input_file, engine='openpyxl')
    
    # 2. ENTEGRASYON KONTROLÜ: Seçilen özellikleri oku
    if os.path.exists(model_bridge_path):
        print(f"> Özellik Seçimi (Phase 2) sonuçları yükleniyor...")
        selected_features = joblib.load(model_bridge_path)
        # Sadece Seçilen Özellikler + Kredi Skoru (İsim, ID vb. atıldı)
        final_cols = ["Kredi Skoru"] + [c for c in selected_features if c in df.columns and c not in ["İsim", "Kredi Skoru", "ID", "Müşteri ID", "Kimlik No", "Ay"]]
        df = df[[c for c in final_cols if c in df.columns]]
        print(f"> BAŞARILI: Model eğitimi sadece seçilen özellikler üzerinden yapılacak.")
    else:
        print("> UYARI: Özellik seçimi dosyası bulunamadı! Tüm sütunlar kullanılacak.")

    # 3. Eğitim ve Tahmin Havuzu Olarak Böl
    train_data = df[df["Kredi Skoru"].notna()].copy()
    test_data = df[df["Kredi Skoru"].isna()].copy()
    
    # 4. Dosyaları Kaydet
    train_data.to_excel(os.path.join(output_dir, "Egitim_Datasi.xlsx"), index=False)
    test_data.to_excel(os.path.join(output_dir, "Test_Datasi.xlsx"), index=False)
    
    print(f"\n> İşlem Tamamlandı!")
    print(f"  - Eğitim Verisi (Etiketli): {len(train_data)} Satır")
    print(f"  - Tahmin Havuzu (Etiketsiz): {len(test_data)} Satır")

if __name__ == "__main__":
    integrated_data_prep_341()
