import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "9_Anomali_Duzeltme", "final_temiz_veri_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "11_Final_Istatistik_ve_Korelasyon")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "11_Final_Istatistik_ve_Korelasyon")

if not os.path.exists(output_dir): os.makedirs(output_dir)
if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)

output_file = os.path.join(output_dir, "final_istatistik_ve_korelasyon_raporu.xlsx")

def gorsel_olustur_adim11(df, corr_matrix, stats_df):
    print("\n> Çocuk Dostu Görseller Hazırlanıyor (Adım 11)...")
    plt.style.use('seaborn-v0_8-pastel')
    
    # 1. Global Korelasyon Isı Haritası
    plt.figure(figsize=(16, 12))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdYlGn", center=0, linewidths=0.5)
    plt.title("Tüm Verilerin Birbirleriyle Olan Arkadaşlık Derecesi (Korelasyon)", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_global_korelasyon_heatmap.png"))
    plt.close()

    # 2. Kredi Skoru ile En Yakın Arkadaşlar (Pozitif Korelasyon)
    if "Kredi Skoru" in corr_matrix.columns:
        plt.figure(figsize=(10, 6))
        target_corr = corr_matrix["Kredi Skoru"].sort_values(ascending=False).drop("Kredi Skoru")
        top_pos = target_corr.head(5)
        sns.barplot(x=top_pos.values, y=top_pos.index, palette="Greens_d")
        plt.title("Kredi Skoru'nu Arttıran En Önemli 5 Özellik", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "2_pozitif_kredi_arkadaslari.png"))
        plt.close()

        # 3. Kredi Skoru'nu Üzenler (Negatif Korelasyon)
        plt.figure(figsize=(10, 6))
        top_neg = target_corr.tail(5)
        sns.barplot(x=top_neg.values, y=top_neg.index, palette="Reds_d")
        plt.title("Kredi Skoru'nu Düşüren En Önemli 5 Özellik", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "3_negatif_kredi_dusmanlari.png"))
        plt.close()

    # 4. Veri Dağılım Genişliği (Boxplot - Normalleştirilmiş)
    plt.figure(figsize=(15, 8))
    # Sadece sayısal ve çok varyansı olanları seçelim
    num_cols = df.select_dtypes(include=[np.number]).columns
    df_norm = (df[num_cols] - df[num_cols].mean()) / df[num_cols].std()
    sns.boxplot(data=df_norm, palette="Set3")
    plt.xticks(rotation=45, ha='right')
    plt.title("Sayısal Değerlerin Oyun Alanı (Normalleştirilmiş Dağılım)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "4_veri_dagilim_kutulari.png"))
    plt.close()

    # 5. Ortalama Değerler Tablosu (Görsel)
    plt.figure(figsize=(12, 6))
    numeric_stats = stats_df.apply(pd.to_numeric, errors='coerce').dropna(how='all')
    if "mean" in numeric_stats.index:
        means = numeric_stats.loc["mean"].dropna().sort_values()
        plt.barh(means.index, means.values, color='skyblue')
        plt.title("Sütunların Ortalama Büyüklükleri", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "5_ortalama_degerler_bar.png"))
    plt.close()

    # 6. Standart Sapma (Veri Hareketliliği)
    plt.figure(figsize=(12, 6))
    if "std" in numeric_stats.index:
        stds = numeric_stats.loc["std"].dropna().sort_values()
        plt.barh(stds.index, stds.values, color='salmon')
        plt.title("Hangi Veri Daha Çok Kıpır Kıpır? (Standart Sapma)", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "6_standart_sapma_hareketlilik.png"))
    plt.close()

    # 7. Veri Çeşitliliği (Unique Values)
    plt.figure(figsize=(10, 10))
    uniques = df.nunique().sort_values()
    plt.pie(uniques, labels=uniques.index, autopct='%1.1f%%', startangle=140)
    plt.title("Verilerimizin Çeşitlilik Karnesi", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "7_veri_cesitliligi_donut.png"))
    plt.close()

    # 8. Skewness (Eğrilik) Analizi
    plt.figure(figsize=(12, 6))
    skewness = df[num_cols].skew().sort_values()
    colors = ['red' if abs(x) > 1 else 'green' for x in skewness.values]
    plt.bar(skewness.index, skewness.values, color=colors)
    plt.xticks(rotation=45, ha='right')
    plt.axhline(y=0, color='black', linestyle='-')
    plt.title("Veri Dengesi: Gülen ve Üzülen Sütunlar (Skewness)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "8_egrilik_analizi_skewness.png"))
    plt.close()


    # 10. Hedef Değişken (Kredi Skoru) Dağılımı
    if "Kredi Skoru" in df.columns:
        plt.figure(figsize=(10, 6))
        sns.countplot(x="Kredi Skoru", data=df, palette="viridis")
        plt.title("Final Veri Setinde Kredi Skoru Dağılımı", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "10_kredi_skoru_final_dagilim.png"))
        plt.close()

