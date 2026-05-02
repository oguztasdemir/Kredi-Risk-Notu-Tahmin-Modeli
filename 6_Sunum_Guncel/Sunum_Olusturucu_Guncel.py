import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def copy_project_images(base_path):
    """Proje klasörlerindeki görselleri sunum klasörüne kopyalar ve organize eder."""
    sunum_gorseller_root = os.path.join(base_path, "6_Sunum_Guncel", "gorseller")
    
    # Hedef klasörleri oluştur
    fazlar = {
        "1_Veri_Manipulasyonu": os.path.join(base_path, "1_Veri_Manipülasyonu", "Gorseller"),
        "2_Ozellik_Muhendisligi": os.path.join(base_path, "2_Ozellik_Muhendisligi_ve_Secimi", "Gorseller"),
        "3_Model_Egitimi": os.path.join(base_path, "3_Model_Egitimi_ve_Degerlendirme", "Gorseller")
    }
    
    print("> Görseller organize ediliyor...")
    for faz_adi, src_dir in fazlar.items():
        dest_dir = os.path.join(sunum_gorseller_root, faz_adi)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        if os.path.exists(src_dir):
            folders = [f for f in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, f))]
            # Klasörleri numaralarına göre sırala (1_..., 2_... vb.)
            try:
                folders.sort(key=lambda x: int(x.split('_')[0]))
            except:
                folders.sort()
                
            for folder in folders:
                step_num = folder.split('_')[0]
                src_folder_path = os.path.join(src_dir, folder)
                images = [img for img in os.listdir(src_folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if images:
                    # İlk görseli al ve Adim_X.png olarak kopyala
                    src_img = os.path.join(src_folder_path, images[0])
                    dest_img = os.path.join(dest_dir, f"Adim_{step_num}.png")
                    shutil.copy2(src_img, dest_img)

def create_updated_presentation():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Önce görselleri hazırla
    copy_project_images(base_path)
    
    prs = Presentation()
    
    # Sayfa Boyutu (16:9)
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    def set_background(slide, color_rgb):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color_rgb

    def add_bullet_points(tf, text_list, level=0, font_size=18):
        for text in text_list:
            p = tf.add_paragraph()
            p.text = text
            p.level = level
            p.font.size = Pt(font_size)
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.font.name = 'Calibri'

    def add_transition_slide(title):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_background(slide, RGBColor(13, 27, 42))
        txBox = slide.shapes.add_textbox(0, prs.slide_height/2 - Inches(1), prs.slide_width, Inches(2))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = title
        p.font.bold = True
        p.font.size = Pt(60)
        p.font.color.rgb = RGBColor(212, 175, 55)
        p.alignment = PP_ALIGN.CENTER

    def add_standard_slide(title, points):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_background(slide, RGBColor(13, 27, 42))
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), prs.slide_width - Inches(1), Inches(1))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = title
        p.font.bold = True
        p.font.size = Pt(40)
        p.font.color.rgb = RGBColor(255, 255, 255)
        line = slide.shapes.add_connector(1, Inches(0.5), Inches(1.2), Inches(12.8), Inches(1.2))
        line.line.color.rgb = RGBColor(212, 175, 55)
        line.line.width = Pt(2)
        txContent = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), prs.slide_width - Inches(1), Inches(5))
        tf_c = txContent.text_frame
        tf_c.word_wrap = True
        add_bullet_points(tf_c, points, font_size=18)

    def add_image_slide(title, points, image_path, step_index=0):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_background(slide, RGBColor(13, 27, 42))
        
        # Başlık
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), prs.slide_width - Inches(1), Inches(1))
        tf = txBox.text_frame
        p = tf.add_paragraph()
        p.text = title
        p.font.bold = True
        p.font.size = Pt(32)
        p.font.color.rgb = RGBColor(255, 255, 255)
        
        # Ayrıştırıcı Çizgi
        line = slide.shapes.add_connector(1, Inches(0.5), Inches(1.2), Inches(12.8), Inches(1.2))
        line.line.color.rgb = RGBColor(212, 175, 55)
        line.line.width = Pt(2)

        # Alternatif Yerleşim (Çift sayılarda görsel solda, tek sayılarda sağda)
        is_left = (step_index % 2 == 0)
        
        img_width = Inches(6.5)
        text_width = Inches(5.5)
        
        if os.path.exists(image_path):
            if is_left:
                # Görsel Sol, Metin Sağ
                slide.shapes.add_picture(image_path, Inches(0.5), Inches(1.8), height=Inches(5))
                txContent = slide.shapes.add_textbox(Inches(7.3), Inches(1.8), text_width, Inches(5))
            else:
                # Metin Sol, Görsel Sağ
                txContent = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), text_width, Inches(5))
                slide.shapes.add_picture(image_path, Inches(6.3), Inches(1.8), height=Inches(5))
        else:
            txContent = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), prs.slide_width - Inches(1), Inches(5))

        tf_c = txContent.text_frame
        tf_c.word_wrap = True
        add_bullet_points(tf_c, points, font_size=16)

    # 1. KAPAK (Slayt 1)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, RGBColor(13, 27, 42))
    
    # Üniversite ve Fakülte (Altın Sarısı)
    txBox = slide.shapes.add_textbox(Inches(0), Inches(0.5), prs.slide_width, Inches(1))
    tf = txBox.text_frame
    p = tf.add_paragraph()
    p.text = "İSTANBUL MEDENİYET ÜNİVERSİTESİ"
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = RGBColor(212, 175, 55)
    p.alignment = PP_ALIGN.CENTER
    p = tf.add_paragraph()
    p.text = "Mühendislik ve Doğa Bilimleri Fakültesi | Matematik Bölümü"
    p.font.size = Pt(20)
    p.font.color.rgb = RGBColor(212, 175, 55)
    p.alignment = PP_ALIGN.CENTER

    # Ana Başlık
    txBox2 = slide.shapes.add_textbox(Inches(0), Inches(2.2), prs.slide_width, Inches(2))
    tf2 = txBox2.text_frame
    p2 = tf2.add_paragraph()
    p2.text = "KREDİ NOTU SINIFLANDIRMA"
    p2.font.bold = True
    p2.font.size = Pt(66)
    p2.font.color.rgb = RGBColor(255, 255, 255) # Başlığı Beyaz yaparak vurguladık
    p2.alignment = PP_ALIGN.CENTER
    
    # Danışman (Başlığın hemen altı)
    txBox4 = slide.shapes.add_textbox(Inches(0), Inches(3.8), prs.slide_width, Inches(1))
    tf4 = txBox4.text_frame
    p4 = tf4.add_paragraph()
    p4.text = "Danışman: Dr. Öğr. Üyesi Betül Hiçdurmaz"
    p4.font.bold = True
    p4.font.size = Pt(24)
    p4.font.color.rgb = RGBColor(212, 175, 55)
    p4.alignment = PP_ALIGN.CENTER

    # Proje Ekibi (En Alt)
    txBox3 = slide.shapes.add_textbox(Inches(0), Inches(5.8), prs.slide_width, Inches(1.5))
    tf3 = txBox3.text_frame
    p3 = tf3.add_paragraph()
    p3.text = "PROJE EKİBİ"
    p3.font.bold = True
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(212, 175, 55)
    p3.alignment = PP_ALIGN.CENTER

    p3 = tf3.add_paragraph()
    p3.text = "Oğuz Taşdemir • Ertuğrul Akkuş • Yunus Emre Demir\nRabia Zeynep Sofu • Nisa Gönültaş • Ali Baran Akdoğan"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(240, 240, 240) # Fildişi beyazı (yumuşak beyaz)
    p3.alignment = PP_ALIGN.CENTER

    # 2. ÖNSÖZ (Slayt 2)
    add_standard_slide("ÖNSÖZ VE PROJE AMACI", [
        "• Veri setindeki yapısal bozuklukların ve anomali içeren kayıtların temizlenerek, yüksek hassasiyetli bir kredi risk tahmin modeli geliştirilmesi amaçlanmıştır.",
        "• Müşterilerin 12 aylık finansal davranış örüntüleri, harcama alışkanlıkları ve ödeme sadakati çok boyutlu analiz yöntemleriyle incelenmiştir.",
        "• Geleneksel skorlama yöntemlerinin ötesine geçilerek, gelişmiş makine öğrenmesi algoritmaları ve hibrit mimariler (Stacking) ile karar destek sistemi kurgulanmıştır.",
        "• Proje boyunca veri bütünlüğü ve akademik tarafsızlık ön planda tutulmuş, tüm süreçler denetlenebilir bir pipeline üzerine inşa edilmiştir."
    ])

    # 3. DOSYA DÜZENİ (Slayt 3)
    add_standard_slide("PROJE DOSYA VE KLASÖR DÜZENİ", [
        "• Klasör 1 (Veri Manipülasyonu): Ham verinin işlenmesi, gürültüden arındırılması ve semantik tutarlılığın sağlanması aşamasıdır.",
        "• Klasör 2 (Özellik Mühendisliği): Tahmin gücü en yüksek değişkenlerin istatistiksel metotlarla (RFE, PCA, UMAP) saptanması sürecidir.",
        "• Klasör 3 (Model Eğitimi ve Değerlendirme): Algoritmaların eğitimi, hiperparametre optimizasyonu ve hibrit model validasyonu adımlarını içerir."
    ])

    # 4. KLASÖR 1 ÖZET (Slayt 4)
    add_standard_slide("KLASÖR 1: VERİ MANİPÜLASYONU STRATEJİSİ", [
        "• Karakter kodlama hataları giderilerek tüm veri seti UTF-8 standardına ve Türkçe terminolojiye normalize edilmiştir.",
        "• Kayıp veriler (Missing Values) ve hatalı girişler, veri dağılımını bozmayacak şekilde medyan ve ileri tahmin yöntemleriyle onarılmıştır.",
        "• Finansal sütunlardaki aşırı sapmalar (Outliers), iş mantığı çerçevesinde belirlenen alt ve üst limitlere baskılanmıştır.",
        "• Kategorik veriler, modelin matematiksel olarak işleyebileceği 'Label Encoding' ve 'One-Hot Encoding' protokollerine dönüştürülmüştür."
    ])

    # 5. KLASÖR 2 ÖZET (Slayt 5)
    add_standard_slide("KLASÖR 2: ÖZELLİK MÜHENDİSLİĞİ VE BOYUT İNDİRGEME", [
        "• Özelliklerin kredi notu üzerindeki doğrudan etkisi korelasyon matrisleri ve Random Forest önem sıralaması ile analiz edilmiştir.",
        "• PCA ve Manifold Öğrenme (UMAP) teknikleri kullanılarak veri uzayındaki gizli örüntüler ve kümelenmeler saptanmıştır.",
        "• Recursive Feature Elimination (RFE) yöntemi ile modelin karmaşıklığı azaltılmış ve sinyal-gürültü oranı optimize edilmiştir.",
        "• Belirlenen en kritik 20 özellik, modelin genelleme yeteneğini artırmak amacıyla nihai veri setinde sabitlenmiştir."
    ])

    # 6. KLASÖR 3 ÖZET (Slayt 6)
    add_standard_slide("KLASÖR 3: MODEL MİMARİSİ VE ANALİZ", [
        "• 20'den fazla makine öğrenmesi algoritması üzerinden 'Mega Benchmark' yapılarak en performanslı baz modeller seçilmiştir.",
        "• Bayesian Optimizasyon (Optuna) kullanılarak modellerin hiperparametreleri en yüksek F1-Skorunu verecek şekilde ayarlanmıştır.",
        "• ExtraTrees, XGBoost ve CatBoost tabanlı 'Stacking Ensemble' mimarisi ile %89.38 doğruluk oranına ulaşılmıştır.",
        "• SHAP ve LIME gibi açıklanabilir yapay zeka (XAI) yöntemleri ile modelin bireysel kredi kararları şeffaflaştırılmıştır."
    ])

    # 7. VERİ SETİ BİLGİLERİ (Slayt 7)
    add_standard_slide("VERİ SETİ VE DENETİM STANDARTLARI", [
        "• Veri Kaynağı: Kaggle platformunda paylaşılan gerçek dünya bankacılık verileri baz alınmıştır.",
        "• Örneklem Büyüklüğü: 100.000+ satırlık veri seti, 12 aylık periyodik finansal kayıtları kapsamaktadır.",
        "• Veri Hijyeni: Yapılan restorasyon işlemleri sonucunda veri seti %99.4 oranında temizlik ve tutarlılık seviyesine ulaşmıştır.",
        "• Akademik Uyumluluk: Tüm pipeline adımları, veri sızıntısını (Data Leakage) önleyen bağımsız modüller halinde kurgulanmıştır."
    ])

    # 8. GEÇİŞ: KLASÖR 1 (Slayt 8)
    add_transition_slide("KLASÖR 1: VERİ MANİPÜLASYONU")

    # KLASÖR 1 DETAYLAR
    faz1_steps = [
        ("FORMAT VE ÇEVİRİ", ["• Veri setindeki özel karakterler temizlenmiş ve tüm terminoloji finansal literatüre uygun olarak Türkçeye kazandırılmıştır.", "• Sayısal olması gereken ancak metin formatında olan kolonlar başarıyla dönüştürülmüştür."]),
        ("MÜŞTERİ ID KONTROLÜ", ["• Kayıtların zamansal takibi için müşteri kimlikleri üzerinden benzersizlik ve ardışıklık denetimleri yapılmıştır."]),
        ("VERİ BİRLEŞTİRME", ["• Modelin daha geniş bir perspektifle restorasyon yapabilmesi için eğitim ve test veri blokları güvenli bir şekilde konsolide edilmiştir."]),
        ("DOLULUK ANALİZİ", ["• Veri setindeki boş değerlerin (NaN) yoğunluk haritası çıkarılarak, her değişken için en uygun doldurma stratejisi uygulanmıştır."]),
        ("KRİTİK SÜTUN TEMİZLİĞİ", ["• Yaş, Kimlik No ve Gelir gibi kritik alanlardaki mantıksal hatalar (negatif yaş vb.) iş kuralları çerçevesinde onarılmıştır."]),
        ("VERİ TUTARLILIĞI", ["• Bir müşteriye ait aylık kayıtlar arasında değişmemesi gereken statik bilgilerin zaman içindeki tutarlılığı denetlenmiştir."]),
        ("FİNANSAL TEMİZLİK", ["• Yıllık gelir ve borç miktarlarındaki uçuk rakamlar, istatistiksel güven aralıkları dışına çıkan kayıtlar için normalize edilmiştir."]),
        ("FİNANSAL TUTARLILIK", ["• Aylık ödemelerin toplam borç ve gelirle olan matematiksel tutarlılığı çapraz sorgularla doğrulanmıştır."]),
        ("ANOMALİ DÜZELTME", ["• Veri dağılımını bozan uç değerler (Outliers), verinin orijinal yapısını korumak adına robust istatistik yöntemleriyle baskılanmıştır."]),
        ("KALİTE ANALİZİ", ["• Uygulanan temizlik adımlarının her biri için başarı metrikleri üretilmiş ve veri sağlığı raporlanmıştır."]),
        ("İSTATİSTİKSEL ANALİZ", ["• Özelliklerin dağılımı (Skewness/Kurtosis) ve değişkenler arasındaki multikolinerite riskleri Pearson korelasyon matrisleri ile incelenmiştir."]),
        ("KATEGORİK KODLAMA", ["• Algoritmaların işleyebileceği matematiksel matris yapısı için yüksek kardinaliteli veriler uygun yöntemlerle kodlanmıştır."])
    ]
    for i, (title, desc) in enumerate(faz1_steps, 1):
        img = os.path.join(base_path, "6_Sunum_Guncel", "gorseller", "1_Veri_Manipulasyonu", f"Adim_{i}.png")
        add_image_slide(f"KLASÖR 1 - ADIM {i}: {title}", desc, img, step_index=i)

    # KLASÖR 2 GEÇİŞ
    add_transition_slide("KLASÖR 2: ÖZELLİK MÜHENDİSLİĞİ")
    faz2_steps = [
        ("FİLTRE METODU", ["• Değişkenlerin hedef etiket (Kredi Notu) ile olan doğrusal ve doğrusal olmayan ilişkileri istatistiksel testlerle puanlanmıştır."]),
        ("GÖMÜLÜ METOT", ["• Model tabanlı özellik seçimi yapılarak, algoritmanın kararlarında en çok ağırlık verdiği sütunlar hiyerarşik olarak sıralanmıştır."]),
        ("WRAPPER METODU", ["• Recursive Feature Elimination (RFE) ile en düşük hata oranını veren optimal özellik alt kümesi belirlenmiştir."]),
        ("PCA ANALİZİ", ["• Çok boyutlu verilerdeki varyansın %95'ini temsil eden temel bileşenler hesaplanarak veri karmaşıklığı minimize edilmiştir."]),
        ("MANİFOLD ÖĞRENME", ["• Yüksek boyutlu verilerdeki müşteri segmentasyonları t-SNE ve UMAP algoritmaları ile düşük boyutlu uzayda görselleştirilmiştir."]),
        ("ÖZELLİK ADLİ TIP", ["• Seçilen özelliklerin model performansı üzerindeki etkisi 'Ablation Study' yöntemleriyle derinlemesine analiz edilmiştir."]),
        ("NİHAİ SEÇİM", ["• Tahmin isabetini en üst düzeye çıkaran ve hesaplama maliyetini düşüren nihai 20 özellik model girişi olarak sabitlenmiştir."])
    ]
    for i, (title, desc) in enumerate(faz2_steps, 1):
        img = os.path.join(base_path, "6_Sunum_Guncel", "gorseller", "2_Ozellik_Muhendisligi", f"Adim_{i}.png")
        add_image_slide(f"KLASÖR 2 - ADIM {i}: {title}", desc, img, step_index=i)

    # KLASÖR 3 GEÇİŞ
    add_transition_slide("KLASÖR 3: MODEL EĞİTİMİ VE ANALİZ")
    faz3_steps = [
        ("VERİ HAZIRLIK", ["• Veri seti eğitim ve test bloklarına ayrılmış, özellikler 'StandardScaler' protokolü ile normalize edilmiştir."]),
        ("MODEL KIYASLAMA", ["• Klasik regresyonlardan modern derin öğrenme yaklaşımlarına kadar 20 algoritma aynı veri seti üzerinde kıyaslanmıştır."]),
        ("HİPERPARAMETRE", ["• Optuna çerçevesi kullanılarak her algoritma için en verimli hiperparametre uzayı Bayesian yöntemlerle taranmıştır."]),
        ("HİBRİT MODEL", ["• En başarılı modellerden (XGBoost, CatBoost, ExtraTrees) oluşan gelişmiş bir Stacking mimarisi inşa edilmiştir."]),
        ("VALİDASYON", ["• K-Fold Cross-Validation ve Blind Test yöntemleri ile modelin görmediği veriler üzerindeki genelleme başarısı doğrulanmıştır."]),
        ("FİNAL MODEL", ["• Şampiyon model nihai veri setiyle eğitilmiş ve SHAP öznitelik katkı analizleri ile yorumlanabilir hale getirilmiştir."]),
        ("TAHMİNLER", ["• Üretim ortamına hazır model ile 50.000 kişilik müşteri portföyü üzerinde nihai kredi risk sınıfları atanmıştır."]),
        ("AKADEMİK SONUÇLAR", ["• Model başarısı; Hassasiyet, Geri Çağırma, F1-Skoru ve ROC-AUC gibi akademik metriklerle raporlanmıştır."]),
        ("NİHAİ RAPOR", ["• Tüm pipeline sürecini, veri temizlik oranlarını ve model başarılarını içeren kapsamlı 'Forensic' denetim raporu üretilmiştir."])
    ]
    for i, (title, desc) in enumerate(faz3_steps, 1):
        img = os.path.join(base_path, "6_Sunum_Guncel", "gorseller", "3_Model_Egitimi", f"Adim_{i}.png")
        add_image_slide(f"KLASÖR 3 - ADIM {i}: {title}", desc, img, step_index=i)

    # SONUÇ
    add_standard_slide("PROJE SONUCU VE STRATEJİK ÇIKTILAR", [
        "• Veri temizleme ve anomali giderme süreçleri sonucunda veri bütünlüğü %99.4 seviyesine çıkarılmıştır.",
        "• Geliştirilen Hibrit Stacking Modeli, %89.38 doğruluk ile sektör standartlarının üzerinde bir başarı sergilemiştir.",
        "• Kurulan otomatik pipeline, yeni verilerin sisteme dahil edilmesini ve modelinin güncellenmesini kolaylaştırmaktadır.",
        "• Tüm süreçler, akademik raporlama standartlarına ve profesyonel bankacılık denetim kriterlerine uygun şekilde belgelenmiştir."
    ])

    add_standard_slide("TEŞEKKÜRLER VE SORU-CEVAP", [
        "• Proje sürecindeki sabrınız ve ilginiz için teşekkür ederiz.",
        "• Teknik detaylar, modellerin hiperparametreleri ve veri setine dair tüm forensics analizleri final raporunda mevcuttur.",
        "• Varsa sorularınızı yanıtlamaktan memnuniyet duyarız."
    ])

    pptx_path = os.path.join(base_path, "6_Sunum_Guncel", "Akademik_Sunum_Guncel.pptx")
    prs.save(pptx_path)
    print(f"Sunum başarıyla oluşturuldu: {pptx_path}")

    # PDF DÖNÜŞTÜRME
    try:
        import comtypes.client
        print("> PDF Dönüştürme başlatılıyor...")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1
        pdf_path = pptx_path.replace(".pptx", ".pdf")
        deck = powerpoint.Presentations.Open(pptx_path)
        deck.SaveAs(pdf_path, 32)
        deck.Close()
        powerpoint.Quit()
        print(f"PDF başarıyla oluşturuldu: {pdf_path}")
    except Exception as e:
        print(f"\n[UYARI] PDF dönüşümü başarısız oldu: {e}")

if __name__ == "__main__":
    create_updated_presentation()
