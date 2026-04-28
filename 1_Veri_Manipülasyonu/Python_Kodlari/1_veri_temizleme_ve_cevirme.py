import pandas as pd
import os
import shutil
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# Ana dizini bul ve sys.path'e ekle (kullanici.py'yi import edebilmek için)
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    # Eğer kullanici.py bulunamazsa (doğrudan bu klasörde çalıştırılırsa) yedek yol
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

input_dir = os.path.join(base_path, "0_Dataset")
output_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "1_Format_ve_Ceviri")

def clear_outputs(directory):
    if os.path.exists(directory):
        print(f"Eski çıktılar siliniyor: {directory}")
        shutil.rmtree(directory)
    os.makedirs(directory)

# Çıktı klasörünü temizle
clear_outputs(output_dir)

# Çeviri Sözlükleri
column_translation = {
    "ID": "ID",
    "Customer_ID": "Müşteri ID",
    "Month": "Ay",
    "Name": "İsim",
    "Age": "Yaş",
    "SSN": "Kimlik No",
    "Occupation": "Meslek",
    "Annual_Income": "Yıllık Gelir",
    "Monthly_Inhand_Salary": "Aylık Net Maaş",
    "Num_Bank_Accounts": "Banka Hesabı Sayısı",
    "Num_Credit_Card": "Kredi Kartı Sayısı",
    "Interest_Rate": "Faiz Oranı",
    "Num_of_Loan": "Kredi Sayısı",
    "Type_of_Loan": "Kredi Türü",
    "Delay_from_due_date": "Ödeme Gecikme Günü",
    "Num_of_Delayed_Payment": "Geciken Ödeme Sayısı",
    "Changed_Credit_Limit": "Kredi Limiti Değişimi",
    "Num_Credit_Inquiries": "Kredi Sorgu Sayısı",
    "Credit_Mix": "Kredi Karışımı",
    "Outstanding_Debt": "Toplam Borç",
    "Credit_Utilization_Ratio": "Kredi Kullanım Oranı",
    "Credit_History_Age": "Kredi Geçmişi Yaşı",
    "Payment_of_Min_Amount": "Minimum Ödeme Tutarı",
    "Total_EMI_per_month": "Toplam Aylık Taksit",
    "Amount_invested_monthly": "Aylık Yatırım Tutarı",
    "Payment_Behaviour": "Ödeme Davranışı",
    "Monthly_Balance": "Aylık Bakiye",
    "Credit_Score": "Kredi Skoru"
}

month_translation = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan",
    "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos",
    "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}

occupation_translation = {
    "Scientist": "Bilim İnsanı", "Teacher": "Öğretmen", "Engineer": "Mühendis",
    "Entrepreneur": "Girişimci", "Developer": "Geliştirici", "Lawyer": "Avukat",
    "Media_Manager": "Medya Yöneticisi", "Doctor": "Doktor", "Journalist": "Gazeteci",
    "Manager": "Yönetici", "Accountant": "Muhasebeci", "Musician": "Müzisyen",
    "Mechanic": "Tamirci", "Writer": "Yazar", "Architect": "Mimar",
    "_______": "Belirtilmemiş"
}

credit_mix_translation = {
    "Good": "İyi", "Standard": "Standart", "Bad": "Kötü", "_": "Belirtilmemiş"
}

loan_type_translation = {
    "Credit-Builder Loan": "Kredi Geliştirme Kredisi",
    "Home Equity Loan": "Ev Özsermaye Kredisi",
    "Payday Loan": "Hızlı Kredi",
    "Student Loan": "Öğrenci Kredisi",
    "Debt Consolidation Loan": "Borç Yapılandırma Kredisi",
    "Personal Loan": "Bireysel Kredi",
    "Auto Loan": "Araç Kredisi",
    "Mortgage Loan": "Konut Kredisi",
    "Not Specified": "Belirtilmemiş",
    " and ": " ve "
}

payment_behaviour_translation = {
    "High_spent_Small_value_payments": "Yüksek Harcama Düşük Ödeme",
    "Low_spent_Large_value_payments": "Düşük Harcama Yüksek Ödeme",
    "Low_spent_Medium_value_payments": "Düşük Harcama Orta Ödeme",
    "Low_spent_Small_value_payments": "Düşük Harcama Düşük Ödeme",
    "High_spent_Medium_value_payments": "Yüksek Harcama Orta Ödeme",
    "High_spent_Large_value_payments": "Yüksek Harcama Yüksek Ödeme",
    "!@9#%8": "Geçersiz"
}

credit_score_translation = {
    "Good": "İyi", "Standard": "Standart", "Poor": "Kötü"
}

yes_no_translation = {"Yes": "Evet", "No": "Hayır", "NM": "Belirtilmemiş"}

