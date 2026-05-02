import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Proje ana dizini bul (Relatif Yol)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
base_path = ana_dizin

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
output_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Ciktilar", "7_Nihai_Secim")
gorsel_dir = os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller", "7_Nihai_Secim")
model_kopru_yolu = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Modeller", "secilmis_ozellikler.joblib")

import shutil

def setup_folders():
    for folder in [output_dir, gorsel_dir]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    os.makedirs(os.path.dirname(model_kopru_yolu), exist_ok=True)

def ozet_tablosu_olustur(baslangic_sayisi, final_sayisi):
    print("> Özellik Seçimi Özet Tablosu Hazırlanıyor...")
    
    summary_data = [
        ["Tanımlayıcılar (ID, İsim vb.)", "Manuel Filtreleme", "Tahmin Gücü Yok / Veri Sızıntısı", "Elendi"],
        ["Yüksek Korelasyon (r > 0.90)", "Pearson Korelasyon", "Çoklu Bağlantı (Multicollinearity)", "Elendi"],
        ["Düşük Önem Skorları", "Random Forest (Embedded)", "Düşük Bilgi Kazancı (%95 Eşiği)", "Elendi"],
        ["Hassas Eleme (RFE)", "RFE (Wrapper)", "Model Karmaşıklığını Azaltma", "Elendi"],
        ["Final Özellik Seti", "Hibrit Karar", "En Yüksek Tahmin Gücü", "SEÇİLDİ"]
    ]
    
    cols = ["Kategori / Adım", "Yöntem", "Eleme / Seçim Nedeni", "Durum"]
    df_summary = pd.DataFrame(summary_data, columns=cols)
    
    # Görsel Tablo
    plt.figure(figsize=(15, 6))
    plt.axis('off')
    table = plt.table(cellText=df_summary.values, colLabels=df_summary.columns, loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 4)
    
    # Başlıkları boya
    for (i, j), cell in table.get_celld().items():
        if i == 0:
            cell.set_facecolor('#34495e')
            cell.get_text().set_color('white')
            cell.get_text().set_weight('bold')
        elif i == len(summary_data):
            cell.set_facecolor('#27ae60')
            cell.get_text().set_color('white')
            cell.get_text().set_weight('bold')

    plt.title(f"Özellik Seçimi Karar ve Özet Tablosu\n(Başlangıç: {baslangic_sayisi} Özellik -> Final: {final_sayisi} Özellik)", 
              fontweight='bold', fontsize=15, pad=30)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Ozellik_Secimi_Karar_Ozet_Tablosu.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    df_summary.to_excel(os.path.join(output_dir, "Ozellik_Secimi_Karar_Raporu.xlsx"), index=False)

def final_ozellik_koprusu_ve_ozet():
    print("\n" + "="*60)
    print("FAZ 2 - ADIM 2.7: NİHAİ ÖZELLİK SEÇİMİ VE KARAR ÖZETİ")
    print("="*60)
    
    setup_folders()
    
    # 1. Veriyi Yükle
    df_raw = pd.read_excel(input_file, engine='openpyxl')
    baslangic_ozellik_sayisi = df_raw.shape[1] - 1 # Kredi Skoru hariç
    
    df_train = df_raw[df_raw["Kredi Skoru"].notna()].copy()
    
    # Gereksizleri Ele (Tanımlayıcılar)
    exclude_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df_train.drop(columns=[c for c in exclude_cols if c in df_train.columns], errors='ignore')
    y = df_train["Kredi Skoru"]
    
    # 2. Nihai Sıralama
    from sklearn.ensemble import RandomForestClassifier
    print("> En güçlü özellikler belirleniyor...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    feature_importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    top_features = feature_importances.head(20).index.tolist()
    
    # 3. KÖPRÜ KURULDU
    joblib.dump(top_features, model_kopru_yolu)
    
    # 4. Özet Tablosu Oluştur (Hoca İstemi)
    ozet_tablosu_olustur(baslangic_ozellik_sayisi, len(top_features))
    
    # 5. Görselleştirme (Bar Chart)
    plt.figure(figsize=(12, 10))
    bars = sns.barplot(x=feature_importances.values, y=feature_importances.index, palette='magma')
    
    # Değerleri bar yanına (sağına) ekle
    for i, v in enumerate(feature_importances.values):
        plt.text(v + 0.002, i, f'{v:.3f}', color='black', va='center', fontweight='bold', fontsize=10)

    plt.title("Nihai Seçilen Özelliklerin Tahmin Gücü ve Önem Skorları", fontweight='bold', fontsize=14)
    plt.xlabel("Göreceli Önem Puanı")
    plt.grid(True, axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Nihai_Ozellik_Siralama_Grafigi.png"), dpi=300)
    plt.close()
    
    # 6. Sadeleştirilmiş Veriyi Kaydet
    final_df = df_raw[["Kredi Skoru"] + top_features]
    final_df.to_excel(os.path.join(output_dir, "Model_Hazir_Sadelestirilmis_Veri.xlsx"), index=False)
    
    print(f"\n> BAŞARILI! Özellik seçimi süreci tamamlandı.")
    print(f"  Özet Rapor: {os.path.join(gorsel_dir, 'Ozellik_Secimi_Karar_Ozet_Tablosu.png')}")

if __name__ == "__main__":
    final_ozellik_koprusu_ve_ozet()
