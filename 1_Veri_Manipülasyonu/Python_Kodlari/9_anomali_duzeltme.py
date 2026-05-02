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

def gorsel_olustur_adim9(ozet_df, gorsel_dir):
    print("\n> Akademik Görseller Hazırlanıyor (Adım 9)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2)

    # 9.1 Anomali Onarım Dağılımı (Barh)
    ax1 = fig.add_subplot(gs[0, 0])
    plot_df = ozet_df.sort_values(by="Aykırı Değer", ascending=True).tail(10)
    sns.barplot(x="Aykırı Değer", y="Sütun Adı", data=plot_df, palette="Oranges_r", ax=ax1)
    ax1.set_title("Şekil 9.1: En Çok Anomali Onarımı Yapılan 10 Değişken")

    # 9.2 Genel Onarım (Donut)
    ax2 = fig.add_subplot(gs[0, 1])
    onarılan = ozet_df["Aykırı Değer"].sum()
    saglam = ozet_df["Sağlam Değer"].sum()
    ax2.pie([saglam, onarılan], labels=['Tutarlı Veri', 'Onarılan Anomali'], 
            autopct='%1.1f%%', colors=['#27ae60', '#e67e22'], startangle=90, wedgeprops={'width':0.4, 'edgecolor': 'white'})
    ax2.set_title("Şekil 9.2: Veri Seti Genel Anomali Temizlik Oranı")

    # 9.3 Onarım Detay Tablosu
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    # Önemli olanları gösterelim
    tab_df = ozet_df.sort_values(by="Aykırı Değer", ascending=False).head(10)
    table_data = [["Özellik", "Onarılan Adet", "Değişim Oranı (%)"]] + tab_df[["Sütun Adı", "Aykırı Değer", "Değişim Oranı (%)"]].values.tolist()
    tab = ax3.table(cellText=table_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 2)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        else: cell.set_facecolor('#f8f9fa')
    ax3.set_title("Tablo 9.1: Sütun Bazlı Final Anomali Denetim İstatistikleri", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_9_Anomali_Panel.png"))
    plt.close()
    print(f"Görseller kaydedildi: {gorsel_dir}")

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
