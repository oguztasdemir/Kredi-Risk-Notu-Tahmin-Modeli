import pandas as pd
import numpy as np
import os
import time
import sys
import shutil
import matplotlib.pyplot as plt
import seaborn as sns

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "5_Kritik_Sutun_Temizligi", "kritik_sutunlar_temizlenmis_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "6_Veri_Tutarlilik_Denetimi")

# ÇAKIŞMA ÖNLEME
if os.path.exists(output_dir):
    try: shutil.rmtree(output_dir)
    except: pass
os.makedirs(output_dir)

output_file = os.path.join(output_dir, "final_tutarlilik_denetimi.xlsx")

def progress_bar(current, total, start_time, prefix=''):
    percent = (current / total) * 100
    elapsed = time.time() - start_time
    speed = current / elapsed if elapsed > 0 else 0
    remaining = (total - current) / speed if speed > 0 else 0
    bar = "#" * int(percent / 2) + "-" * (50 - int(percent / 2))
    sys.stdout.write(f"\r{prefix} |{bar}| %{percent:.1f} - Hız: {speed:.2f} it/s - Kalan: {remaining:.1f}sn")
    sys.stdout.flush()

def tutarlilik_denetimi():
    print("\n" + "="*50)
    print("ADIM 6: VERİ TUTARLILIK VE BÜTÜNLÜK DENETİMİ")
    print("="*50)
    
    if not os.path.exists(input_file):
        print(f"HATA: {input_file} bulunamadı! Önce Adım 5'i çalıştırın.")
        return

    df = pd.read_excel(input_file)
    kritik_sutunlar = ["İsim", "Yaş", "Kimlik No", "Meslek", "Yıllık Gelir", "Aylık Net Maaş", "Kredi Türü"]
    
    audit_results = {}
    ozet_tablo = []
    
    start_time = time.time()
    
    for i, col in enumerate(kritik_sutunlar):
        progress_bar(i, len(kritik_sutunlar), start_time, prefix=f'Denetim: {col[:10]}')
        
        # Müşteri bazlı grupla ve benzersiz değerleri topla
        grouped = df.groupby("Müşteri ID")[col].apply(lambda x: list(set(x.dropna().astype(str))))
        
        col_audit = pd.DataFrame(grouped).reset_index()
        col_audit.columns = ["Müşteri ID", "Mevcut Değerler"]
        col_audit["Benzersiz Sayı"] = col_audit["Mevcut Değerler"].apply(len)
        col_audit["Durum"] = "X" # Varsayılan hata
        
        # Tik (✓) Mantığı
        if col == "Yaş":
            def yas_kontrol(vals):
                if len(vals) == 0: return "X"
                nums = sorted([float(v) for v in vals])
                if len(nums) == 1: return "✓"
                if len(nums) == 2 and abs(nums[0] - nums[1]) == 1: return "✓"
                return "X"
            col_audit["Durum"] = col_audit["Mevcut Değerler"].apply(yas_kontrol)
        elif col in ["Yıllık Gelir", "Aylık Net Maaş"]:
            def finans_kontrol(vals):
                if len(vals) == 0: return "X"
                nums = sorted([float(v) for v in vals])
                if len(nums) == 1: return "✓"
                # %30'dan az fark varsa tutarlı kabul et (Zam/Prim payı)
                if (max(nums) - min(nums)) / min(nums) <= 0.30: return "✓"
                return "X"
            col_audit["Durum"] = col_audit["Mevcut Değerler"].apply(finans_kontrol)
        else:
            # Statik Sütunlar: Sadece 1 benzersiz değer olmalı
            col_audit.loc[col_audit["Benzersiz Sayı"] == 1, "Durum"] = "✓"
            col_audit.loc[col_audit["Benzersiz Sayı"] == 0, "Durum"] = "X" # Hepsi boşsa hata

        # Rapor Sayfası Hazırlığı
        col_audit["Mevcut Değerler"] = col_audit["Mevcut Değerler"].apply(lambda x: ", ".join(x))
        # Hatalıları (X) en başa al
        col_audit = col_audit.sort_values(by="Durum", ascending=True)
        audit_results[col] = col_audit[["Müşteri ID", "Durum", "Mevcut Değerler"]]
        
        # Özet Veri
        basarili = (col_audit["Durum"] == "✓").sum()
        hatali = (col_audit["Durum"] == "X").sum()
        toplam = len(col_audit)
        ozet_tablo.append({
            "Sütun Adı": col,
            "Başarılı (✓)": basarili,
            "Hatalı (X)": hatali,
            "Toplam Müşteri": toplam,
            "Başarı Oranı (%)": round((basarili/toplam)*100, 2)
        })

    # Henüz denetlenmemiş sütunları bul
    tum_sutunlar = df.columns.tolist()
    denetlenmemis = [c for c in tum_sutunlar if c not in kritik_sutunlar and c not in ["ID", "Müşteri ID", "Ay"]]
    
    progress_bar(len(kritik_sutunlar), len(kritik_sutunlar), start_time, prefix='Tamamlandı')
    
    # EXCEL KAYIT
    print(f"\n\n> Denetim Raporu hazırlanıyor: {output_file}")
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Özet Tabloyu Yaz
        pd.DataFrame(ozet_tablo).to_excel(writer, sheet_name='GENEL ÖZET', index=False)
        
        # Denetlenmemiş Sütunlar Listesini Yaz (Özetin hemen altına veya yanına)
        df_denetlenmemis = pd.DataFrame({"KONTROL EDİLMEMİŞ SÜTUNLAR": denetlenmemis})
        df_denetlenmemis.to_excel(writer, sheet_name='GENEL ÖZET', index=False, startcol=7) # G sütununa yaz
        
        for col_name, res_df in audit_results.items():
            res_df.to_excel(writer, sheet_name=col_name[:31], index=False)
            
    print("\nDENETİM TAMAMLANDI!")
    print(f"Genel Özet: {ozet_tablo[0]['Başarı Oranı (%)']}% ile {ozet_tablo[-1]['Başarı Oranı (%)']}% arası tutarlılık.")

