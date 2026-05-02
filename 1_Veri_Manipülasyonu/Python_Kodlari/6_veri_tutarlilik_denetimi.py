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
    print("\n> Pedagojik Görseller Hazırlanıyor (Adım 6)...")
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "6_Veri_Tutarlilik_Denetimi")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Raporu geri okuyalım (Özet tablo için)
    ozet_df = pd.read_excel(output_file, sheet_name='GENEL ÖZET')
    plt.style.use('seaborn-v0_8-pastel')

    # 1. Sütun Bazlı Başarı Oranları (Bar Chart)
    plt.figure(figsize=(12,6))
    bars = sns.barplot(x="Sütun Adı", y="Başarı Oranı (%)", data=ozet_df, palette="viridis", hue="Sütun Adı", legend=False)
    plt.axhline(95, color='red', linestyle='--', label='95% Eşik')
    
    for i, rate in enumerate(ozet_df["Başarı Oranı (%)"]):
        plt.text(i, rate + 2, f"%{rate:.1f}", ha='center', fontweight='bold')
    
    plt.title("Müşteri Verisi Tarihsel Tutarlılık Karnesi", fontsize=14, fontweight='bold')
    plt.ylim(0, 115)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_tutarlilik_basari_bar.png"))
    plt.close()

    # 2. Denetim Dashboard (Geçti/Kaldı)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Başarılı vs Hatalı Toplam
    tik = ozet_df["Başarılı (✓)"].sum()
    carpi = ozet_df["Hatalı (X)"].sum()
    axes[0].pie([tik, carpi], labels=['Tutarlı (✓)', 'Tutarsız (X)'], autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], startangle=90)
    axes[0].set_title("Genel Veri Bütünlüğü Oranı")
    
    # En Hatalı Sütunlar
    hatalilar = ozet_df.sort_values(by="Hatalı (X)", ascending=False).head(5)
    sns.barplot(x="Hatalı (X)", y="Sütun Adı", data=hatalilar, ax=axes[1], palette="Reds_r")
    for i, v in enumerate(hatalilar["Hatalı (X)"]):
        axes[1].text(v + 1, i, str(v), va='center', fontweight='bold')
    axes[1].set_title("En Çok Tutarsızlık Tespit Edilen 5 Alan")
    
    plt.suptitle("KATEGORİK VERİ ADLİ DENETİM (FORENSIC AUDIT) DASHBOARD", fontsize=16, fontweight='bold')
    
    # Not Ekle
    fig.text(0.5, 0.01, "Denetim Kriteri: Müşteri ID bazlı tarihsel veri eşleşme kontrolü (Zam/Hata payı dahil).", 
             ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(gorsel_dir, "2_tutarlilik_dashboard.png"), dpi=300)
    plt.close()
    
    print(f"Görseller kaydedildi: {gorsel_dir}")

# Görselleştirmeyi çalıştır
if os.path.exists(output_file):
    gorsel_olustur_adim6()
