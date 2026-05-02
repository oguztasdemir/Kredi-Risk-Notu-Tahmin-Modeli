import pandas as pd
import numpy as np
import os
import sys
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# Ana dizini bul ve sys.path'e ekle
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Dosya yolları
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "9_Anomali_Duzeltme", "final_temiz_veri_renkli.xlsx")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama")
gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "12_Kategorik_Kodlama")

if not os.path.exists(output_dir): os.makedirs(output_dir)
if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)

output_file = os.path.join(output_dir, "ml_hazir_sayisal_veri.xlsx")
mapping_file = os.path.join(output_dir, "kodlama_sozlugu_mapping.xlsx")

def gorsel_olustur_adim12(df_original, df_encoded, mappings):
    print("\n> Akademik Görseller Hazırlanıyor (Adım 12)...")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Akademik Stil
    plt.rcParams.update({'font.family': 'sans-serif', 'savefig.dpi': 300})
    
    fig = plt.figure(figsize=(18, 14))
    gs = fig.add_gridspec(3, 2)

    # 12.1 Kodlama Özeti (Pie)
    ax1 = fig.add_subplot(gs[0, 0])
    encoded_count = len(mappings)
    numerical_count = len(df_encoded.columns) - encoded_count
    ax1.pie([encoded_count, numerical_count], labels=['Kodlanan Özellikler', 'Sabit Sayısal Özellikler'], 
            autopct='%1.1f%%', colors=['#f39c12', '#3498db'], startangle=90, wedgeprops={'width':0.4, 'edgecolor': 'white'})
    ax1.set_title("Şekil 12.1: Veri Seti Sayısallaştırma Oranı")

    # 12.2 Hedef Değişken Mantığı (Barh)
    ax2 = fig.add_subplot(gs[0, 1])
    if "Kredi Skoru" in mappings:
        m = mappings["Kredi Skoru"]
        sorted_m = sorted(m.items(), key=lambda x: x[1])
        labels, values = zip(*sorted_m)
        sns.barplot(x=list(values), y=list(labels), palette="viridis", ax=ax2)
        ax2.set_title("Şekil 12.2: Kredi Skoru (Hedef Etiket) Ordinal Kodlama Matrisi")

    # 12.3 Kodlama Dönüşüm Forensik Paneli (Table)
    ax3 = fig.add_subplot(gs[1:, :])
    ax3.axis('off')
    
    target_cols = [c for c in mappings.keys() if c != "Kredi Skoru"][:5]
    before_rows = df_original[target_cols].head(5).values.tolist()
    after_rows = df_encoded[target_cols].head(5).values.tolist()
    
    combined_rows = [["Özellik"] + target_cols]
    for i in range(5):
        combined_rows.append(["ÖNCE (Metin)"] + [str(x) for x in before_rows[i]])
        combined_rows.append(["SONRA (Kod)"] + [str(x) for x in after_rows[i]])
        combined_rows.append(["-" for _ in range(len(target_cols)+1)]) # Ayırıcı
        
    tab = ax3.table(cellText=combined_rows, loc='center', cellLoc='center')
    tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.8)
    for (row, col), cell in tab.get_celld().items():
        if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
        elif "ÖNCE" in cell.get_text().get_text(): cell.set_facecolor('#fff3e0')
        elif "SONRA" in cell.get_text().get_text(): cell.set_facecolor('#e8f5e9')
    ax3.set_title("Tablo 12.1: Veri Dönüşüm Forensik Analizi (Önce vs Sonra)", pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_12_Kodlama_Panel.png"))
    plt.close()
    print(f"Görseller kaydedildi: {gorsel_dir}")

def kodlama_adim12():
    print("\n" + "="*50)
    print("ADIM 12: KATEGORIK VERILERI KODLAMA (LABEL ENCODING)")
    print("="*50)

    # ÖNCEKİ VERİLERİ KONTROL ET (Update Mode)
    if os.path.exists(output_file) and os.path.exists(mapping_file):
        print(f"\n> BİLGİ: Çıktılar zaten mevcut.")
        print("> SADECE GÖRSEL VE RAPORLAR GÜNCELLENİYOR (Update Mode)...")
        df_encoded = pd.read_excel(output_file)
        df_original = pd.read_excel(input_file)
        
        # Mapping oku
        mapping_sheets = pd.read_excel(mapping_file, sheet_name=None)
        mappings = {}
        for sheet_name, m_df in mapping_sheets.items():
            mappings[sheet_name] = dict(zip(m_df.iloc[:,0], m_df.iloc[:,1]))
            
        gorsel_olustur_adim12(df_original, df_encoded, mappings)
        print("\nİŞLEM TAMAMLANDI (Görseller Güncellendi)!")
        return

    # 1. Veriyi Yükle
    print("> Temizlenmiş veri seti yükleniyor...")
    df = pd.read_excel(input_file, engine='openpyxl')
    df_original = df.copy()
    
    # 2. Kodlama Mantığı (Dictionary)
    print("> Kategorik sütunlar tespit ediliyor ve akıllı kodlama uygulanıyor...")
    mappings = {}
    le = LabelEncoder()
    
    # --- AYLAR İÇİN ÖZEL SIRALAMA ---
    if "Ay" in df.columns:
        print("  - 'Ay' sütunu kronolojik olarak kodlanıyor (Ocak=1...Aralık=12)...")
        ay_sirasi = {
            "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, 
            "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
        }
        df["Ay"] = df["Ay"].map(ay_sirasi)
        mappings["Ay"] = ay_sirasi

    # --- KİMLİK NO / ID TEMİZLİĞİ (Sayısal Tutma) ---
    kimlik_cols = ["Kimlik No", "ID", "Müşteri ID"]
    for col in kimlik_cols:
        if col in df.columns:
            print(f"  - '{col}' temizleniyor (Sadece rakamlar tutuluyor)...")
            # Sadece rakamları tut, diğer her şeyi sil
            df[col] = df[col].astype(str).str.replace(r'\D', '', regex=True)
            # Boş kalanları 0 yap veya koru, sonra sayıya çevirmeyi dene
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- HEDEF DEĞİŞKEN (ORDINAL) ---
    if "Kredi Skoru" in df.columns:
        print("  - 'Kredi Skoru' hedef değişkeni ordinal (0,1,2) kodlanıyor...")
        skor_order = {"Kötü": 0, "Standart": 1, "İyi": 2}
        df["Kredi Skoru"] = df["Kredi Skoru"].map(skor_order)
        mappings["Kredi Skoru"] = skor_order

    # --- DİĞER KATEGORİK SÜTUNLAR ---
    obj_cols = df.select_dtypes(include=['object']).columns
    for col in obj_cols:
        if col in mappings: continue # Zaten özel işlem yapıldı
        
        print(f"  - '{col}' kategorik olarak kodlanıyor...")
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        
        # Sözlüğü kaydet
        mappings[col] = dict(zip(le.classes_, le.transform(le.classes_)))

    # 3. Sayısal Veriyi Kaydet
    print("> Sayısal veri seti kaydediliyor...")
    df.to_excel(output_file, index=False)

    # 4. Sözlük (Mapping) Raporunu Kaydet
    print("> Kodlama sözlüğü kaydediliyor...")
    with pd.ExcelWriter(mapping_file, engine='xlsxwriter') as writer:
        for col, m_dict in mappings.items():
            m_df = pd.DataFrame(list(m_dict.items()), columns=['Orijinal Değer', 'Sayısal Kod'])
            m_df.to_excel(writer, sheet_name=col[:31], index=False)

    # 5. Görselleri Oluştur
    gorsel_olustur_adim12(df_original, df, mappings)

    print(f"\nİŞLEM TAMAMLANDI! ")
    print(f"Sayısal Veri: {output_file}")
    print(f"Kodlama Sözlüğü: {mapping_file}")

if __name__ == "__main__":
    kodlama_adim12()
