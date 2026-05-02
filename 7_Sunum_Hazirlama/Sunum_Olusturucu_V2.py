import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_professional_presentation():
    prs = Presentation()

    def add_slide(title, subtitle, content_list=None, image_path=None):
        slide_layout = prs.slide_layouts[1] # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        title_shape = slide.shapes.title
        title_shape.text = title
        
        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        
        if content_list:
            for item in content_list:
                p = tf.add_paragraph()
                p.text = item
                p.level = 0
        
        if image_path and os.path.exists(image_path):
            slide.shapes.add_picture(image_path, Inches(5), Inches(2), width=Inches(4))

    # Slide 1: Title
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "Kredi Skoru Sınıflandırma ve Hibrit AI Modeli"
    slide.placeholders[1].text = "Forensic Veri Analizi ve Optimize Edilmiş Modelleme\nAkademik Proje Final Sunumu v2"

    # Slide 2: Faz 1 - Veri Manipülasyonu
    add_slide("Faz 1: Veri Manipülasyonu ve Restorasyon", 
              "Veri Onarımı ve Temizliği",
              ["ID bazlı trend analizi ile eksik veri tamamlama", 
               "Anomali tespiti ve Median/Pattern onarımı",
               "Kategorik verilerin sayısal dönüşümü"])

    # Slide 3: Faz 2 - Özellik Seçimi (RFE & UMAP) - HOCANIN İSTEĞİ ÜZERİNE BURAYA TAŞINDI
    add_slide("Faz 2: Özellik Mühendisliği (RFE & UMAP)", 
              "Boyut İndirgeme ve Kritik Özellik Seçimi",
              ["RFE (Recursive Feature Elimination): En yüksek tahmin gücü olan 20 özellik seçildi.",
               "UMAP/t-SNE: Verinin manifold düzleminde kümelenme başarısı doğrulandı.",
               "Data Leakage Kontrolü: Bağımlı değişkenle sızıntı yapan sütunlar elendi."])

    # Slide 4: Faz 3 - Modelleme Stratejisi
    add_slide("Faz 3: Modelleme ve Hibrit Mimari", 
              "Voting ve Stacking Ensemble",
              ["XGBoost, RandomForest ve ExtraTrees tabanlı hibrit Voting sistemi.",
               "Optuna ile Bayesian Hiperparametre Optimizasyonu.",
               "Modellerin zayıf yanlarını birbirini dengeleyecek şekilde ağırlıklandırılması."])

    # Slide 5: Hibrit Model Ağırlıkları (HOCANIN İSTEĞİ ÜZERİNE DETAYLANDIRILDI)
    add_slide("Hibrit Model: Çalışma Prensibi ve Ağırlıklar", 
              "Weights & Ensemble Logic",
              ["Şampiyon Model: Soft Voting Classifier",
               "Ağırlık Dağılımı: XGBoost (%44.7) | RandomForest (%43.8) | ExtraTrees (%11.5)",
               "Ağırlık Mantığı: XGBoost'un yüksek varyans başarısı, RF'in genelleme yeteneği ile harmanlanmıştır."])

    # Slide 6: Sonuçlar - Başarı Metrikleri
    add_slide("Nihai Sonuçlar ve Başarı Analizi", 
              "Model Karşılaştırma",
              ["Test Doğruluğu: %81.31",
               "F1-Skoru (Weighted): 0.8124",
               "MAE: 0.18 | RMSE: 0.42",
               "Hybrid model, tekil modellere göre %3.2 daha yüksek kararlılık göstermiştir."])

    # Slide 7: Sonuç - Proje Özeti
    add_slide("Sonuç ve Değerlendirme", 
              "Summary",
              ["Veri sızıntısından arındırılmış güvenilir tahminleme.",
               "Geliştirilen boru hattı 50.000+ yeni veri için anlık tahmin üretebilmektedir.",
               "Modeller .joblib formatında saklanarak üretime hazır hale getirilmiştir."])

    output_path = "c:\\Users\\User\\Desktop\\Kredi Hesaplaması\\5_Sunum\\Sunum_Final_V2.pptx"
    prs.save(output_path)
    print(f"Sunum başarıyla kaydedildi: {output_path}")

if __name__ == "__main__":
    create_professional_presentation()
