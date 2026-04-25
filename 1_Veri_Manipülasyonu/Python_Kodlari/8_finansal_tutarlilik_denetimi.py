import pandas as pd
import numpy as np
import os
import time
import sys
import shutil

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "7_Finansal_Sutun_Temizligi", "finansal_veriler_temizlenmis_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "8_Finansal_Tutarlilik_Denetimi")

if os.path.exists(output_dir):
    try:
        shutil.rmtree(output_dir)
    except PermissionError:
        print("\n!!! HATA: Excel dosyası açık olabilir. Lütfen 'final_finansal_tutarlilik_denetimi.xlsx' dosyasını kapatın.")
        sys.exit(1)
os.makedirs(output_dir)

output_file = os.path.join(output_dir, "final_finansal_tutarlilik_denetimi.xlsx")

def clean_vals_for_excel(vals):
    clean = []
    for v in vals:
        if pd.isna(v): continue
        if isinstance(v, (np.integer, np.floating)): v = v.item()
        if isinstance(v, float) and v.is_integer(): v = int(v)
        clean.append(v)
    return clean

def detect_anomalies_forensic_v9(col, v_list):
    if not v_list: return [], True
    sorted_v = sorted(v_list)
    is_behavioral = any(x in col for x in ["Bakiye", "Bor", "Tutar", "Taksit", "Oran"])
    
    if any(x in col for x in ["Banka", "Kart", "Says"]): tol = 10
    elif "Faiz" in col: tol = 5
    elif "Sorgu" in col: tol = 25
    elif "Ya" in col: tol = 12
    else: tol = max(1000, np.median(v_list) * 1.5) if len(v_list) > 0 else 1000

    clusters = []
    current_cluster = [sorted_v[0]]
    for i in range(1, len(sorted_v)):
        if sorted_v[i] - sorted_v[i-1] <= tol:
            current_cluster.append(sorted_v[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_v[i]]
    clusters.append(current_cluster)
    
    if is_behavioral:
        # Behavioral verilerde kme says serbest olabilir, sadece ok uaklar anomali
        main_cluster = max(clusters, key=len)
        med_main = np.median(main_cluster)
        anomalies = [x for x in v_list if x > max(50000, med_main * 50) or x < med_main / 50]
        is_tik = len(anomalies) == 0 # Sadece anomali yoksa Tik (Kme saysna taklma)
    else:
        main_cluster = max(clusters, key=len)
        anomalies = [x for x in v_list if x not in main_cluster]
        is_tik = len(clusters) == 1
        
    return anomalies, is_tik

def akilli_finansal_denetim_v9():
    print("\n" + "="*50)
    print("ADIM 8: ULTRA-BALANCED FORENSIC AUDIT (V9)")
    print("="*50)
    
    df = pd.read_excel(input_file, engine='openpyxl')
    
    finansal_sutunlar = [
        "Banka Hesabı Sayısı", "Kredi Kartı Sayısı", "Faiz Oranı", "Kredi Sayısı",
        "Ödeme Gecikme Günü", "Geciken Ödeme Sayısı", "Kredi Limiti Değişimi",
        "Kredi Sorgu Sayısı", "Kredi Karışımı", "Toplam Borç", "Kredi Kullanım Oranı",
        "Kredi Geçmişi Yaşı", "Minimum Ödeme Tutarı", "Toplam Aylık Taksit",
        "Aylık Yatırım Tutarı", "Ödeme Davranışı", "Aylık Bakiye"
    ]
    
    denetim_sonuclari, ozet_veriler = {}, []
    total_customers = df["Müşteri ID"].nunique()
    
    for col in finansal_sutunlar:
        print(f"> Denetleniyor: {col}")
        grouped = df.groupby("Müşteri ID")[col]
        stats = grouped.nunique()
        unique_vals_raw = grouped.apply(lambda x: list(x.unique()))
        anomali_tespitleri, durumlar = [], []
        for vals in unique_vals_raw:
            v = clean_vals_for_excel(vals)
            if col in ["Kredi Karışımı", "Ödeme Davranışı", "Minimum Ödeme Tutarı"]:
                if not v: anomalies, is_tik = [], True
                else:
                    mode_val = max(set(v), key=v.count)
                    anomalies = [x for x in v if x != mode_val]
                    is_tik = len(anomalies) == 0
            else:
                v_num = [x for x in v if isinstance(x, (int, float))]
                anomalies, is_tik = detect_anomalies_forensic_v9(col, v_num)
            durumlar.append("✓" if is_tik else "X")
            anomali_tespitleri.append(str(anomalies) if anomalies else "-")

        report_df = pd.DataFrame({
            "Müşteri ID": stats.index, "Benzersiz Değer Sayısı": stats.values,
            "Alınan Değerler": unique_vals_raw.apply(lambda x: str(clean_vals_for_excel(x))).values,
            "Tespit Edilen Aykırı Değerler": anomali_tespitleri, "Durum": durumlar
        })
        tik_sayisi = sum(1 for d in durumlar if d == "✓")
        basari_orani = round((tik_sayisi/total_customers)*100, 2)
        denetim_sonuclari[col] = (report_df.sort_values(by="Durum", ascending=True), basari_orani)
        ozet_veriler.append({
            "Sütun Adı": col, "Tik (✓) Sayısı": tik_sayisi, "Çarpı (X) Sayısı": total_customers - tik_sayisi,
            "Toplam Müşteri": total_customers, "Başarı Oranı (%)": basari_orani
        })

    ozet_df = pd.DataFrame(ozet_veriler).sort_values(by="Başarı Oranı (%)", ascending=True)
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        ozet_df.to_excel(writer, sheet_name='GENEL ÖZET', index=False)
        for col_name in ozet_df["Sütun Adı"]:
            rdf, _ = denetim_sonuclari[col_name]
            rdf.to_excel(writer, sheet_name=col_name[:31], index=False)

    print("\nDENETİM TAMAMLANDI!")

if __name__ == "__main__":
    akilli_finansal_denetim_v9()