if __name__ == "__main__":
    tutarlilik_denetimi()

# --- GÖRSELLEŞTİRME EKLEMESİ (ADIM 6) ---
def gorsel_olustur_adim6():
    print("\n> Akademik Görseller Hazırlanıyor (Adım 6)...")
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "6_Veri_Tutarlilik_Denetimi")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Raporu geri okuyalım (Özet tablo için)
    ozet_df = pd.read_excel(output_file, sheet_name='GENEL ÖZET')
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(2, 2)

    # 1. Sütun Bazlı Başarı Oranları (Bar)
    ax1 = fig.add_subplot(gs[0, 0])
    sns.barplot(x="Sütun Adı", y="Başarı Oranı (%)", data=ozet_df, palette="Blues_d", ax=ax1, hue="Sütun Adı", legend=False)
    ax1.axhline(95, color='#c0392b', linestyle='--', alpha=0.5)
    ax1.set_title("Şekil 6.1: Veri Alanı Bazlı Tutarlılık Skorları")
    ax1.set_ylim(0, 110)
    for p in ax1.patches:
        ax1.annotate(f'%{p.get_height():.1f}', (p.get_x() + p.get_width()/2., p.get_height()), ha='center', va='bottom', fontweight='bold')

    # 2. Genel Bütünlük (Donut)
    ax2 = fig.add_subplot(gs[0, 1])
    tik = ozet_df["Başarılı (✓)"].sum()
    carpi = ozet_df["Hatalı (X)"].sum()
    ax2.pie([tik, carpi], labels=['Tutarlı Kayıtlar', 'Tutarsız / Onarılması Gereken'], 
            autopct='%1.1f%%', colors=['#27ae60', '#e74c3c'], startangle=90, wedgeprops={'width':0.4, 'edgecolor': 'white'})
    ax2.set_title("Şekil 6.2: Genel Veri Seti Bütünlük Oranı")

    # 3. Hata Detay Tablosu
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    hatalilar = ozet_df.sort_values(by="Hatalı (X)", ascending=False)
    table_data = [["Özellik", "Hatalı Kayıt Sayısı", "Başarı Oranı (%)"]] + hatalilar[["Sütun Adı", "Hatalı (X)", "Başarı Oranı (%)"]].values.tolist()
    tab = ax3.table(cellText=table_data, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(11); tab.scale(1, 2)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        else: cell.set_facecolor('#f8f9fa')
    ax3.set_title("Tablo 6.1: Veri Alanı Bazlı Forensic Denetim Bulguları", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_6_Konsolide_Rapor.png"))
    plt.close()
    print(f"Görseller kaydedildi: {gorsel_dir}")

# Görselleştirmeyi çalıştır
if os.path.exists(output_file):
    gorsel_olustur_adim6()
