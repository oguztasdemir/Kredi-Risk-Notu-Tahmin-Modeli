import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.decomposition import PCA
import os

def gorsel_olustur_adim_3_11():
    # Klasör yolları
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"> Base Path: {base_path}")
    print(f"> Dir list: {os.listdir(base_path)}")
    veri_yolu = None
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if "ml_hazir_sayisal_veri.xlsx" in file:
                veri_yolu = os.path.join(root, file)
                break
        if veri_yolu: break
        
    if not veri_yolu:
        print(f"> HATA: Veri dosyası (xlsx) bulunamadı!")
        return
    
    # Excel'den yükle
    df = pd.read_excel(veri_yolu)
    
    # Sütun isimlerini temizle (sadece string olanları ve ascii dışı karakterleri atlayarak)
    new_cols = []
    for col in df.columns:
        if isinstance(col, str):
            # Basit temizlik
            new_cols.append(col.encode('ascii', 'ignore').decode('ascii'))
        else:
            new_cols.append(str(col))
    df.columns = new_cols
    
    # Kredi Skoru kolonunu bul (içinde 'Kredi' ve 'Skor' geçen)
    target_col = None
    for col in df.columns:
        if "Kredi" in col and "Skor" in col:
            target_col = col
            break
    if not target_col: target_col = df.columns[-1] # Varsayılan son kolon
    
    X = df.drop(target_col, axis=1)
    # Sayısal olmayanları at
    X = X.select_dtypes(include=[np.number])
    y = df[target_col]
    
    # NaN temizliği (Zorunlu)
    non_nan_mask = y.notna()
    X = X[non_nan_mask]
    y = y[non_nan_mask]
    
    # Hala NaN varsa (X içinde)
    X = X.fillna(X.median())
    
    print(f"> Bulunan Dosya: {veri_yolu}")
    gorsel_dir = os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller", "11_Veri_Temsili_Kiyaslama")
    
    if not os.path.exists(gorsel_dir):
        os.makedirs(gorsel_dir)

    print("============================================================")
    print("FAZ 3 - ADIM 11: VERİ TEMSİLİ VE BAŞARI KIYASLAMASI")
    print("============================================================")

    # Örneklem (Hız için)
    X_sample, _, y_sample, _ = train_test_split(X, y, train_size=5000, stratify=y, random_state=42)

    # 1. Ham Özellikler (Tümü)
    best_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    f1_ham = np.mean(cross_val_score(best_clf, X_sample, y_sample, cv=3, scoring='f1_macro'))
    print(f"> Ham Özellikler F1: {f1_ham:.4f}")

    # 2. Filter ile seçilmiş (Korelasyon > 0.1)
    correlations = df.corr()[target_col].abs().sort_values(ascending=False)
    filter_features = correlations[correlations > 0.1].index.tolist()
    if target_col in filter_features: filter_features.remove(target_col)
    X_filter = X_sample[filter_features]
    f1_filter = np.mean(cross_val_score(best_clf, X_filter, y_sample, cv=3, scoring='f1_macro'))
    print(f"> Filtered (Corr) F1: {f1_filter:.4f}")

    # 3. Wrapper/Embedded ile seçilmiş (En iyi 15 özellik - Step 2.2/2.3 mantığı)
    best_clf.fit(X_sample, y_sample)
    importances = pd.Series(best_clf.feature_importances_, index=X.columns).sort_values(ascending=False)
    wrapper_features = importances.head(15).index.tolist()
    X_wrapper = X_sample[wrapper_features]
    f1_wrapper = np.mean(cross_val_score(best_clf, X_wrapper, y_sample, cv=3, scoring='f1_macro'))
    print(f"> Wrapper/Embedded F1: {f1_wrapper:.4f}")

    # 4. PCA Bileşenleri (Varyans %90)
    pca = PCA(n_components=11)
    X_pca = pca.fit_transform(X_sample)
    f1_pca = np.mean(cross_val_score(best_clf, X_pca, y_sample, cv=3, scoring='f1_macro'))
    print(f"> PCA Bileşenleri F1: {f1_pca:.4f}")

    # GÖRSELLEŞTİRME (AKADEMİK PANEL)
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#F0F2F5')
    
    # Veri Hazırlığı
    data = {
        'Özellik Seçimi Yöntemi': ['Ham Özellikler (Tümü)', 'Filtreleme (Korelasyon)', 'Gömülü Yöntem (RF)', 'PCA Bileşenleri'],
        'Model': ['Random Forest', 'Random Forest', 'Random Forest', 'Random Forest'],
        'F1-Skoru': [f1_ham, f1_filter, f1_wrapper, f1_pca]
    }
    kiyas_df = pd.DataFrame(data)

    # Bar Grafiği
    colors = ['#1B263B', '#415A77', '#778DA9', '#E0E1DD']
    sns.barplot(data=kiyas_df, x='Özellik Seçimi Yöntemi', y='F1-Skoru', palette=colors, ax=ax)
    
    # Değerleri bar üzerine yaz
    for i, v in enumerate(kiyas_df['F1-Skoru']):
        ax.text(i, v + 0.01, f'{v:.4f}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#1B263B')

    # Tabloyu ekle (PDF'deki formatta)
    table_data = kiyas_df.values.tolist()
    table = plt.table(cellText=table_data, 
                      colLabels=kiyas_df.columns, 
                      loc='bottom', 
                      bbox=[0, -0.45, 1, 0.3],
                      cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)

    # Başlıklar
    plt.title("Şekil 3.11: Özellik Temsili Stratejilerinin Model Performansı Üzerindeki Etkisi\n(Literatür Bazlı Karşılaştırmalı Analiz)", 
              fontsize=16, fontweight='bold', pad=20, color='#1B263B')
    ax.set_ylabel("Macro F1-Skoru", fontsize=12, fontweight='bold')
    ax.set_xlabel("", fontsize=12)
    ax.set_ylim(0, 1.1)
    
    plt.subplots_adjust(bottom=0.35)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Kaydet
    output_path = os.path.join(gorsel_dir, "Adim_3_11_Veri_Temsili_Kiyaslama.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"> Karşılaştırma tablosu kaydedildi: {output_path}")
    plt.close()

if __name__ == "__main__":
    gorsel_olustur_adim_3_11()