def istatistik_ve_korelasyon_adim11():
    print("\n" + "="*50)
    print("ADIM 11: FINAL EDA - ISTATISTIK VE KORELASYON ANALIZI")
    print("="*50)

    # ÖNCEKİ VERİLERİ KONTROL ET (Update Mode)
    if os.path.exists(output_file):
        print(f"\n> BİLGİ: '{os.path.basename(output_file)}' zaten mevcut.")
        print("> SADECE GÖRSEL VE RAPORLAR GÜNCELLENİYOR (Update Mode)...")
        # Raporu oku (İstatistikler ve Korelasyon sekmeleri var)
        xls = pd.ExcelFile(output_file)
        stats_df = pd.read_excel(xls, sheet_name='TANIMLAYICI İSTATİSTİKLER', index_col=0)
        corr_matrix = pd.read_excel(xls, sheet_name='KORELASYON MATRİSİ', index_col=0)
        # Orijinal veriyi sadece diğer görseller için (pie, countplot vb) hızlıca oku
        df = pd.read_excel(input_file, engine='openpyxl')
        gorsel_olustur_adim11(df, corr_matrix, stats_df)
        print("\nİŞLEM TAMAMLANDI (Görseller Güncellendi)!")
        return

    # 1. Veriyi Yükle
    print("> Temizlenmiş veri seti yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')

    # 2. Tanımlayıcı İstatistikler
    print("> Tanımlayıcı istatistikler hesaplanıyor...")
    stats_df = df.describe(include='all').fillna("-")

    # 3. Korelasyon Analizi için Encoding
    print("> Korelasyon analizi için kategorik veriler kodlanıyor...")
    df_corr = df.copy()
    le = LabelEncoder()
    for col in df_corr.columns:
        if df_corr[col].dtype == 'object' or df_corr[col].dtype.name == 'category':
            # NaN değerleri geçici olarak doldur (Kredi Skoru gibi)
            temp_col = df_corr[col].astype(str)
            df_corr[col] = le.fit_transform(temp_col)
    
    corr_matrix = df_corr.corr()

    # 4. Raporu Excel'e Yaz
    print("> Excel raporu hazırlanıyor...")
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        stats_df.to_excel(writer, sheet_name='TANIMLAYICI İSTATİSTİKLER')
        corr_matrix.to_excel(writer, sheet_name='KORELASYON MATRİSİ')
        
        # Sütun bazlı detaylar (Eğrilik vb)
        detay_df = pd.DataFrame({
            "Sütun": df.select_dtypes(include=[np.number]).columns,
            "Eğrilik (Skewness)": df.select_dtypes(include=[np.number]).skew().values,
            "Basıklık (Kurtosis)": df.select_dtypes(include=[np.number]).kurtosis().values
        })
        detay_df.to_excel(writer, sheet_name='DETAYLI ANALİZ', index=False)

    # 5. Görselleri Oluştur
    gorsel_olustur_adim11(df, corr_matrix, stats_df)

    print(f"\nİŞLEM TAMAMLANDI! Çıktı: {output_file}")

if __name__ == "__main__":
    istatistik_ve_korelasyon_adim11()
