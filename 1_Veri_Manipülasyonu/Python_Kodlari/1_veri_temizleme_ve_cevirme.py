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
    print("\n> Akademik Görseller Hazırlanıyor (Adım 1)...")
    gorsel_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller", "1_Format_ve_Ceviri")
    if not os.path.exists(gorsel_dir): os.makedirs(gorsel_dir)
    
    # Akademik Stil Ayarları
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 11,
        'savefig.dpi': 300
    })

    # 1. BİRLEŞİK ANALİZ PANELİ (Donut + Örnek Tablo)
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2)
    
    # Sol Üst: Çeviri Oranı Donut
    ax1 = fig.add_subplot(gs[0, 0])
    translated_cols = len(column_translation)
    total_cols = 28 
    ax1.pie([translated_cols, total_cols - translated_cols], 
            labels=['Yerelleştirilen\nÖzellikler', 'Sabit/Sayısal\nVeriler'], 
            autopct='%1.1f%%', colors=['#2980b9', '#ecf0f1'], startangle=90, 
            wedgeprops={'width':0.4, 'edgecolor':'#2c3e50'})
    ax1.set_title("Şekil 1.1: Veri Sözlüğü Yerelleştirme Oranı")

    # Sağ Üst: Temel İstatistik Özeti
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')
    summary_data = [
        ["Metrik", "Değer"],
        ["Toplam Sütun", total_cols],
        ["Çevrilen Sütun", translated_cols],
        ["Meslek Grupları", len(occupation_translation)],
        ["Kredi Türleri", len(loan_type_translation)],
        ["Format", "UTF-8 / Excel"]
    ]
    table_summary = ax2.table(cellText=summary_data, loc='center', cellLoc='center', colWidths=[0.4, 0.4])
    table_summary.auto_set_font_size(False)
    table_summary.set_fontsize(11)
    table_summary.scale(1, 2.5)
    for (row, col), cell in table_summary.get_celld().items():
        if row == 0:
            cell.set_facecolor('#34495e')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor('#f8f9fa')

    # Alt: Before-After Karşılaştırma
    ax3 = fig.add_subplot(gs[1, :])
    ax3.axis('off')
    try:
        target_cols_raw = ["ID", "Month", "Age", "Occupation", "Annual_Income", "Monthly_Inhand_Salary", "Credit_Mix"]
        target_cols_clean = ["ID", "Ay", "Yaş", "Meslek", "Yıllık Gelir", "Aylık Net Maaş", "Kredi Karışımı"]
        raw_path = os.path.join(base_path, "0_Dataset", "egitim_verisi.csv")
        raw_df = pd.read_csv(raw_path, nrows=5)[target_cols_raw]
        clean_path = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "1_Format_ve_Ceviri", "egitim_verisi.xlsx")
        clean_df = pd.read_excel(clean_path, nrows=5)[target_cols_clean]
        
        # Sadece ilk 3 satırı gösterelim daha net olması için
        combined_data = []
        for i in range(3):
            combined_data.append(raw_df.iloc[i].values)
            combined_data.append(clean_df.iloc[i].values)
            
        labels = []
        for i in range(3):
            labels.extend([f"Ham {i+1}", f"Temiz {i+1}"])
            
        table_comp = ax3.table(cellText=combined_data, rowLabels=labels, colLabels=target_cols_clean, loc='center', cellLoc='left')
        table_comp.auto_set_font_size(False)
        table_comp.set_fontsize(9)
        table_comp.scale(1, 2)
        for (row, col), cell in table_comp.get_celld().items():
            if row == 0: cell.set_facecolor('#2c3e50'); cell.set_text_props(color='white')
            elif row % 2 == 0: cell.set_facecolor('#ecf0f1') # Ham satırlar
            else: cell.set_facecolor('#d5f5e3') # Temiz satırlar
            
        ax3.set_title("Tablo 1.1: Ham Veri ve Temizlenmiş Veri Karşılaştırmalı Örneklem", pad=30)
    except Exception as e:
        ax3.text(0.5, 0.5, f"Veri yükleme hatası: {e}", ha='center')

    plt.tight_layout()
    plt.savefig(os.path.join(gorsel_dir, "Adim_1_Konsolide_Rapor.png"))
    plt.close()
    print(f"Görsel kaydedildi: {gorsel_dir}")

gorsel_olustur_adim1()