def clean_and_translate(file_name):
    print(f"İşleniyor: {file_name}")
    file_path = os.path.join(input_dir, file_name)
    
    # CSV Oku (Ayırıcı virgül)
    df = pd.read_csv(file_path, low_memory=False)
    
    # 1. İçerik Çevirisi
    if "Month" in df.columns:
        df["Month"] = df["Month"].map(month_translation).fillna(df["Month"])
    if "Occupation" in df.columns:
        df["Occupation"] = df["Occupation"].map(occupation_translation).fillna(df["Occupation"])
    if "Credit_Mix" in df.columns:
        df["Credit_Mix"] = df["Credit_Mix"].map(credit_mix_translation).fillna(df["Credit_Mix"])
    if "Payment_Behaviour" in df.columns:
        df["Payment_Behaviour"] = df["Payment_Behaviour"].map(payment_behaviour_translation).fillna(df["Payment_Behaviour"])
    if "Credit_Score" in df.columns:
        df["Credit_Score"] = df["Credit_Score"].map(credit_score_translation).fillna(df["Credit_Score"])
    if "Payment_of_Min_Amount" in df.columns:
        df["Payment_of_Min_Amount"] = df["Payment_of_Min_Amount"].map(yes_no_translation).fillna(df["Payment_of_Min_Amount"])
        
    # Kredi Türü (Type_of_Loan) Çevirisi
    if "Type_of_Loan" in df.columns:
        df["Type_of_Loan"] = df["Type_of_Loan"].astype(str)
        for eng, tr in loan_type_translation.items():
            df["Type_of_Loan"] = df["Type_of_Loan"].str.replace(eng, tr, regex=False)

    # Kredi Geçmişi Yaşı Çevirisi (Örn: 22 Years and 4 Months -> 22 Yıl ve 4 Ay)
    if "Credit_History_Age" in df.columns:
        df["Credit_History_Age"] = df["Credit_History_Age"].astype(str).str.replace("Years", "Yıl").str.replace("and", "ve").str.replace("Months", "Ay").str.replace("Month", "Ay")

    # 2. Sütun Adlarını Çevir ve Alt Çizgileri Kaldır
    df.rename(columns=column_translation, inplace=True)
    df.columns = [col.replace("_", " ") for col in df.columns]
    
    # 3. Excel Olarak Kaydet
    output_file = os.path.join(output_dir, file_name.replace(".csv", ".xlsx"))
    df.to_excel(output_file, index=False)
    print(f"Tamamlandı: {output_file}")

# Dosyaları işle
clean_and_translate("egitim_verisi.csv")
clean_and_translate("test_verisi.csv")

print("\nTüm işlemler başarıyla tamamlandı!")

# --- GÖRSELLEŞTİRME EKLEMESİ (ADIM 1) ---
def gorsel_olustur_adim1():
    print("\n> Pedagojik Görseller Hazırlanıyor (Adım 1)...")
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "1_Format_ve_Ceviri")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    plt.style.use('seaborn-v0_8-pastel')

    # 1. Çeviri Oranı (Donut Chart)
    plt.figure(figsize=(8,8))
    translated_cols = len(column_translation)
    total_cols = 28 # Yaklaşık
    plt.pie([translated_cols, total_cols - translated_cols], 
            labels=['Çevrilen Sütunlar', 'Sayısal/Sabitler'], 
            autopct='%1.1f%%', colors=['#2ecc71', '#3498db'], startangle=90, wedgeprops={'width':0.4})
    plt.title("Veri Seti Türkçe Dil Dönüşüm Oranı", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "1_ceviri_orani_donut.png"))
    plt.close()

    # 2. Before-After Karşılaştırma Tablosu (Kapsamlı Forensik Kanıt)
    print("> Kapsamlı Before-After Tablosu Hazırlanıyor...")
    try:
        # Karşılaştırma için en kritik 8 sütunu seçelim
        target_cols_raw = ["ID", "Month", "Age", "Occupation", "Annual_Income", "Monthly_Inhand_Salary", "Num_Bank_Accounts", "Credit_Mix"]
        target_cols_clean = ["ID", "Ay", "Yaş", "Meslek", "Yıllık Gelir", "Aylık Net Maaş", "Banka Hesabı Sayısı", "Kredi Karışımı"]
        
        # Ham veriyi oku (İlk 8 satır)
        raw_path = os.path.join(base_path, "0_Dataset", "egitim_verisi.csv")
        raw_df = pd.read_csv(raw_path, nrows=8)[target_cols_raw]
        
        # Temizlenmiş veriyi oku (İlk 8 satır)
        clean_path = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "1_Format_ve_Ceviri", "egitim_verisi.xlsx")
        clean_df = pd.read_excel(clean_path, nrows=8)[target_cols_clean]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
        ax1.axis('off')
        ax2.axis('off')
        
        # Before Tablosu
        t1 = ax1.table(cellText=raw_df.values, colLabels=raw_df.columns, loc='center', cellLoc='left')
        t1.auto_set_font_size(False); t1.set_fontsize(8)
        t1.scale(1, 1.8) # Tabloyu dikeyde uzat
        ax1.set_title("1. ADIM: ÖNCE (HAM VERİ - NOISY & ENGLISH)", fontsize=14, fontweight='bold', color='#c0392b', pad=20)
        
        # After Tablosu
        t2 = ax2.table(cellText=clean_df.values, colLabels=clean_df.columns, loc='center', cellLoc='left')
        t2.auto_set_font_size(False); t2.set_fontsize(8)
        t2.scale(1, 1.8) # Tabloyu dikeyde uzat
        ax2.set_title("1. ADIM: SONRA (TEMİZLENMİŞ VERİ - CLEAN & TÜRKÇE)", fontsize=14, fontweight='bold', color='#27ae60', pad=20)
        
        plt.tight_layout()
        plt.savefig(os.path.join(gorsel_dir, "2_before_after_karsilastirma.png"), dpi=300)
        plt.close()
    except Exception as e:
        print(f"Uyarı: Kapsamlı Before-After görseli oluşturulamadı: {e}")

    
    print(f"Görseller kaydedildi: {gorsel_dir}")

gorsel_olustur_adim1()
