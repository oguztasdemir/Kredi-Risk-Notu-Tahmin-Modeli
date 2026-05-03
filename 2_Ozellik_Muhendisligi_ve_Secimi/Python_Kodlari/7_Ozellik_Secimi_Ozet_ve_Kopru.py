import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Proje ana dizini bul
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

def gorsel_olustur_adim2_7(feature_importances, baslangic_ozellik_sayisi, final_sayisi):
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2])
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.axis('off')
    summary_data = [
        ["Tanımlayıcılar", "Manuel Filtreleme", "Tahmin Gücü Yok", "Elendi"],
        ["Yüksek Korelasyon", "Pearson (r > 0.90)", "Çoklu Bağlantı", "Elendi"],
        ["Düşük Önem", "RF-Embedded", "%95 Bilgi Eşiği", "Elendi"],
        ["Hassas Eleme", "RFE (Wrapper)", "Boyut İndirgeme", "Elendi"],
        ["Final Özellik Seti", "Hibrit Karar", "En Yüksek Güç", "SEÇİLDİ"]
    ]
    cols = ["Adım", "Yöntem", "Neden", "Durum"]
    tab = ax1.table(cellText=summary_data, colLabels=cols, loc='center', cellLoc='left')
    tab.auto_set_font_size(False); tab.set_fontsize(10); tab.scale(1, 4)
    for (i, j), cell in tab.get_celld().items():
        if i == 0: cell.set_facecolor('#34495e'); cell.get_text().set_color('white')
        elif i == 5: cell.set_facecolor('#27ae60'); cell.get_text().set_color('white')
    ax1.set_title(f"Şekil 2.7.1: Karar Matrisi ({baslangic_ozellik_sayisi} -> {final_sayisi})", pad=20)

    ax2 = fig.add_subplot(gs[0, 1])
    sns.barplot(x=feature_importances.values, y=feature_importances.index, palette='magma', ax=ax2)
    ax2.set_title("Şekil 2.7.2: Nihai Seçilen Özelliklerin Önem Skorları", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_2_7_Nihai_Secim_Paneli.png"), dpi=300)
    plt.close()

def final_ozellik_koprusu_ve_ozet():
    print("\n" + "="*60)
    print("FAZ 2 - ADIM 2.7: NİHAİ ÖZELLİK SEÇİMİ VE KARAR ÖZETİ")
    print("="*60)
    
    setup_folders()
    df_raw = pd.read_excel(input_file, engine='openpyxl')
    baslangic_ozellik_sayisi = df_raw.shape[1] - 1
    df_train = df_raw[df_raw["Kredi Skoru"].notna()].copy()
    
    exclude_cols = ["ID", "Müşteri ID", "İsim", "Kimlik No", "Ay", "Kredi Skoru"]
    X = df_train.drop(columns=[c for c in exclude_cols if c in df_train.columns], errors='ignore')
    y = df_train["Kredi Skoru"]
    
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    
    feature_importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
    top_features = feature_importances.head(20).index.tolist()
    
    joblib.dump(top_features, model_kopru_yolu)
    gorsel_olustur_adim2_7(feature_importances, baslangic_ozellik_sayisi, len(top_features))
    
    final_df = df_raw[["Kredi Skoru"] + top_features]
    final_df.to_excel(os.path.join(output_dir, "Model_Hazir_Sadelestirilmis_Veri.xlsx"), index=False)
    print(f"\n> BAŞARILI! Özellik seçimi süreci tamamlandı.")

if __name__ == "__main__":
    final_ozellik_koprusu_ve_ozet()
