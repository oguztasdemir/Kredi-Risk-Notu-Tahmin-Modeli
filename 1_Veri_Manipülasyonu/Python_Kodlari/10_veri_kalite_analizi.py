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

import matplotlib.pyplot as plt
import seaborn as sns

def gorsel_olustur_adim10(report_df, gorsel_dir):
    print("\n> Akademik Görseller Hazırlanıyor (Adım 10)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2)

    # 10.1 Kalite Puanları (Barh)
    ax1 = fig.add_subplot(gs[0, 0])
    plot_df = report_df.sort_values(by="Kalite Puanı", ascending=True)
    sns.barplot(x="Kalite Puanı", y="Sütun Adı", data=plot_df, palette="viridis", ax=ax1)
    ax1.set_title("Şekil 10.1: Özellik Bazlı Veri Kalite Endeksi")
    ax1.set_xlim(0, 110)

    # 10.2 Durum Dağılımı (Donut)
    ax2 = fig.add_subplot(gs[0, 1])
    hazir = len(report_df[report_df["Durum"].str.contains("HAZIR")])
    kritik = len(report_df) - hazir
    ax2.pie([hazir, kritik], labels=['Model Hazır', 'Ek Denetim Gerekli'], 
            autopct='%1.1f%%', colors=['#27ae60', '#c0392b'], startangle=90, wedgeprops={'width':0.4, 'edgecolor': 'white'})
    ax2.set_title("Şekil 10.2: Modelleme Öncesi Veri Hazırlık Durumu")

    # 10.3 Kalite Matrisi (Table)
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    tab_df = report_df.sort_values(by="Kalite Puanı", ascending=False).head(15)
    table_data = [["Özellik", "Doluluk (%)", "Kalite Puanı", "Durum"]] + tab_df[["Sütun Adı", "Doluluk/Sağlık (%)", "Kalite Puanı", "Durum"]].values.tolist()
    tab = ax3.table(cellText=table_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(10); tab.scale(1, 1.8)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        else: cell.set_facecolor('#f8f9fa')
    ax3.set_title("Tablo 10.1: Forensic Intelligence Audit - Detaylı Kalite Raporu", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_10_Kalite_Panel.png"))
    plt.close()
    print(f"Görseller kaydedildi: {gorsel_dir}")

def analiz_adim10_v4():
    print("\n" + "="*50)
    print("ADIM 10: FORENSIC INTELLIGENCE AUDIT (V4)")
    print("="*50)
    
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "10_Veri_Kalite_Analizi")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)

    # ÖNCEKİ VERİLERİ KONTROL ET (Dataset Skip Mantığı)
    if os.path.exists(output_file):
        print(f"\n> BİLGİ: '{os.path.basename(output_file)}' zaten mevcut.")
        print("> SADECE GÖRSEL VE RAPORLAR GÜNCELLENİYOR (Update Mode)...")
        report_df = pd.read_excel(output_file)
        gorsel_olustur_adim10(report_df, gorsel_dir)
        print("\nİŞLEM TAMAMLANDI (Görseller Güncellendi)!")
        return

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
            # Test verisi için Kredi Skoru'nun %66.67 dolulukta olması normaldir (Model tahmini için ayrıldı)
            puan = 100 if fill_rate >= 65 else (fill_rate * 1.5)
            durum = "HAZIR (HEDEF DEĞİŞKEN)"
        elif col in ["Müşteri ID", "ID"]:
            # Müşteri ID bağımsızdır ve her zaman %100 hazır kabul edilmelidir
            puan = 100
            durum = "HAZIR"
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

    report_df = pd.DataFrame(kalite_ozeti)
    report_df.to_excel(output_file, index=False)

    # GÖRSELLERİ OLUŞTUR
    gorsel_olustur_adim10(report_df, gorsel_dir)

    print(f"\nİŞLEM TAMAMLANDI! Rapor: {output_file}")

if __name__ == "__main__":
    analiz_adim10_v4()
