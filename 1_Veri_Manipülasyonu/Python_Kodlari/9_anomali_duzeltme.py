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

def anomali_duzeltme_adim9_v2():
    print("\n" + "="*50)
    print("ADIM 9: TRIPLE-COLOR ANOMALY CORRECTION (V2)")
    print("="*50)
    
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
    
    ozet_veriler = []
    detayli_onarımlar = {}
    
    for sheet in sheets:
        report_df = pd.read_excel(xls, sheet_name=sheet)
        error_ids = report_df[report_df["Durum"] == "X"]["Müşteri ID"].tolist()
        
        col_name = sheet
        print(f"> {col_name} denetleniyor...")
        
        mask_error = df["Müşteri ID"].isin(error_ids)
        aykiri_say = 0
        
        if error_ids:
            # Düzeltme
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
            id_medians = df.groupby("Müşteri ID")[col_name].transform('median')
            
            # Değişiklikleri Kaydet
            actual_change_mask = (df[col_name].astype(str) != id_medians.astype(str)) & mask_error
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
            "Sütun Adı": col_name,
            "Sağlam Değer": len(df) - aykiri_say,
            "Eksik Değer Doldurması": 0, # Bu adımda eksik doldurulmadı, anomali onarıldı
            "Karakter Yanlışı": 0,
            "Aykırı Değer": aykiri_say,
            "Toplam Değer": len(df),
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

    print(f"\nİŞLEM TAMAMLANDI!")
    print(f"Final Veri: {output_file}")
    print(f"Audit Raporu: {denetim_file}")

if __name__ == "__main__":
    anomali_duzeltme_adim9_v2()
