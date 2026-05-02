import pandas as pd
import numpy as np
import os
import sys
import joblib
import shutil
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False

# Proje ana dizini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Ciktilar", "1_Veri_Hazirlik")
model_kopru_yolu = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "secilmis_ozellikler.joblib")

def setup_folders():
    for folder in [output_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def veri_hazirlik_ve_dengeleme():
    print("\n" + "="*60)
    print("FAZ 3 - ADIM 3.1: VERİ HAZIRLIK VE SINIF DENGELENME (SMOTE)")
    print("="*60)
    
    setup_folders()
    
    # 1. Veriyi Yükle
    print(f"> Veri yükleniyor: {os.path.basename(input_file)}")
    df = pd.read_excel(input_file, engine='openpyxl')
    
    # 2. Faz 2 Entegrasyonu
    if os.path.exists(model_kopru_yolu):
        print(f"> Faz 2'den gelen seçilmiş özellikler yükleniyor...")
        selected_features = joblib.load(model_kopru_yolu)
        final_cols = ["Kredi Skoru"] + [c for c in selected_features if c in df.columns]
        df = df[final_cols]
        print(f"> Başarılı: Sadece en predictive {len(selected_features)} özellik kullanılacak.")
    else:
        print("> UYARI: Özellik seçimi dosyası bulunamadı! Tüm sütunlar kullanılacak.")

    # 3. Eğitim ve Tahmin Havuzu Ayrımı
    train_data = df[df["Kredi Skoru"].notna()].copy()
    predict_pool = df[df["Kredi Skoru"].isna()].copy()
    
    # 4. SINIF DENGELENME (SMOTE)
    if SMOTE_AVAILABLE:
        print("> Sınıf dengesizliği kontrol ediliyor...")
        X_train_raw = train_data.drop(columns=["Kredi Skoru"])
        y_train_raw = train_data["Kredi Skoru"]
        
        counts_before = y_train_raw.value_counts()
        print(f"  - Orijinal Dağılım: {dict(counts_before)}")
        
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_train_raw, y_train_raw)
        
        counts_after = y_resampled.value_counts()
        train_data_balanced = pd.DataFrame(X_resampled, columns=X_train_raw.columns)
        train_data_balanced["Kredi Skoru"] = y_resampled
        
        print(f"  - SMOTE Sonrası Dağılım: {dict(counts_after)}")
        train_data = train_data_balanced

        # Görselleştirme: Dengeleme Öncesi ve Sonrası
        import matplotlib.pyplot as plt
        import seaborn as sns
        g_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller", "1_Veri_Hazirlik")
        os.makedirs(g_dir, exist_ok=True)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Öncesi
        ax1.pie(counts_before, labels=counts_before.index, autopct='%1.1f%%', colors=['#e74c3c', '#f1c40f', '#2ecc71'])
        ax1.set_title("1. Dengeleme ÖNCESİ (Dengesiz Dağılım)", fontweight='bold')
        
        # Sonrası
        ax2.pie(counts_after, labels=counts_after.index, autopct='%1.1f%%', colors=['#e74c3c', '#f1c40f', '#2ecc71'])
        ax2.set_title("2. Dengeleme SONRASI (SMOTE - Dengeli)", fontweight='bold')
        
        plt.suptitle("Akademik Veri Dengeleme Analizi", fontsize=16, fontweight='bold')
        
        # Not Ekle
        plt.text(0.5, 0.02, "Metot: SMOTE (Synthetic Minority Over-sampling Technique)\nAmaç: Modelin azınlık sınıfları daha iyi öğrenmesini sağlamak.", 
                 ha='center', transform=fig.transFigure, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

        plt.savefig(os.path.join(g_dir, "01_SMOTE_Dengeleme_Analizi.png"), dpi=300)
        plt.close()

        # Görselleştirme 2: Sayısal Karşılaştırma Tablosu
        plt.figure(figsize=(10, 4))
        plt.axis('off')
        balance_data = [
            ["Kredi Skoru", "Önce (Dengesiz)", "Sonra (Dengeli - SMOTE)"],
            ["Kötü", f"{dict(counts_before).get(2, 0)}", f"{dict(counts_after).get(2, 0)}"],
            ["Standart", f"{dict(counts_before).get(1, 0)}", f"{dict(counts_after).get(1, 0)}"],
            ["İyi", f"{dict(counts_before).get(0, 0)}", f"{dict(counts_after).get(0, 0)}"]
        ]
        
        table = plt.table(cellText=balance_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 3)
        
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#2980b9'); cell.get_text().set_color('white'); cell.get_text().set_weight('bold')

        plt.title("Sınıf Dengeleme Operasyonu Sayısal Özeti", fontweight='bold', fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig(os.path.join(g_dir, "02_SMOTE_Tablo_Ozeti.png"), dpi=300)
        plt.close()
    else:
        print("> BİLGİ: imbalanced-learn kütüphanesi yüklü değil, SMOTE atlandı.")

    # 5. Kayıt
    train_data.to_excel(os.path.join(output_dir, "Egitim_Verisi_Dengelenmis.xlsx"), index=False)
    predict_pool.to_excel(os.path.join(output_dir, "Tahmin_Havuzu_Etiketsiz.xlsx"), index=False)
    
    print(f"\n> İŞLEM TAMAMLANDI!")
    print(f"  - Dengelenmiş Eğitim Verisi: {len(train_data)} Satır")
    print(f"  - Tahmin Havuzu: {len(predict_pool)} Satır")

if __name__ == "__main__":
    veri_hazirlik_ve_dengeleme()
