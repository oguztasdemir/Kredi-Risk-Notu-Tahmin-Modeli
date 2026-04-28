import pandas as pd
import numpy as np
import os
import sys
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Ana dizini bul
ana_dizin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ana_dizin)

try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = r"c:\Users\User\Desktop\Kredi Hesaplaması"

# Yollar
input_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "12_Kategorik_Kodlama", "ml_hazir_sayisal_veri.xlsx")
model_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "10_Stacking_Model", "champion_stacking_final.joblib")
bridge_path = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Modeller", "selected_features.joblib")
output_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Ciktilar", "15_Final_Denetim")
gorsel_dir = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Gorseller", "15_Final_Denetim")

def setup_folders():
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(gorsel_dir, exist_ok=True)

def final_forensic_audit_3415():
    print("\n" + "="*60)
    print("PHASE 3 - ADIM 15: FİNAL DENETİM VE HATA ANALİZİ RAPORU")
    print("="*60)
    
    setup_folders()
    
    if not os.path.exists(model_path) or not os.path.exists(bridge_path):
        print("HATA: Model veya Özellik köprüsü bulunamadı! Önce Adım 8 ve 10'u çalıştırın.")
        return

    # 1. Veri ve Model Yükleme
    print("> Veri ve Şampiyon Model yükleniyor...")
    df = pd.read_excel(input_file)
    df_labeled = df[df["Kredi Skoru"].notna()].copy()
    
    model = joblib.load(model_path)
    selected_features = joblib.load(bridge_path)
    
    # 2. Tahminleme
    X = df_labeled[selected_features]
    y_true = df_labeled["Kredi Skoru"]
    y_pred = model.predict(X)
    
    # 3. Rapor Hazırlama (Sheet 1: Detay)
    # Sınıf isimlerini geri yükleyelim
    label_map = {0.0: "İyi", 1.0: "Standart", 2.0: "Kötü"}
    
    audit_df = pd.DataFrame({
        'Kullanıcı Adı': df_labeled['İsim'],
        'Dönem (Ay)': df_labeled['Ay'],
        'Gerçekteki Sınıf': [label_map[v] for v in y_true],
        'Tahmin Sınıfı': [label_map[v] for v in y_pred],
        'Hata (Yanlışsa 1)': (y_true != y_pred).astype(int)
    })
    
    # 4. Model Güvenilirliği (Sheet 2: Overfit ve Leakage Kontrolü)
    print("> Model Güvenilirliği testleri yapılıyor...")
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    X_train, X_val, y_train, y_val_split = train_test_split(X, y_true, test_size=0.2, random_state=42, stratify=y_true)
    train_acc = accuracy_score(y_train, model.predict(X_train))
    val_acc = accuracy_score(y_val_split, model.predict(X_val))
    overfit_gap = (train_acc - val_acc) * 100
    
    # Leakage kontrolü (Korelasyon > 0.95 olan var mı?)
    correlations = df_labeled[selected_features + ["Kredi Skoru"]].corr()['Kredi Skoru'].abs().sort_values(ascending=False)
    high_corr_features = correlations[correlations > 0.95].index.tolist()
    high_corr_features.remove("Kredi Skoru")
    leakage_status = "GÜVENLİ (Sızıntı Yok)" if len(high_corr_features) == 0 else f"RİSKLİ ({', '.join(high_corr_features)})"
    
    reliability_df = pd.DataFrame({
        'Kontrol Tipi': ['Ezberleme (Overfit) Kontrolü', 'Veri Sızıntısı (Leakage) Kontrolü', 'Eğitim Doğruluğu', 'Test Doğruluğu', 'Performans Farkı (Gap)'],
        'Sonuç / Değer': [
            "MÜKEMMEL" if overfit_gap < 15 else "RİSKLİ",
            leakage_status,
            f"%{train_acc*100:.2f}",
            f"%{val_acc*100:.2f}",
            f"%{overfit_gap:.2f}"
        ],
        'Açıklama': [
            'Eğitim ve Test başarıları arasındaki farkın %15\'ten az olması istenir.',
            'Hiçbir özellik hedef değişkeni %95\'ten fazla açıklamamalıdır.',
            'Modelin kendi gördüğü verideki başarısı.',
            'Modelin hiç görmediği verideki başarısı.',
            'Pozitif değer modelin ezberleme eğilimini gösterir.'
        ]
    })
    
    # 5. Özet Tablo (Sheet 1)
    accuracy = (1 - audit_df['Hata (Yanlışsa 1)'].mean()) * 100
    summary_df = pd.DataFrame({
        'Metrik': ['Toplam Kayıt', 'Doğru Tahmin', 'Hatalı Tahmin', 'Genel Başarı Oranı (%)'],
        'Değer': [
            len(audit_df),
            len(audit_df[audit_df['Hata (Yanlışsa 1)'] == 0]),
            len(audit_df[audit_df['Hata (Yanlışsa 1)'] == 1]),
            f"%{accuracy:.2f}"
        ]
    })
    
    # 6. Excel'e Kaydet (YENİ SIRA: Özet -> Güvenilirlik -> Detay)
    excel_path = os.path.join(output_dir, "Final_Model_Denetim_Raporu.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='1_Genel_Ozet', index=False)
        reliability_df.to_excel(writer, sheet_name='2_Model_Guvenilirligi', index=False)
        audit_df.to_excel(writer, sheet_name='3_Detayli_Denetim', index=False)
    
    print(f"> Excel Raporu (3 Sayfa) oluşturuldu: {excel_path}")
    
    # 7. Görselleştirme
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    counts = audit_df['Hata (Yanlışsa 1)'].value_counts().rename(index={0: 'Doğru', 1: 'Hatalı'})
    colors = ['#2ecc71', '#e74c3c']
    
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=colors, explode=(0, 0.1), shadow=True)
    plt.title(f"Final Model Denetimi: Genel Doğruluk Payı\n(Başarı: %{accuracy:.2f})", fontweight='bold')
    
    plt.savefig(os.path.join(gorsel_dir, "Figure_15_1_Audit_Success.png"), dpi=300)
    plt.close()
    
    # 8. YENİ: Özet Tabloyu Görsel Olarak Hazırla (Sunum için)
    plt.figure(figsize=(8, 4))
    plt.axis('off')
    tbl = plt.table(cellText=summary_df.values, colLabels=summary_df.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(14)
    tbl.scale(1.2, 2.5)
    
    # Tablo Renklendirme
    for i in range(len(summary_df.columns)):
        tbl[(0, i)].set_facecolor('#2ecc71')
        tbl[(0, i)].set_text_props(color='white', weight='bold')
    
    plt.title("ADIM 15: FİNAL MODEL DENETİM ÖZETİ", fontweight='bold', pad=20)
    plt.savefig(os.path.join(gorsel_dir, "Figure_15_2_Audit_Table.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"> Özet Tablo Görseli hazır: Figure_15_2_Audit_Table.png")
    print("="*60 + "\nİŞLEM BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    final_forensic_audit_3415()
