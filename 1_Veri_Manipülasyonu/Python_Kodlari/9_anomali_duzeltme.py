import pandas as pd
import numpy as np
import os
import sys
import time
import shutil
import re

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
original_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme", "birlesik_veri_türkçe.xlsx")
step5_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "5_Kritik_Sutun_Temizligi", "kritik_sutunlar_temizlenmis_renkli.xlsx")
step7_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "7_Finansal_Sutun_Temizligi", "finansal_veriler_temizlenmis_renkli.xlsx")
step8_report = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "8_Finansal_Tutarlilik_Denetimi", "final_finansal_tutarlilik_denetimi.xlsx")

output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "9_Anomali_Duzeltme")
if not os.path.exists(output_dir): os.makedirs(output_dir)
output_file = os.path.join(output_dir, "final_temiz_veri_renkli.xlsx")
denetim_file = os.path.join(output_dir, "final_anomali_temizlik_raporu.xlsx")

def parse_age(val):
    if pd.isna(val) or not isinstance(val, str): return val
    parts = re.findall(r'\d+', val)
    if len(parts) == 2: return int(parts[0]) * 12 + int(parts[1])
    elif len(parts) == 1: return int(parts[0]) * 12 if "Yıl" in val else int(parts[0])
    return np.nan

import matplotlib.pyplot as plt
import seaborn as sns

def gorsel_olustur_adim9(ozet_df, gorsel_dir):
    print("\n> Çocuk Dostu Görseller Hazırlanıyor (Adım 9)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    plt.style.use('seaborn-v0_8-pastel')
    
    # 1. Onarım Özeti (Donut)
    plt.figure(figsize=(8,8))
    onarılan = ozet_df["Aykırı Değer"].sum()
    saglam = ozet_df["Sağlam Değer"].sum()
    plt.pie([saglam, onarılan], labels=['Sağlam Veri', 'Onarılan Anomali'], autopct='%1.1f%%', colors=['#2ecc71', '#f39c12'], startangle=90, wedgeprops={'width':0.4})
    plt.title("Final Anomali Onarımı Başarısı", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_final_onarım_donut.png"))
    plt.close()

    # 2-11. En Çok Onarılan 10 Sütun (10 Adet)
    for i, row in enumerate(ozet_df.sort_values(by="Aykırı Değer", ascending=False).head(10).itertuples()):
        plt.figure(figsize=(10,6))
        plt.bar(['Onarılan Hata'], [row._5], color='#e67e22')
        plt.title(f"{row._1} - Onarım Sayısı", fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, f"{i+2}_{row._1}_onarım_bar.png"))
        plt.close()

    # 12. Başarı Bayrağı
    plt.figure(figsize=(6,4))
    plt.text(0.5, 0.5, "%100", fontsize=100, color='#f39c12', ha='center', va='center', fontweight='bold')
    plt.text(0.5, 0.2, "Anomali Temizliği", fontsize=20, color='#d35400', ha='center')
    plt.axis('off')
    plt.title("Adım 9 Başarı Bayrağı!", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "12_basari_bayragi.png"))
    plt.close()

    # --- EK 5 GLOBAL GÖRSEL ---
    # 13. Global Onarım Dağılımı (Bar)
    plt.figure(figsize=(12,8))
    sns.barplot(x="Aykırı Değer", y="Sütun Adı", data=ozet_df.sort_values(by="Aykırı Değer"), palette="YlOrBr")
    plt.title("Tüm Sütunlardaki Anomali Onarım Sayıları", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "13_global_onarım_dagilimi.png"))
    plt.close()

    # 14. Global Temizlik Oranı (Bar)
    plt.figure(figsize=(12,6))
    plt.bar(ozet_df["Sütun Adı"], ozet_df["Değişim Oranı (%)"], color='#e67e22')
    plt.xticks(rotation=45, ha='right')
    plt.title("Sütun Bazlı Veri Değişim Oranları (%)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "14_global_degisim_oranlari.png"))
    plt.close()

    # 15. Global Onarım Isı Haritası (Heatmap)
    plt.figure(figsize=(10,6))
    pivot_data = ozet_df.set_index("Sütun Adı")[["Aykırı Değer"]]
    sns.heatmap(pivot_data, annot=True, fmt="g", cmap="Oranges")
    plt.title("Anomali Onarım Yoğunluk Matrisi", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "15_global_onarım_heatmap.png"))
    plt.close()

    # 16. Sağlam vs Onarılan Trendi (Area Plot)
    plt.figure(figsize=(12,6))
    plt.fill_between(ozet_df["Sütun Adı"], ozet_df["Sağlam Değer"], color="skyblue", alpha=0.4, label='Sağlam')
    plt.fill_between(ozet_df["Sütun Adı"], ozet_df["Aykırı Değer"], color="orange", alpha=0.5, label='Onarılan')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.title("Veri Seti Sağlık Profili (Global)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "16_global_saglik_profili.png"))
    plt.close()

    # 17. Final Kalite Notu (Bar)
    plt.figure(figsize=(10,6))
    success_rate = (1 - (ozet_df["Aykırı Değer"].sum() / ozet_df["Toplam Değer"].sum())) * 100
    plt.bar(['Final Veri Kalitesi'], [success_rate], color='#27ae60')
    plt.ylim(0, 100)
    plt.text(0, success_rate/2, f"%{success_rate:.2f}", ha='center', fontsize=30, color='white', fontweight='bold')
    plt.title("Adım 9 Sonrası Global Veri Kalitesi", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "17_global_kalite_notu.png"))
    plt.close()

