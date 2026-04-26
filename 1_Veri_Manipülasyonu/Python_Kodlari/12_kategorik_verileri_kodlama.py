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
    print("\n> Çocuk Dostu Görseller Hazırlanıyor (Adım 12)...")
    plt.style.use('seaborn-v0_8-pastel')
    
    # 1. Kodlama Özeti (Pie)
    plt.figure(figsize=(8,8))
    encoded_count = len(mappings)
    numerical_count = len(df_encoded.columns) - encoded_count
    plt.pie([encoded_count, numerical_count], labels=['Kodlanan (Metin)', 'Zaten Sayısal'], autopct='%1.1f%%', colors=['#f39c12', '#3498db'], startangle=90)
    plt.title("Veri Setimiz Sayısallaştı!", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_kodlama_ozeti_pie.png"))
    plt.close()

    # 2. Hedef Değişken (Kredi Skoru) Kodlama Mantığı
    if "Kredi Skoru" in mappings:
        plt.figure(figsize=(10,6))
        m = mappings["Kredi Skoru"]
        sorted_m = sorted(m.items(), key=lambda x: x[1])
        labels, values = zip(*sorted_m)
        sns.barplot(x=list(values), y=list(labels), palette="viridis")
        plt.title("Kredi Skoru: Kim Hangi Puanı Aldı?", fontsize=14)
        for i, v in enumerate(values):
            plt.text(v + 0.1, i, str(v), color='black', va='center', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "2_kredi_skoru_mantigi.png"))
        plt.close()

    # 3-7. Önemli Sütunların Dağılımı (5 Adet)
    cols_to_plot = [c for c in mappings.keys() if c != "Kredi Skoru"][:5]
    for i, col in enumerate(cols_to_plot):
        plt.figure(figsize=(10,6))
        counts = df_original[col].value_counts().head(10)
        sns.barplot(x=counts.values, y=counts.index, palette="husl")
        plt.title(f"{col} - En Sık Geçen 10 Kategori", fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, f"{i+3}_{col}_dagilim.png"))
        plt.close()

    # 8. Dönüşüm Başarısı (Gauge)
    plt.figure(figsize=(6,4))
    plt.text(0.5, 0.5, "HAZIR", fontsize=80, color='#2ecc71', ha='center', va='center', fontweight='bold')
    plt.text(0.5, 0.2, "Model Eğitimi İçin %100 Sayısal", fontsize=16, color='#27ae60', ha='center')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "8_donusum_hazir_bayragi.png"))
    plt.close()

    # 9. Isı Haritası (Kısmi - Kodlanmış Sütunlar)
    plt.figure(figsize=(12,8))
    encoded_cols = list(mappings.keys())
    sns.heatmap(df_encoded[encoded_cols].corr(), annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title("Kodlanmış Sütunlar Arasındaki İlişki", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "9_kodlanmis_korelasyon.png"))
    plt.close()

    # 10. Veri Tipi Değişimi (Before vs After)
    plt.figure(figsize=(10,6))
    plt.bar(['Eski (Object)', 'Yeni (Sayısal)'], [encoded_count, len(df_encoded.columns)], color=['#e74c3c', '#2ecc71'])
    plt.title("Veri Tiplerindeki Büyük Değişim", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "10_tip_degisimi_bar.png"))
    plt.close()

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
