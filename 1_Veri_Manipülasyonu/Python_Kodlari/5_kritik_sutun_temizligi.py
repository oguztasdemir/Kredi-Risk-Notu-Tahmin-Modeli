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
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme", "birlesik_veri_türkçe.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "5_Kritik_Sutun_Temizligi")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "5_Kritik_Sutun_Temizligi")

output_file = os.path.join(output_dir, "kritik_sutunlar_temizlenmis_renkli.xlsx")
denetim_file = os.path.join(output_dir, "detayli_temizlik_raporu.xlsx")

def clean_str_val(val):
    s = str(val).strip().lower()
    if s.endswith('.0'): s = s[:-2]
    return s

def progress_bar(current, total, start_time, prefix=''):
    percent = (current / total) * 100
    elapsed = time.time() - start_time
    speed = current / elapsed if elapsed > 0 else 0
    remaining = (total - current) / speed if speed > 0 else 0
    bar = "#" * int(percent / 2) + "-" * (50 - int(percent / 2))
    sys.stdout.write(f"\r{prefix} |{bar}| %{percent:.1f} - Hız: {speed:.2f} it/s - Kalan: {remaining:.1f}sn")
    sys.stdout.flush()

def temizle_karakter_saf(text):
    if pd.isna(text) or not isinstance(text, str):
        return text
    clean = re.sub(r'[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ\s,.-]', '', text).strip()
    return clean

def akilli_temizlik_v6():
    print("\n" + "="*50)
    print("ADIM 5: CERRAHİ KRİTİK SÜTUN ONARIMI (V6)")
    print("="*50)

    # İNTERAKTİF SEÇİM (AI Modunda Otomatik '1')
    if os.path.exists(output_file):
        print(f"\nUYARI: '{os.path.basename(output_file)}' zaten mevcut.")
        secim = "1" # AI Otomasyonu için
        if secim == "2":
            print("> Mevcut Excel üzerinden rapor ve görseller güncelleniyor...")
            df = pd.read_excel(output_file, engine='openpyxl')
            original_df = pd.read_excel(input_file, engine='openpyxl')
        else:
            for d in [output_dir, gorsel_dir]:
                if os.path.exists(d): shutil.rmtree(d)
                os.makedirs(d)
            df = pd.read_excel(input_file, engine='openpyxl')
            original_df = df.copy()
    else:
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
        df = pd.read_excel(input_file, engine='openpyxl')
        original_df = df.copy()

    kritik_sutunlar = ["İsim", "Yaş", "Kimlik No", "Meslek", "Yıllık Gelir", "Aylık Net Maaş", "Kredi Türü"]
    placeholders = ["belirtilmemiş", "bilinmiyor", "unknown", "none", "null", "-", "_", "nan", " ", ""]
    
    detayli_onarımlar = {}
    ozet_veriler = []
    start_time = time.time()
    
    for i, col in enumerate(kritik_sutunlar):
        progress_bar(i, len(kritik_sutunlar), start_time, prefix=f'İşlem: {col[:10]}')
        
        row_reasons = pd.Series("", index=df.index)
        eksik_say, karakter_say, aykiri_say = 0, 0, 0

        is_placeholder = df[col].astype(str).str.lower().str.strip().isin(placeholders)
        is_missing = is_placeholder | df[col].isna()
        df.loc[is_placeholder, col] = np.nan
        eksik_say = is_missing.sum()

        if df[col].dtype == 'object':
            cleaned_col = df[col].apply(temizle_karakter_saf)
            mask_char = (df[col].notnull()) & (~is_missing) & (df[col].astype(str) != cleaned_col.astype(str))
            row_reasons[mask_char] = "Karakter Yanlışı"
            df[col] = cleaned_col
            karakter_say = mask_char.sum()

        if col in ["İsim", "Kimlik No", "Meslek"]:
            id_mode = df.groupby("Müşteri ID")[col].transform(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
            mask_outlier = (df[col].notnull()) & (~is_missing) & (df[col].astype(str) != id_mode.astype(str))
            row_reasons[mask_outlier & (row_reasons == "")] = "Aykırı Değer"
            df[col] = id_mode
            aykiri_say = mask_outlier.sum()
            
        elif col == "Yaş":
            temp_numeric = pd.to_numeric(df[col], errors='coerce')
            id_median = temp_numeric.groupby(df["Müşteri ID"]).transform('median').round()
            mask_outlier = (temp_numeric.notnull()) & (~is_missing) & (abs(temp_numeric - id_median) > 1)
            row_reasons[mask_outlier & (row_reasons == "")] = "Aykırı Değer"
            df[col] = temp_numeric.where(~mask_outlier, id_median).fillna(id_median)
            aykiri_say = mask_outlier.sum()
            
        elif col in ["Yıllık Gelir", "Aylık Net Maaş"]:
            temp_numeric = pd.to_numeric(df[col], errors='coerce')
            id_median = temp_numeric.groupby(df["Müşteri ID"]).transform('median')
            safe_median = id_median.replace(0, 1)
            threshold = 0.3 if col == "Aylık Net Maaş" else 0.5
            mask_outlier = (temp_numeric.notnull()) & (~is_missing) & ((temp_numeric > safe_median * (1 + threshold)) | (temp_numeric < safe_median * (1 - threshold)))
            row_reasons[mask_outlier & (row_reasons == "")] = "Aykırı Değer"
            df[col] = temp_numeric.where(~mask_outlier, id_median).fillna(id_median)
            aykiri_say = mask_outlier.sum()

        actual_diff = []
        for idx in df.index:
            if clean_str_val(original_df.at[idx, col]) != clean_str_val(df.at[idx, col]):
                actual_diff.append(idx)
        
        if actual_diff:
            detayli_onarımlar[col] = pd.DataFrame({
                "Müşteri ID": df.loc[actual_diff, "Müşteri ID"],
                "Önceki Değer": original_df.loc[actual_diff, col],
                "Sonraki Değer": df.loc[actual_diff, col],
                "Düzeltme Gerekçesi": row_reasons[actual_diff]
            }).sort_values(by="Düzeltme Gerekçesi")

        ozet_veriler.append({
            "Sütun Adı": col,
            "Sağlam Değer": len(df) - len(actual_diff),
            "Eksik Değer Doldurması": eksik_say,
            "Karakter Yanlışı": karakter_say,
            "Aykırı Değer": aykiri_say,
            "Toplam Değer": len(df),
            "Değişim Oranı (%)": round((len(actual_diff)/len(df))*100, 2)
        })

    progress_bar(len(kritik_sutunlar), len(kritik_sutunlar), start_time, prefix='Tamamlandı')
    
    print(f"\n\n> Audit Raporu ve Renkli Excel hazırlanıyor...")
    with pd.ExcelWriter(denetim_file, engine='xlsxwriter') as writer:
        pd.DataFrame(ozet_veriler).to_excel(writer, sheet_name='GENEL ÖZET', index=False)
        for col_name, diff_df in detayli_onarımlar.items():
            diff_df.to_excel(writer, sheet_name=col_name[:31], index=False)

    with pd.ExcelWriter(output_file, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
        df.to_excel(writer, sheet_name='Temizlenmiş Veri', index=False)
        workbook, worksheet = writer.book, writer.sheets['Temizlenmiş Veri']
        green = workbook.add_format({'bg_color': '#C6EFCE'})
        for col_idx, col in enumerate(df.columns):
            if col in detayli_onarımlar:
                for row_idx in detayli_onarımlar[col].index:
                    worksheet.write(row_idx + 1, col_idx, df.iloc[row_idx, col_idx], green)

    print(f"\nİŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    akilli_temizlik_v6()