def anomali_duzeltme_adim9_v2():
    print("\n" + "="*50)
    print("ADIM 9: TRIPLE-COLOR ANOMALY CORRECTION (V2)")
    print("="*50)
    
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "9_Anomali_Duzeltme")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)

    # ÖNCEKİ VERİLERİ KONTROL ET (Dataset Skip Mantığı)
    if os.path.exists(output_file):
        print(f"\n> BİLGİ: '{os.path.basename(output_file)}' zaten mevcut.")
        print("> SADECE GÖRSEL VE RAPORLAR GÜNCELLENİYOR (Update Mode)...")
        ozet_df = pd.read_excel(denetim_file, sheet_name='GENEL ÖZET')
        gorsel_olustur_adim9(ozet_df, gorsel_dir)
        print("\nİŞLEM TAMAMLANDI (Görseller Güncellendi)!")
        return

    # 1. Verileri Oku
    df = pd.read_excel(step7_file, engine='openpyxl')
    prev_df = df.copy() 
    orig_df = pd.read_excel(original_file, engine='openpyxl')
    orig_df["Kredi Geçmişi Yaşı"] = orig_df["Kredi Geçmişi Yaşı"].apply(parse_age)
    s5_df = pd.read_excel(step5_file, engine='openpyxl')
    
    # 2. Step 8 Raporu
    xls = pd.ExcelFile(step8_report)
    sheets = xls.sheet_names
    if "GENEL ÖZET" in sheets: sheets.remove("GENEL ÖZET")
    
    ozet_veriler, detayli_onarımlar = [], {}
    
    for sheet in sheets:
        report_df = pd.read_excel(xls, sheet_name=sheet)
        error_ids = report_df[report_df["Durum"] == "X"]["Müşteri ID"].tolist()
        col_name = sheet
        print(f"> {col_name} denetleniyor...")
        mask_error = df["Müşteri ID"].isin(error_ids)
        aykiri_say = 0
        if error_ids:
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
            id_medians = df.groupby("Müşteri ID")[col_name].transform('median')
            df.loc[mask_error, col_name] = id_medians[mask_error].fillna(df[col_name].median())
            aykiri_say = mask_error.sum()
            if aykiri_say > 0:
                detayli_onarımlar[col_name] = pd.DataFrame({
                    "Müşteri ID": df.loc[mask_error, "Müşteri ID"],
                    "Önceki Değer": prev_df.loc[mask_error, col_name],
                    "Sonraki Değer": df.loc[mask_error, col_name],
                    "Düzeltme Gerekçesi": "Anomali Onarımı (Step 8 Audit)"
                })

        ozet_veriler.append({
            "Sütun Adı": col_name, "Sağlam Değer": len(df) - aykiri_say,
            "Eksik Değer Doldurması": 0, "Karakter Yanlışı": 0,
            "Aykırı Değer": aykiri_say, "Toplam Değer": len(df),
            "Değişim Oranı (%)": round((aykiri_say/len(df))*100, 2)
        })

    # 3. Raporu Yaz
    with pd.ExcelWriter(denetim_file, engine='xlsxwriter') as writer:
        pd.DataFrame(ozet_veriler).to_excel(writer, sheet_name='GENEL ÖZET', index=False)
        for col, ddf in detayli_onarımlar.items(): ddf.to_excel(writer, sheet_name=col[:31], index=False)

    # 4. Final Excel (Renkli)
    with pd.ExcelWriter(output_file, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
        df.to_excel(writer, sheet_name='Final Temiz Veri', index=False)
        workbook, worksheet = writer.book, writer.sheets['Final Temiz Veri']
        green, blue, orange = workbook.add_format({'bg_color': '#C6EFCE'}), workbook.add_format({'bg_color': '#DEEBF7'}), workbook.add_format({'bg_color': '#FFD966'})
        for col_idx, col in enumerate(df.columns):
            mask_orange = df[col].astype(str) != prev_df[col].astype(str)
            mask_blue = (prev_df[col].astype(str) != s5_df[col].astype(str)) & (~mask_orange)
            mask_green = (s5_df[col].astype(str) != orig_df[col].astype(str)) & (~mask_orange) & (~mask_blue)
            for r_idx in mask_orange[mask_orange].index: worksheet.write(r_idx+1, col_idx, df.iloc[r_idx, col_idx], orange)
            for r_idx in mask_blue[mask_blue].index: worksheet.write(r_idx+1, col_idx, df.iloc[r_idx, col_idx], blue)
            for r_idx in mask_green[mask_green].index: worksheet.write(r_idx+1, col_idx, df.iloc[r_idx, col_idx], green)

    # GÖRSELLERİ OLUŞTUR
    gorsel_olustur_adim9(pd.DataFrame(ozet_veriler), gorsel_dir)

    print(f"\nİŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    anomali_duzeltme_adim9_v2()
