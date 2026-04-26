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
    print("\n> Çocuk Dostu Görseller Hazırlanıyor (Adım 10)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    plt.style.use('seaborn-v0_8-pastel')
    
    # 1. Hazır vs Kritik (Pie)
    plt.figure(figsize=(8,8))
    hazir = len(report_df[report_df["Durum"].str.contains("HAZIR")])
    kritik = len(report_df) - hazir
    plt.pie([hazir, kritik], labels=['Hazır', 'Düzeltilmeli'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
    plt.title("Verilerimiz Modelleme İçin Hazır mı?", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_hazirlik_ozeti_pie.png"))
    plt.close()

    # 2. Global Kalite Puanları (Bar)
    plt.figure(figsize=(12,8))
    sns.barplot(x="Kalite Puanı", y="Sütun Adı", data=report_df.sort_values(by="Kalite Puanı", ascending=False), palette="viridis")
    plt.title("Her Sütun İçin Kalite Karnesi", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "2_global_kalite_bar.png"))
    plt.close()

    # 3-11. İlk 9 Sütun İçin Küçük Kartlar (9 Adet)
    for i, row in enumerate(report_df.head(9).itertuples()):
        plt.figure(figsize=(6,4))
        plt.text(0.5, 0.5, f"%{row._2}", fontsize=60, color='#3498db', ha='center', va='center', fontweight='bold')
        plt.text(0.5, 0.2, f"{row._1}", fontsize=18, color='#2c3e50', ha='center')
        plt.axis('off')
        plt.title("Doluluk Oranı", fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, f"{i+3}_{row._1}_kart.png"))
        plt.close()

    # 12. Final Başarı Bayrağı
    plt.figure(figsize=(6,4))
    plt.text(0.5, 0.5, "BAŞARILI", fontsize=60, color='#2ecc71', ha='center', va='center', fontweight='bold')
    plt.text(0.5, 0.2, "Veri Temizleme Tamamlandı!", fontsize=16, color='#27ae60', ha='center')
    plt.axis('off')
    plt.title("PROJE BAŞARI BAYRAĞI!", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "12_final_basari.png"))
    plt.close()

    # --- EK 5 GLOBAL GÖRSEL ---
    # 13. Global ML Hazırlık Skorları (Bar)
    plt.figure(figsize=(12,8))
    sns.barplot(x="Doluluk/Sağlık (%)", y="Sütun Adı", data=report_df.sort_values(by="Doluluk/Sağlık (%)"), palette="magma")
    plt.title("Tüm Sütunların ML Modelleme Hazırlık Durumu", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "13_global_ml_hazirlik.png"))
    plt.close()

    # 14. Doluluk vs Kalite İlişkisi (Scatter)
    plt.figure(figsize=(10,6))
    sns.scatterplot(x="Doluluk/Sağlık (%)", y="Kalite Puanı", hue="Durum", size="Benzersiz Değer", data=report_df, palette="deep", sizes=(100, 500))
    plt.title("Veri Doluluğu ve Kalite Puanı Karşılaştırması", fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "14_global_doluluk_vs_kalite.png"))
    plt.close()

    # 15. Global Kalite Isı Haritası (Heatmap)
    plt.figure(figsize=(10,6))
    pivot_data = report_df.set_index("Sütun Adı")[["Kalite Puanı"]]
    sns.heatmap(pivot_data, annot=True, cmap="RdYlGn", center=80)
    plt.title("Veri Seti Kalite Matrisi (Step 10 Final)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "15_global_kalite_heatmap.png"))
    plt.close()

    # 16. Durum Dağılımı (Bar)
    plt.figure(figsize=(10,6))
    counts = report_df["Durum"].value_counts()
    sns.barplot(x=counts.index, y=counts.values, palette="muted")
    plt.xticks(rotation=45, ha='right') # TAŞMAYI ÖNLEMEK İÇİN ROTASYON
    plt.title("Sütunlarımızın Final Durum Dağılımı", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "16_global_durum_ozeti.png"))
    plt.close()

    # 17. Final Proje Sağlık Ölçer (Gauge-like Bar)
    plt.figure(figsize=(10,4))
    avg_score = report_df["Kalite Puanı"].mean()
    plt.barh(['Proje Sağlık Puanı'], [avg_score], color='#2ecc71' if avg_score > 90 else '#f1c40f')
    plt.xlim(0, 100)
    plt.text(avg_score/2, 0, f"%{avg_score:.1f}", va='center', ha='center', fontsize=30, color='white', fontweight='bold')
    plt.title("VERİ MÜHENDİSLİĞİ FİNAL SKORU", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "17_global_proje_skoru.png"))
    plt.close()

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
