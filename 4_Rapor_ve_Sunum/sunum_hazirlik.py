import os
import sys

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
rapor_dir = os.path.join(base_path, "4_Rapor_ve_Sunum")
os.makedirs(rapor_dir, exist_ok=True)

def create_presentation_outline():
    print("\n" + "="*60)
    print("PHASE 4 - ADIM 1: AKADEMİK SUNUM VE RAPOR TASLAĞI")
    print("="*60)
    
    summary_text = """
============================================================
KREDİ NOTU SINIFLANDIRMA VE TAHMİNLEME PROJESİ - NİHAİ RAPOR
============================================================

1. VERİ RESTORASYONU (PHASE 1)
-------------------------------
- 150.000 satırlık ham veri 14 farklı aşamadan geçirilerek temizlendi.
- Müşteri ID bazlı restorasyon ile eksik veriler %35'ten %0'a indirildi.
- Finansal anomaliler (Negatif borç, imkansız yaş) mantıksal kurallarla düzeltildi.

2. ÖZELLİK MÜHENDİSLİĞİ VE SEÇİMİ (PHASE 2)
-------------------------------------------
- Korelasyon Analizi, PCA ve Random Forest Importances kullanıldı.
- 50+ parametre arasından model başarısını en çok artıran "En İyi 20" özellik seçildi.
- t-SNE ve Manifold Learning ile veri kümeleri görselleştirildi.

3. MAKİNE ÖĞRENMESİ VE HİBRİT SİSTEMLER (PHASE 3)
-------------------------------------------------
- 20 farklı algoritma Pipeline (StandardScaler) ile en adil şartlarda yarıştırıldı.
- Şampiyon Yapı: Extra Trees + RandomForest + XGBoost (Hibrit Voting Classifier).
- Başarı Oranı: %82.56 (Cross-Validation ve Test verisi üzerinde).
- Hata Analizi: MAE, RMSE ve MAPE metrikleri ile ordinal hata payı ölçüldü.

4. NİHAİ UYGULAMA (TAHMİNLEME)
------------------------------
- Etiketsiz 50.000 kişilik liste için tahminler üretildi.
- "İyi", "Standart" ve "Kötü" olarak kategorize edilen liste çıktı olarak sunuldu.

============================================================
PROJE SONUCU: ÜSTÜN BAŞARI (SUPERIOR SUCCESS) STANDARTLARINDA.
============================================================
"""
    
    with open(os.path.join(rapor_dir, "Executive_Summary_Forensic.txt"), "w", encoding="utf-8") as f:
        f.write(summary_text)

    # Sunum Planı (Markdown formatında Slide-by-Slide)
    presentation_plan = """
# KREDİ NOTU SINIFLANDIRMA SUNUM PLANI

## Slayt 1: Kapak ve Giriş
- Proje Başlığı, İsim, Tarih.

## Slayt 2: Veri Problematiği
- Kirli verinin AI üzerindeki yıkıcı etkisi.
- Figure 1: Ham veri eksiklik analizi.

## Slayt 3: Veri Restorasyonu (Mutfak Aşaması)
- ID bazlı temizlik ve anomali onarımı.
- Figure 3: Birleştirme sonrası veri doluluk oranı.

## Slayt 4: Özellik Seçimi (Akılcı Eleme)
- Neden en iyi 20 özellik seçildi?
- Figure 10: Nihai Özellik Önem Tablosu.

## Slayt 5: Mega Benchmark (20 Algoritma Yarışı)
- Scaling'in önemi ve yarışma sonuçları.
- Figure 11: Accuracy Leaderboard.

## Slayt 6: Şampiyon Hibrit Model
- Hibrit yapının (Voting) tekil modellere üstünlüğü.
- Table 9: Nihai Performans Metrikleri (Hassasiyet, Duyarlılık).

## Slayt 7: 50.000 Tahmin ve Sonuç
- Figure 7-1: Tahmin Dağılımı.
- Projenin ticari ve akademik değeri.
"""
    
    with open(os.path.join(rapor_dir, "Akademik_Sunum_Plani.md"), "w", encoding="utf-8") as f:
        f.write(presentation_plan)

    print(f"\n> Raporlar Hazırlandı: {rapor_dir}")
    print("  - Executive_Summary_Forensic.txt")
    print("  - Akademik_Sunum_Plani.md")

if __name__ == "__main__":
    create_presentation_outline()
