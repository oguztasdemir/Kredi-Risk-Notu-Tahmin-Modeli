import pandas as pd
import numpy as np
import os
import time
import sys
import re
import shutil

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
base_original_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme", "birlesik_veri_türkçe.xlsx")
step5_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "5_Kritik_Sutun_Temizligi", "kritik_sutunlar_temizlenmis_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "7_Finansal_Sutun_Temizligi")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "7_Finansal_Sutun_Temizligi")

output_file = os.path.join(output_dir, "finansal_veriler_temizlenmis_renkli.xlsx")
denetim_file = os.path.join(output_dir, "finansal_temizlik_raporu.xlsx")

def parse_credit_age(val):
    if pd.isna(val) or not isinstance(val, str): return val
    try:
        parts = re.findall(r'\d+', val)
        if len(parts) == 2: return int(parts[0]) * 12 + int(parts[1])
        elif len(parts) == 1: return int(parts[0]) * 12 if "Yıl" in val else int(parts[0])
        return np.nan
    except: return np.nan

def clean_str_val(val):
    s = str(val).strip().lower()
    if s.endswith('.0'): s = s[:-2]
    return s

def akilli_finansal_temizlik_v7():
    print("\n" + "="*50)
    print("ADIM 7: FİNANSAL VERİ CERRAHİ ONARIMI (V7 - FORENSIC)")
    print("="*50)

    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    df = pd.read_excel(step5_file, engine='openpyxl')
    prev_df = df.copy()

    # ÖZEL SÜTUN TESPİTİ: Minimum Ödeme Tutarı aslında bir Flag olabilir (Evet/Hayır)
    # Eğer %80'den fazlası Evet/Hayır ise onu kategorik işle.
    if df["Minimum Ödeme Tutarı"].astype(str).str.contains("Evet|Hayır|Yes|No").mean() > 0.5:
        flag_mode = True
    else:
        flag_mode = False

    finansal_sutunlar = [
        "Banka Hesabı Sayısı", "Kredi Kartı Sayısı", "Faiz Oranı", "Kredi Sayısı",
        "Ödeme Gecikme Günü", "Geciken Ödeme Sayısı", "Kredi Limiti Değişimi",
        "Kredi Sorgu Sayısı", "Kredi Karışımı", "Toplam Borç", "Kredi Kullanım Oranı",
        "Kredi Geçmişi Yaşı", "Minimum Ödeme Tutarı", "Toplam Aylık Taksit",
        "Aylık Yatırım Tutarı", "Ödeme Davranışı", "Aylık Bakiye"
    ]
    
    # Pre-parse Credit Age
    df["Kredi Geçmişi Yaşı"] = df["Kredi Geçmişi Yaşı"].apply(parse_credit_age)
    prev_df["Kredi Geçmişi Yaşı"] = prev_df["Kredi Geçmişi Yaşı"].apply(parse_credit_age)

    ozet_veriler = []
    detayli_onarımlar = {}
    start_time = time.time()

    for i, col in enumerate(finansal_sutunlar):
        sys.stdout.write(f"\rİşlem: {col[:15]}...")
        sys.stdout.flush()
        
        row_reasons = pd.Series("Sağlam", index=df.index)
        
        # Kategorik Sütunlar
        if col in ["Kredi Karışımı", "Ödeme Davranışı"] or (col == "Minimum Ödeme Tutarı" and flag_mode):
            id_mode = df.groupby("Müşteri ID")[col].transform(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
            mask_diff = (df[col].astype(str) != id_mode.astype(str)) & (id_mode.notnull())
            row_reasons[mask_diff] = "Aykırı Değer"
            df[col] = id_mode
        else:
            # Sayısal Sütunlar
            df[col] = pd.to_numeric(df[col], errors='coerce')
            id_median = df.groupby("Müşteri ID")[col].transform('median')
            
            if col in ["Banka Hesabı Sayısı", "Kredi Kartı Sayısı", "Kredi Sayısı"]:
                mask_outlier = (df[col].notnull()) & (abs(df[col] - id_median) > 10)
                df[col] = df[col].where(~mask_outlier, id_median).fillna(id_median)
                row_reasons[mask_outlier] = "Aykırı Değer"
            elif "Yaşı" in col:
                df[col] = df[col].fillna(id_median).fillna(method='ffill').fillna(method='bfill')
            elif "Taksit" in col or "Yatırım" in col:
                # Maaş ile ilişki kur: Taksit + Yatırım < Maaş * 1.5 (Toleranslı)
                maaş = pd.to_numeric(df["Aylık Net Maaş"], errors='coerce').fillna(df["Aylık Net Maaş"].median())
                mask_absurd = (df[col] > maaş * 2)
                df[col] = df[col].where(~mask_absurd, id_median).fillna(id_median)
                row_reasons[mask_absurd] = "Aykırı Değer"
            else:
                df[col] = df[col].fillna(id_median).fillna(df[col].median())

        actual_diff_mask = df[col].astype(str) != prev_df[col].astype(str)
        if actual_diff_mask.any():
            detayli_onarımlar[col] = pd.DataFrame({
                "Müşteri ID": df.loc[actual_diff_mask, "Müşteri ID"],
                "Önceki Değer": prev_df.loc[actual_diff_mask, col],
                "Sonraki Değer": df.loc[actual_diff_mask, col],
                "Düzeltme Gerekçesi": row_reasons[actual_diff_mask].replace("Sağlam", "Eksik Değer Doldurması")
            })

        ozet_veriler.append({
            "Sütun Adı": col,
            "Sağlam Değer": (actual_diff_mask == False).sum(),
            "Eksik Değer Doldurması": (actual_diff_mask & row_reasons.str.contains("Sağlam|Eksik")).sum(),
            "Karakter Yanlışı": 0, # Artık Numeric conversion içinde eridi
            "Aykırı Değer": (actual_diff_mask & (row_reasons == "Aykırı Değer")).sum(),
            "Toplam Değer": len(df),
            "Değişim Oranı (%)": round((actual_diff_mask.sum()/len(df))*100, 2)
        })

    # FINAL EXCEL EXPORT
    with pd.ExcelWriter(denetim_file, engine='xlsxwriter') as writer:
        pd.DataFrame(ozet_veriler).to_excel(writer, sheet_name='GENEL ÖZET', index=False)
        for col, ddf in detayli_onarımlar.items(): ddf.to_excel(writer, sheet_name=col[:31], index=False)

    original_base = pd.read_excel(base_original_file, engine='openpyxl')
    original_base["Kredi Geçmişi Yaşı"] = original_base["Kredi Geçmişi Yaşı"].apply(parse_credit_age)
    
    with pd.ExcelWriter(output_file, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
        df.to_excel(writer, sheet_name='Temizlenmiş Veri', index=False)
        workbook, worksheet = writer.book, writer.sheets['Temizlenmiş Veri']
        green, blue = workbook.add_format({'bg_color': '#C6EFCE'}), workbook.add_format({'bg_color': '#DEEBF7'})
        for col_idx, col in enumerate(df.columns):
            mask_blue = df[col].astype(str) != prev_df[col].astype(str)
            mask_green = (prev_df[col].astype(str) != original_base[col].astype(str)) & (~mask_blue)
            for r_idx in mask_blue[mask_blue].index: worksheet.write(r_idx+1, col_idx, df.iloc[r_idx, col_idx], blue)
            for r_idx in mask_green[mask_green].index: worksheet.write(r_idx+1, col_idx, df.iloc[r_idx, col_idx], green)

    print(f"\n\nİŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    akilli_finansal_temizlik_v7()
