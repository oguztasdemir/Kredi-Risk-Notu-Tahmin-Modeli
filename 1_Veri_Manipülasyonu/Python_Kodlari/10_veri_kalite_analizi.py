import pandas as pd
import numpy as np
import os
import sys
import time
import shutil

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "9_Anomali_Duzeltme", "final_temiz_veri_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "10_Veri_Kalite_Analizi")

if not os.path.exists(output_dir): os.makedirs(output_dir)

output_file = os.path.join(output_dir, "final_kalite_ve_ml_hazirlik_raporu.xlsx")

def analiz_adim10_v4():
    print("\n" + "="*50)
    print("ADIM 10: FORENSIC INTELLIGENCE AUDIT (V4)")
    print("="*50)
    
    print("> Final veri seti yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')
    
    kalite_ozeti = []
    
    for col in df.columns:
        total = len(df)
        null_count = df[col].isna().sum()
        fill_rate = round(((total - null_count) / total) * 100, 2)
        unique_count = df[col].nunique()
        
        # V4 MANTIK: Koşullu Doluluk (Conditional Completeness)
        if col == "Kredi Türü":
            # Kredisi olmayanlar için türün boş olması bir hata değil, doğrudur.
            logical_nulls = ((df["Kredi Sayısı"] == 0) & (df[col].isna())).sum()
            error_nulls = null_count - logical_nulls
            # Gerçek kalite puanı: (Toplam - Gerçek Hata) / Toplam
            forensic_fill_rate = round(((total - error_nulls) / total) * 100, 2)
            puan = forensic_fill_rate
            durum = "HAZIR (KOŞULLU)" if forensic_fill_rate > 95 else "İNCELENMELİ"
            fill_rate = forensic_fill_rate # Rapor için güncelle
        elif col == "Kredi Skoru":
            puan = 100 if fill_rate >= 65 else (fill_rate * 1.5)
            durum = "HAZIR (HEDEF DEĞİŞKEN)"
        else:
            puan = (fill_rate * 0.6) + (40 if fill_rate > 99 else 10)
            durum = "HAZIR" if puan >= 95 else "İNCELENMELİ"
            
        kalite_ozeti.append({
            "Sütun Adı": col,
            "Doluluk/Sağlık (%)": fill_rate,
            "Benzersiz Değer": unique_count,
            "Kalite Puanı": round(puan, 2),
            "Durum": durum
        })

    pd.DataFrame(kalite_ozeti).to_excel(output_file, index=False)
    print(f"\nİŞLEM TAMAMLANDI! Rapor: {output_file}")

if __name__ == "__main__":
    analiz_adim10_v4()
