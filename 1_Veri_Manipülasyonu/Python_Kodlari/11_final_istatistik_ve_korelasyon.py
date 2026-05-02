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
    print("\n> Akademik Görseller Hazırlanıyor (Adım 11)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    
    # PANEL 1: KORELASYON VE GENEL YAPI
    fig1 = plt.figure(figsize=(18, 14))
    gs1 = fig1.add_gridspec(2, 2)

    # 11.1 Korelasyon (Heatmap)
    ax1 = fig1.add_subplot(gs1[:, 0])
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdYlGn", center=0, ax=ax1, cbar_kws={'shrink': .8})
    ax1.set_title("Şekil 11.1: Özellikler Arası Global Korelasyon Matrisi")

    # 11.2 Veri Çeşitliliği (Donut)
    ax2 = fig1.add_subplot(gs1[0, 1])
    uniques = df.nunique().sort_values().tail(10)
    ax2.pie(uniques, labels=uniques.index, autopct='%1.1f%%', startangle=140, wedgeprops={'width':0.4, 'edgecolor': 'white'})
    ax2.set_title("Şekil 11.2: En Yüksek Varyanslı 10 Özellik (Benzersiz Değer Payı)")

    # 11.3 Kredi Skoru Final Dağılım (Count)
    ax3 = fig1.add_subplot(gs1[1, 1])
    if "Kredi Skoru" in df.columns:
        sns.countplot(x="Kredi Skoru", data=df, palette="viridis", ax=ax3)
        ax3.set_title("Şekil 11.3: Hedef Etiket (Kredi Skoru) Final Dağılımı")

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_11_Panel_1_Korelasyon.png"))
    plt.close()

    # PANEL 2: İSTATİSTİKSEL DAĞILIM VE SKEWNESS
    fig2 = plt.figure(figsize=(18, 12))
    gs2 = fig2.add_gridspec(2, 2)

    # 11.4 Meslek Dağılımı (Barh)
    ax4 = fig2.add_subplot(gs2[0, 0])
    m_counts = df["Meslek"].value_counts().head(10)
    sns.barplot(x=m_counts.values, y=m_counts.index, palette="mako", ax=ax4)
    ax4.set_title("Şekil 11.4: Müşteri Portföyü Meslek Dağılımı (Top 10)")

    # 11.5 Skewness Analizi
    ax5 = fig2.add_subplot(gs2[0, 1])
    num_cols = df.select_dtypes(include=[np.number]).columns
    skewness = df[num_cols].skew().sort_values()
    colors = ['#e74c3c' if abs(x) > 1 else '#27ae60' for x in skewness.values]
    ax5.bar(skewness.index, skewness.values, color=colors)
    ax5.set_xticklabels(ax5.get_xticklabels(), rotation=90)
    ax5.axhline(y=0, color='black', linewidth=0.8)
    ax5.set_title("Şekil 11.5: Veri Eğriliği (Skewness) ve Normal Dağılım Uyumluluğu")

    # 11.6 Tanımlayıcı İstatistikler (Table)
    ax6 = fig2.add_subplot(gs2[1, :])
    ax6.axis('off')
    stats_data = [["Metrik"] + list(num_cols[:5])] # Sadece ilk 5 sütun sığar
    for idx in ['mean', 'std', 'min', 'max']:
        stats_data.append([idx.upper()] + [f"{df[c].describe()[idx]:.2f}" for c in num_cols[:5]])
    tab = ax6.table(cellText=stats_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 3)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        else: cell.set_facecolor('#f8f9fa')
    ax6.set_title("Tablo 11.1: Kritik Finansal Değişkenler Deskriptif İstatistikleri", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_11_Panel_2_Istatistik.png"))
    plt.close()
    print(f"Görseller kaydedildi: {gorsel_dir}")

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
