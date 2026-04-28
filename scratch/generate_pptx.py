from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import os
import glob

# Kurumsal Tema
COLOR_BG = RGBColor(10, 25, 47)
COLOR_TITLE = RGBColor(255, 255, 255)
COLOR_ACCENT = RGBColor(212, 175, 55)
COLOR_BODY = RGBColor(200, 210, 230)
COLOR_TECH = RGBColor(100, 200, 255)

def set_slide_bg(slide, image_path=None):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG
    if image_path and os.path.exists(image_path):
        slide.shapes.add_picture(image_path, 0, 0, width=Inches(10), height=Inches(5.625))

def add_header_line(slide):
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.85), Inches(9), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_ACCENT
    line.line.visible = False

def create_title_slide(prs, title, uni, faculty, dept, course, instructor, students):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, "5_Sunum/Gorseller/ultra_cover_bg.png")
    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(5.625))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = COLOR_BG
    overlay.fill.transparency = 0.3
    overlay.line.visible = False

    uni_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    utf = uni_box.text_frame
    p_uni = utf.paragraphs[0]
    p_uni.text = uni.upper()
    p_uni.font.size = Pt(20)
    p_uni.font.bold = True
    p_uni.font.color.rgb = COLOR_TITLE
    p_uni.alignment = PP_ALIGN.CENTER
    
    p_fac = utf.add_paragraph()
    p_fac.text = f"{faculty} | {dept}"
    p_fac.font.size = Pt(14)
    p_fac.font.color.rgb = COLOR_BODY
    p_fac.alignment = PP_ALIGN.CENTER

    t_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.6), Inches(9), Inches(1.2))
    tf = t_box.text_frame
    p = tf.paragraphs[0]
    p.text = title.upper()
    p.font.size = Pt(56)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    p.alignment = PP_ALIGN.CENTER
    
    p_course = tf.add_paragraph()
    p_course.text = f"{course} Projesi Raporu"
    p_course.font.size = Pt(28)
    p_course.font.color.rgb = COLOR_TITLE
    p_course.alignment = PP_ALIGN.CENTER

    inst_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.6), Inches(9), Inches(0.5))
    itf = inst_box.text_frame
    p_inst = itf.paragraphs[0]
    p_inst.text = f"Danışman: {instructor}"
    p_inst.font.size = Pt(18)
    p_inst.font.italic = True
    p_inst.font.color.rgb = COLOR_TECH
    p_inst.alignment = PP_ALIGN.CENTER

    team_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.3), Inches(9), Inches(1.0))
    ttf = team_box.text_frame
    p_team = ttf.paragraphs[0]
    p_team.text = "PROJE EKİBİ"
    p_team.font.size = Pt(13)
    p_team.font.bold = True
    p_team.font.color.rgb = COLOR_ACCENT
    p_team.alignment = PP_ALIGN.CENTER
    
    half = (len(students) + 1) // 2
    p_names1 = ttf.add_paragraph()
    p_names1.text = " • ".join(students[:half])
    p_names1.font.size = Pt(11)
    p_names1.font.color.rgb = COLOR_BODY
    p_names1.alignment = PP_ALIGN.CENTER
    
    p_names2 = ttf.add_paragraph()
    p_names2.text = " • ".join(students[half:])
    p_names2.font.size = Pt(11)
    p_names2.font.color.rgb = COLOR_BODY
    p_names2.alignment = PP_ALIGN.CENTER

def create_dynamic_slide(prs, title, bullets, use_numbers=False, image_path=None, layout_type=3):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    tf_t = title_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = title.upper()
    p_t.font.size = Pt(28)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TITLE
    p_t.alignment = PP_ALIGN.LEFT
    add_header_line(slide)

    if layout_type == 1: # Görsel Solda
        tx_l, tx_t, tx_w, tx_h = Inches(5.5), Inches(1.2), Inches(4), Inches(4.0)
        img_l, img_t, img_w, img_h = Inches(0.5), Inches(1.2), Inches(4.8), Inches(4.0)
    elif layout_type == 0: # Görsel Sağda
        tx_l, tx_t, tx_w, tx_h = Inches(0.5), Inches(1.2), Inches(4), Inches(4.0)
        img_l, img_t, img_w, img_h = Inches(4.8), Inches(1.2), Inches(4.8), Inches(4.0)
    elif layout_type == 4: # Küçük Görsel Ortada
        tx_l, tx_t, tx_w, tx_h = Inches(0.5), Inches(1.2), Inches(9), Inches(1.5)
        img_l, img_t, img_w, img_h = Inches(2.5), Inches(2.8), Inches(5.0), Inches(2.5)
    else: # Geniş Metin
        tx_l, tx_t, tx_w, tx_h = Inches(0.5), Inches(1.2), Inches(9), Inches(4.2)
        img_l, img_t, img_w, img_h = None, None, None, None

    txt_box = slide.shapes.add_textbox(tx_l, tx_t, tx_w, tx_h)
    tf_b = txt_box.text_frame
    tf_b.word_wrap = True
    for i, b in enumerate(bullets, 1):
        p = tf_b.add_paragraph()
        prefix = f"{i}. " if use_numbers else "• "
        p.text = f"{prefix}{b}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_BODY
        p.space_after = Pt(8)

    if image_path and os.path.exists(image_path):
        slide.shapes.add_picture(image_path, img_l, img_t, width=img_w, height=img_h)

def create_transition_slide(prs, main_text):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide)
    
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.3), Inches(10), Inches(1.0))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_ACCENT
    bar.line.visible = False
    
    t_box = slide.shapes.add_textbox(0, Inches(2.3), Inches(10), Inches(1.0))
    tf = t_box.text_frame
    p = tf.paragraphs[0]
    p.text = main_text.upper()
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_BG
    p.alignment = PP_ALIGN.CENTER

# GÖRSEL BULUCU YARDIMCI FONKSİYON
def get_image(pattern):
    files = glob.glob(pattern)
    return files[0] if files else None

# SUNUM AKIŞI
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)

students = ["Oğuz Taşdemir", "Ertuğrul Akkuş", "Yunus Emre Demir", "Rabia Zeynep Sofu", "Nisa Gönültaş", "Ali Baran Akdoğan"]
uni, dept, fac, course, inst = "İstanbul Medeniyet Üniversitesi", "Matematik Bölümü", "Mühendislik Fakültesi", "Makine Öğrenmesi", "Betül Hiçdurmaz"

# --- 1-7. SLAYTLAR (MEVCUT GİRİŞ YAPISI) ---
create_title_slide(prs, "Kredi Notu Sınıflandırma", uni, fac, dept, course, inst, students)

create_dynamic_slide(prs, "ÖNSÖZ VE PROJE AMACI", 
    ["Bankacılık verilerindeki hataları ve eksikleri ayıklayarak anlamlı bir hale getirmeyi hedefledik.", 
     "Müşterilerin 12 aylık harcama ve ödeme alışkanlıklarını inceleyerek kredi risklerini hesaplamaya çalıştık.",
     "Sadece basit formüllerle değil, modern algoritmalar kullanarak çok daha isabetli tahminler yapmayı amaçladık.",
     "Veri setindeki yanlış girilmiş yaş, gelir veya borç gibi bilgileri tek tek elden geçirerek %99 temizlik sağladık.",
     "Bankaların kredi verirken daha güvenli kararlar alabileceği bir sistem kurgulamaya odaklandık.",
     "Tüm bu süreci, her adımı izlenebilir ve mantıklı bir klasör düzeni içerisinde hazırladık."])

create_dynamic_slide(prs, "PROJE DOSYA VE KLASÖR DÜZENİ", 
    ["Klasör 1 (Veri Manipülasyonu): Ham verinin temizlenip analize hazır hale getirildiği ana bölümdür.", 
     "Klasör 2 (Özellik Seçimi): Yüzlerce veri arasından tahminimizi en çok etkileyenleri seçtiğimiz aşamadır.", 
     "Klasör 3 (Sınıflandırma Modelleri): Farklı modelleri eğitip en başarılı olanı bulduğumuz kısımdır.",
     "Düzeni bozmamak için her klasörün içinde kodları, raporları ve görselleri ayrı alt klasörlere ayırdık."])

create_dynamic_slide(prs, "KLASÖR 1: VERİLERİ NASIL TEMİZLEDİK?", 
    ["Metinlerdeki gürültülü karakterleri temizleyip her şeyi Türkçeye çevirdik.",
     "Müşteri numaralarını kontrol ederek kimin hangi ay ne yaptığını takip edilebilir hale getirdik.",
     "Başlangıçtaki Eğitim ve Test setlerini birleştirerek tüm restorasyon işlemlerini tek bir potada yaptık.",
     "Tablodaki boşlukları tespit edip, eksik yerleri mantıklı tahminlerle doldurduk.",
     "Hatalı girilmiş yaş ve kimlik no gibi bilgileri onardık.",
     "Müşterinin değişmemesi gereken statik bilgilerini sabitleyerek veri güvenliğini sağladık.",
     "Aşırı yüksek veya anlamsız görünen rakamları mantıklı sınırlara çektik.",
     "Kendi içinde tutarsız olan kayıtları denetleyerek hataları ayıkladık.",
     "Uç değerleri ortanca değerlerle değiştirerek modelin yanılmasını önledik.",
     "Verimizin ne kadar sağlıklı olduğunu puanlayarak raporladık.",
     "Hangi değişkenlerin birbiriyle ilişkili olduğunu korelasyon analizleriyle gördük.",
     "Verileri bilgisayarın anlayacağı sayısal kodlara dönüştürdük (Label Encoding).",
     "Sayısal veriler için zorunlu tanımlayıcı istatistik tablosunu oluşturduk."], use_numbers=True)

create_dynamic_slide(prs, "KLASÖR 2: EN ÖNEMLİ VERİLERİ NASIL SEÇTİK?", 
    ["Kredi notunu en çok hangi özelliklerin etkilediğini bulmak için korelasyon testleri yaptık.",
     "Karar ağacı algoritmalarıyla en önemli sütunları önem derecesine göre sıraladık.",
     "Karmaşık veri setini PCA yöntemiyle sadeleştirerek en önemli bileşenleri ortaya çıkardık.",
     "Müşteri gruplarının uzaysal olarak nasıl ayrıştığını t-SNE ile görselleştirdik.",
     "RFE yöntemiyle en başarılı özellik kombinasyonlarını ayıkladık.",
     "t-SNE perplexity kıyaslamasıyla en doğru manifold görünümünü yakaladık.",
     "Tahmin gücü düşük olan ve sadece kalabalık yapan verileri sistemden eledik.",
     "Nihai model eğitimi için en güçlü 20 özelliği sabitleyerek köprü kurduk."], use_numbers=True)

create_dynamic_slide(prs, "KLASÖR 3: MODEL EĞİTİMİ VE BAŞARI ÖLÇÜMÜ", 
    ["1. Veri Hazırlama ve Standartlaştırma",
     "2. Karar Ağacı (Decision Tree) Modelleme",
     "3. Rastgele Orman (Random Forest) Modelleme",
     "4. Mega Benchmark (20 Algoritma Yarışı)",
     "5. Hibrit Sistem ve Temel Oylama Analizi",
     "6. Şampiyon Modelin Final Eğitimi",
     "7. Blind Test (Kör Tahminleme) Süreci",
     "8. Overfit ve Veri Sızıntısı (Leakage) Kontrolü",
     "9. Optuna ile Bayesian Ağırlık Optimizasyonu",
     "10. Gelişmiş İstifleme (Stacking) Mimarisi",
     "11. Kernel-tabanlı SVM Model Entegrasyonu",
     "12. SMOTE Dengeleme ve ROC/PR Analizleri",
     "13. Zorunlu F1 Sonuç Kıyaslama Tablosu",
     "14. Hiperparametre Optimizasyon Raporu"], use_numbers=False)

create_dynamic_slide(prs, "VERİ SETİ HAKKINDA GENEL BİLGİLER", 
    ["Kaggle platformundaki 'Credit Score Classification' adlı açık kaynaktan yararlandık.", 
     "Başlangıçta biri sadece eğitim, diğeri sadece test için ayrılmış iki ayrı dosyamız vardı.",
     "Temizlik aşamasında bu iki dosyayı birleştirip, modelleme aşamasında tekrar amaca göre ayırdık.",
     "Toplamda 100.000'den fazla finansal kayıt üzerinde çalışma şansımız oldu.",
     "Veriler 12 aylık bir süreci kapsıyor, bu da tam bir yıllık finansal döngüyü görmemizi sağlıyor.",
     "Gerçek dünya verisi olduğu için çok fazla gürültü vardı, tüm adımları buna göre kurguladık."])


# --- KLASÖR 1: DETAY SLAYTLARI ---
create_transition_slide(prs, "Veri Manipülasyonu")

create_dynamic_slide(prs, "ADIM 1: FORMAT VE ÇEVİRİ İŞLEMLERİ", 
    ["Ham verideki anlamsız karakterleri ($, _, !! vb.) temizleyerek veriyi okunabilir hale getirdik.",
     "Tüm sütun isimlerini ve içerikleri Türkçe terminolojiye çevirerek yerelleştirdik.",
     "Sayısal olması gereken ama metin olarak girilmiş alanları düzelterek matematiksel işlemlere uygun hale getirdik."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/1_Format_ve_Ceviri/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 2: MÜŞTERİ BÜTÜNLÜK KONTROLÜ", 
    ["Müşteri ID'lerini kontrol ederek, her müşterinin 12 aylık verisinin tam olup olmadığını denetledik.",
     "Kayıp ayları olan veya mükerrer girilen kayıtları tespit ederek veri setinden ayıkladık.",
     "Bu aşamada kullanılan Venn Diyagramları ile veri setindeki kesişim ve ayrışma noktalarını görselleştirdik."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/2_Musteri_ID_Kontrolu/*venn*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 3: VERİ KONSOLİDASYONU", 
    ["Eğitim ve Test setlerini, her ikisinin de aynı temizlik işlemlerinden geçmesi için tek bir çatı altında birleştirdik.",
     "Müşterilerin verilerini kronolojik sıraya dizerek 12 aylık bir zaman serisi bütünü oluşturduk.",
     "Daha sonraki modelleme aşaması için bu iki setin sınırlarını hafızada tutarak güvenli bir birleştirme sağladık."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/3_Veri_Birlestirme/1_aylik_dagilim.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 4: DOLULUK ANALİZİ", 
    ["Birleştirdiğimiz veri setinin hangi sütunlarında eksik bilgiler olduğunu Lollipop haritalama yöntemiyle görselleştirdik.",
     "Eksikliklerin rastgele mi yoksa belirli bir kalıba göre mi oluştuğunu analiz ettik.",
     "Bu haritayı, bir sonraki adımda hangi doldurma yöntemini seçeceğimize karar vermek için bir rehber olarak kullandık."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/4_Doluluk_Analizi/*lollipop*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 5: KRİTİK SÜTUN ONARIMI", 
    ["İsim, SSN, Meslek ve Yaş gibi bir müşteri için asla değişmemesi gereken bilgileri hedef aldık.",
     "Kişinin dolu olduğu aydaki doğru bilgisini bularak, boş veya hatalı girildiği aylara o bilgiyi kopyaladık.",
     "Mantıksız yaş girişlerini (Örn: 200 yaşında görünen müşteriler) tespit edip düzeltilebilir olanları gerçek yaşlarına çektik."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/5_Kritik_Sutun_Temizligi/*dashboard*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 6: VERİ TUTARLILIK DENETİMİ", 
    ["Onardığımız bilgilerin aydan aya gerçekten sabit kalıp kalmadığını kontrol ettik.",
     "Statik olması gereken (doğum tarihi, kimlik no) bilgilerin 12 ay boyunca tutarlı olduğunu doğruladık.",
     "Bu denetimle birlikte müşteri profilindeki temel çelişkileri tamamen ortadan kaldırmış olduk."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/6_Veri_Tutarlilik_Denetimi/*bar*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 7: FİNANSAL SÜTUN TEMİZLİĞİ", 
    ["Aylık maaş veya borç gibi alanlara yanlışlıkla girilmiş, milyonlarca dolar gibi anlamsız sayıları tespit ettik.",
     "Bu aşırı uç noktaları (outliers) sistemden tamamen silmek yerine, 'Winsorization' dediğimiz bir yöntemle makul sınırlara çektik.",
     "Böylece hem veri kaybetmedik hem de uç değerlerin makine öğrenmesi modelimizin kafasını karıştırmasına engel olduk."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/7_Finansal_Sutun_Temizligi/*global_finansal_denge*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 8: MANTIKSAL DENETİM", 
    ["Sayıları düzeltsek de kendi içinde mantıklı olup olmadıklarını çapraz sorgularla test ettik.",
     "Örneğin; aylık harcaması, aylık gelirinden çok daha fazla olan kayıtları inceledik.",
     "Faiz oranları, kredi kartı sayıları ve vadesi geçmiş borçları birbiriyle kıyaslayarak tutarsızlıkları eledik."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/8_Finansal_Tutarlilik_Denetimi/*dashboard*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 9: ANOMALİ RESTORASYONU", 
    ["Kalan eksik bilgileri ve küçük hataları düzeltmek için müşterinin genel durumuna baktık.",
     "Eksik olan finansal bilgileri, ortalama (mean) yerine ortanca (median) değerlerle doldurduk ki uç rakamlardan etkilenmeyelim.",
     "Bu restorasyon sayesinde veri setimizdeki doluluk oranını %100'e yakın bir seviyeye taşıdık."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/9_Anomali_Duzeltme/*dashboard*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 10: VERİ KALİTE ANALİZİ", 
    ["Tüm temizlik işlemleri bittikten sonra, verilerimizin ne kadar temiz ve tutarlı olduğunu bir sağlık puanıyla ölçtük.",
     "Bu puanlama sistemi sayesinde, restorasyon öncesi ve sonrası kalite artışını objektif bir şekilde kanıtladık."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/10_Veri_Kalite_Analizi/*heatmap*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 11: KORELASYON ANALİZİ", 
    ["Kredi notu ile diğer tüm değişkenlerin arasındaki ilişkileri büyük bir ısı haritasıyla inceledik.",
     "Hangi özelliklerin birbiriyle çok benzeştiğini görerek, birbirini tekrar eden verileri fark ettik.",
     "Bu analiz, bir sonraki klasörde yapacağımız 'Özellik Seçimi' (Feature Selection) için zemin hazırladı."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/11_Final_Istatistik_ve_Korelasyon/*heatmap*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 12: LABEL ENCODING (SAYISALLAŞTIRMA)", 
    ["Makine öğrenmesi modelleri, 'Mühendis' veya 'Doktor' gibi metinleri anlayamadığı için bu alanları kodlamamız gerekiyordu.",
     "Tüm metinsel verileri (Meslek, Kredi Tipi vb.) bilgisayarın anlayabileceği sayısal değerlere (0, 1, 2...) dönüştürdük.",
     "Böylece veri setini tamamen sayısal bir matris haline getirerek 'Veri Manipülasyonu' aşamasını tamamladık."],
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/12_Kategorik_Kodlama/*panel*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 13: TANIMLAYICI İSTATİSTİKLER TABLOSU", 
    ["Veri setindeki tüm sayısal değişkenlerin merkezi eğilim (ortalama, medyan) ve yayılım (std, min, max) ölçümleri yapıldı.",
     "Bu istatistikler, verideki finansal dengeleri ve temizlik sonrası oluşan tutarlı yapıyı matematiksel olarak belgeler.",
     "Gözlemlenen değerler, makine öğrenmesi modelinin öğrenme sürecindeki sınırlarını (range) belirlemektedir."], 
    image_path=get_image("1_Veri_Manipülasyonu/Gorseller/11_Final_Istatistik_ve_Korelasyon/5_ortalama_degerler_bar.png"), layout_type=1)


# --- KLASÖR 2: DETAY SLAYTLARI ---
create_transition_slide(prs, "Özellik Seçimi (Feature Selection)")

create_dynamic_slide(prs, "ADIM 1: FİLTRELEME YÖNTEMİ (FILTER METHOD)", 
    ["Kredi notunu belirlemede en etkili olan özellikleri bulmak için istatistiksel filtreleme uyguladık.",
     "Pearson korelasyonu ile hedef değişkenimizle doğrudan ilişkisi olan ve olmayan sütunları ayıkladık.",
     "Böylece modelimizin kafasını karıştırabilecek gereksiz detayları başlangıçta temizlemiş olduk."],
    image_path=get_image("2_Feature_Selection/Gorseller/1_Filter_Method/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 2: RANDOM FOREST İLE ÖNEM SIRALAMASI", 
    ["Karar ağacı tabanlı bir algoritma kurarak, modelin tahminde bulunurken hangi verilere daha çok güvendiğini ölçtük.",
     "Gini önemi (importance) skorlarına göre, örneğin 'Gecikmiş Borç' sütununun ne kadar kritik olduğunu grafiğe döktük.",
     "Tahmin gücü zayıf olan özellikleri tespit ederek modelin daha hızlı ve hatasız çalışmasını sağladık."],
    image_path=get_image("2_Feature_Selection/Gorseller/2_Embedded_Method/*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 3: PCA (TEMEL BİLEŞENLER) ANALİZİ", 
    ["Elimizdeki çok sayıdaki sütunu daha az sayıda ana başlık (bileşen) altında toplamaya çalıştık.",
     "PCA yöntemiyle, verinin taşıdığı anlamı (varyansı) kaybetmeden boyut küçültmesi yaptık.",
     "Bu sayede hem modelin eğitim hızını artırdık hem de aşırı öğrenmenin (overfitting) önüne geçtik."],
    image_path=get_image("2_Feature_Selection/Gorseller/3_PCA_Analizi/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 4: T-SNE İLE UZAYSAL GÖRSELLEŞTİRME", 
    ["İyi, Orta ve Kötü kredi notuna sahip müşterilerin birbirlerinden ne kadar ayrıştığını görmek istedik.",
     "Çok boyutlu verilerimizi t-SNE algoritması yardımıyla iki veya üç boyutlu uzaya taşıdık.",
     "Görselleştirmede kümelerin net bir şekilde birbirinden koptuğunu görerek veri temizliğimizin başarısını kanıtladık."],
    image_path=get_image("2_Feature_Selection/Gorseller/4_Manifold_Visualization/*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 5: RFE (WRAPPER METHOD) İLE ÖZELLİK ELEME", 
    ["Recursive Feature Elimination (RFE) yöntemiyle, en zayıf özellikleri tek tek eleyerek optimal kümeyi bulduk.",
     "Random Forest algoritmasını bir eğitici olarak kullanarak, özelliklerin birbirleriyle olan etkileşimlerini hesaba kattık.",
     "Bu yöntemle, modelin tahmin başarısını düşürmeden veri boyutunu 15 ana özelliğe kadar sadeleştirdik."],
    image_path=get_image("2_Feature_Selection/Gorseller/5_Wrapper_Method/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 6: İLERİ SEVİYE MANIFOLD (t-SNE KIYASI)", 
    ["t-SNE algoritmasının hassasiyet (Perplexity) parametresini {15, 30, 50} değerleri için test ettik.",
     "Farklı yoğunluklardaki veri kümelerinin uzaysal ayrışmasını gözlemleyerek en dengeli görünümü yakaladık.",
     "Bu analiz, modelin sınıfları neden ve nasıl ayırabildiğine dair görsel bir kanıt sundu."],
    image_path=get_image("2_Feature_Selection/Gorseller/6_Advanced_Manifold/1_tSNE_Perplexity_Comparison.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 7: İLERİ SEVİYE FORENSİCS", 
    ["Seçtiğimiz özelliklerin gerçekten doğru olup olmadığını kontrol etmek için Permutation testi uyguladık.",
     "Verilerin sırasını rastgele karıştırarak model performansındaki düşüşü gözlemledik ve asıl önem sırasını netleştirdik.",
     "Bu işlemle birlikte modellemeye girecek en güçlü özellik listesini tamamen dondurmuş olduk."],
    image_path=get_image("2_Feature_Selection/Gorseller/7_Advanced_Forensics/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 8: NİHAİ ÖZELLİK SEÇİMİ (KÖPRÜ)", 
    ["Tüm filtreleme ve RFE süreçleri sonucunda model başarısını en çok etkileyen 20 özellik kesinleştirilmiştir.",
     "Bu özellik seti, modelin hem daha hızlı çalışmasını hem de gereksiz gürültüden arınmasını sağlar.",
     "Seçilen özellik listesi, bir sonraki 'Modelleme' aşaması için ana girdi (joblib) olarak kaydedilmiştir."],
    image_path=get_image("2_Feature_Selection/Gorseller/8_Final_Secim/Figure_10_Final_Features.png"), layout_type=0)


# --- KLASÖR 3: DETAY SLAYTLARI ---
create_transition_slide(prs, "Sınıflandırma Modelleri")

create_dynamic_slide(prs, "ADIM 1: VERİ HAZIRLIĞI VE ÖLÇEKLENDİRME", 
    ["Başlangıçta birleştirdiğimiz veriyi tekrar 'Eğitim' ve 'Test' setleri olarak ayırdık.",
     "Tüm sayısal verileri (Maaş, Yaş, Borç vb.) aynı matematiksel ölçeğe getirmek için Standardization uyguladık.",
     "Böylece hiçbir değişkenin model üzerinde haksız bir ağırlığa sahip olmamasını güvence altına aldık."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/1_Veri_Hazirlik/*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 2 VE 3: TEMEL AĞAÇ MODELLERİ", 
    ["Tahmin sistemimizin temelini oluşturmak için Decision Tree (Karar Ağacı) algoritmalarını kurduk.",
     "Ardından birden fazla karar ağacının oylamasıyla çalışan Random Forest (Rastgele Orman) modelini eğittik.",
     "Modellerin ilk sonuçlarını alarak veri setimizin tahmin edilebilirliğini (Predictability) kanıtladık."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/3_Random_Forest/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 4: MEGA BENCHMARK (20 MODEL YARIŞI)", 
    ["Hangi algoritmanın verimize en uygun olduğunu bulmak için tam 20 farklı makine öğrenmesi modelini aynı anda eğittik.",
     "XGBoost, CatBoost, LightGBM gibi en güçlü algoritmaları doğruluk (Accuracy) ve F1 skorlarına göre sıraladık.",
     "Tüm bu modellerin performanslarını yan yana koyarak şeffaf bir 'Liderlik Tablosu' oluşturduk."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/4_Mega_Benchmark/Figure_11_Accuracy_Leaderboard.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 5: HİBRİT OPTİMİZASYON", 
    ["Tek bir modele güvenmek yerine, yarışta en iyi performansı gösteren modelleri birleştirmeye karar verdik.",
     "Stacking (İstifleme) veya Voting (Oylama) yöntemleriyle, modellerin ortak karar aldığı hibrit bir yapı kurduk.",
     "Bu sayede tek bir modelin yapabileceği olası hataları, diğer modellerin gücüyle kapattık."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/5_Hibrit_ve_Optimizasyon/*.png"), layout_type=1)

create_dynamic_slide(prs, "ADIM 6: FİNAL MODELİNİN EĞİTİMİ", 
    ["Kurduğumuz bu hibrit modeli, eğitim setimizin tamamıyla son bir kez eğittik.",
     "Modelin parametrelerini, geçmiş 12 aylık verilere bakarak en optimum kararları alacak şekilde kalibre ettik.",
     "Bu aşamada model, kredi riskini sınıflandırmak için kendi içinde karmaşık bir matematiksel ağ inşa etti."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/6_Final_Model_Egitimi/*Feature_Importance*.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 7: KÖR TEST (BLIND PREDICTION)", 
    ["Modelin eğitimi bittikten sonra, performansını daha önce hiç görmediği 'Test Seti' üzerinde denedik.",
     "Modelden, cevaplarını bilmediğimiz binlerce müşteri profili için kredi notu (İyi, Orta, Kötü) tahmini yapmasını istedik.",
     "Bu tahminleri gerçek sonuçlarla karşılaştırarak modelin sahada ne kadar güvenilir olduğunu kanıtladık."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/7_Final_Tahminleme/*.png"), layout_type=1)

# GÜNCELLENEN ADIM 8: OVERFIT VE LEAKAGE KONTROLÜ
create_dynamic_slide(prs, "ADIM 8: OVERFIT VE SIZINTI (LEAKAGE) KONTROLÜ", 
    ["Projemizin akademik ve teknik doğruluğunu ispatlamak için son bir test geliştirdik.",
     "Eğitim Doğruluğu ile Test Doğruluğu arasındaki farkı ölçerek modelin veriyi ezberlemediğini (No Overfit) kanıtladık.",
     "Hedef değişkenimiz ile diğer sütunlar arasındaki korelasyonu inceleyerek haksız bilgi geçişi olmadığını (No Leakage) onayladık.",
     "Modelimiz; %82 gibi oldukça yüksek ve istikrarlı bir Test başarı oranına imza attı."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/8_Overfit_Kontrolu/1_Train_vs_Test_Performance.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 8: VERİ SIZINTISI (DATA LEAKAGE) RAPORU", 
    ["Hata yapmamak adına, hiçbir sütunun kredi skorunu önceden %100 bilmediğinden (Sızıntı) emin olduk.",
     "Gerçekleştirdiğimiz Sızıntı Teşhis Raporuna (Leakage Diagnostic) göre tüm verilerimiz GÜVENLİ statüsünde tescillendi.",
     "Bu durum, veri temizliği (Klasör 1) adımlarımızın ne kadar kusursuz çalıştığının teknik bir ispatıdır."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/8_Overfit_Kontrolu/2_Leakage_Diagnostic_Dashboard.png"), layout_type=4)

# ADIM 9: OPTUNA OPTİMİZASYONU
create_dynamic_slide(prs, "ADIM 9: HİBRİT MODEL OPTİMİZASYONU (OPTUNA)", 
    ["Binlerce farklı model kombinasyonu ve ağırlık seçeneği Optuna algoritması ile otomatik olarak test edildi.",
     "Sadece basit oylama değil, modellerin birbiri üzerindeki baskınlık oranları matematiksel olarak optimize edildi.",
     "En yüksek doğruluk potansiyeline sahip hibrit konfigürasyonlar (XGB, RF, ET) bu aşamada belirlendi.",
     "Arama uzayı genişletilerek verinin tavan puanı olan %83 bandı zorlanmaya başlandı."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/9_Optuna_Optimizasyon/Figure_9_1_Optimization_Top_10.png"), layout_type=1)

# ADIM 10: ADVANCED STACKING
create_dynamic_slide(prs, "ADIM 10: ADVANCED STACKING (İSTİFLEME) MİMARİSİ", 
    ["%83 barajını kalıcı olarak aşmak için hiyerarşik (Level 0 ve Level 1) bir ensemble mimarisi geliştirildi.",
     "Baz modellerin (RF, ET, XGB) tahminleri, son kararı veren bir 'Hakem Model' (Logistic Regression) tarafından birleştirildi.",
     "Bu yöntemle zayıf modellerin güçlüleri aşağı çekmesi engellenerek %83.67 gibi rekor bir başarıya ulaşıldı.",
     "Modelin hangi durumda hangi alt modele güvenmesi gerektiğini öğrendiği 'Meta-Öğrenme' süreci başarıyla tamamlandı."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/10_Stacking_Model/Figure_10_1_Confusion_Matrix.png"), layout_type=0)

# ADIM 11: SVM KERNEL MODEL
create_dynamic_slide(prs, "ADIM 11: KERNEL-BASED MODEL (SVM)", 
    ["Rubrikte istenen 'Çekirdek Tabanlı' model grubunu temsil etmek üzere SVM (RBF Kernel) algoritması uygulandı.",
     "Doğrusal olmayan veri sınırlarını (non-linear boundaries) yakalamak için yüksek boyutlu uzayda sınıflandırma yapıldı.",
     "Karmaşıklık matrisi ile SVM'in 'Standart' ve 'Kötü' kredi sınıflarını ayırmadaki başarısı test edildi."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/11_SVM_Model/1_SVM_Confusion_Matrix.png"), layout_type=1)

# ADIM 12: SMOTE VE ROC/PR EĞRİLERİ
create_dynamic_slide(prs, "ADIM 12: SMOTE İLE SINIF DENGELENMESİ", 
    ["Veri setindeki sınıf dengesizliğini (imbalance) gidermek için SMOTE algoritmasıyla sentetik veri üretildi.",
     "Daha az temsil edilen 'Kötü' kredi grubu verileri artırılarak modelin bu sınıfı tanıması kolaylaştırıldı.",
     "Sonuçlar; modelin azınlık sınıflarda daha yüksek bir duyarlılık (Recall) yakaladığını göstermektedir."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/12_Imbalance_Metrics/1_Multiclass_ROC_Curves.png"), layout_type=0)

create_dynamic_slide(prs, "ADIM 12: ZORUNLU DEĞERLENDİRME EĞRİLERİ", 
    ["Modelin tüm sınıflardaki performansını AUC (Area Under Curve) metrikleriyle tescil etmek için ROC eğrileri çizildi.",
     "Hassasiyet ve duyarlılık dengesini gösteren Precision-Recall eğrileri ile modelin kararlılığı kanıtlandı.",
     "Tüm kredi sınıfları için AUC değerleri %0.80 bandının üzerinde kalarak yüksek güvenilirlik sağladı."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/12_Imbalance_Metrics/2_Precision_Recall_Curves.png"), layout_type=1)

# ADIM 13: ZORUNLU KIYASLAMA TABLOSU
create_dynamic_slide(prs, "ADIM 13: ZORUNLU SONUÇ KIYASLAMA TABLOSU", 
    ["Ödev talimatlarında istenen; Ham Veri, Filter, Wrapper ve PCA senaryoları tek bir tabloda kıyaslandı.",
     "Özellik seçimi (RFE) sonrası ulaşılan F1 skorunun ham veriye göre daha verimli bir yapı sunduğu kanıtlandı.",
     "Tablodaki her satır, veri temsilinin (feature representation) model başarısına etkisini bilimsel olarak özetlemektedir."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/13_Comparison_Table/1_Comparison_Table_Visual.png"), layout_type=0)

# ADIM 14: OPTİMİZASYON RAPORU
create_dynamic_slide(prs, "ADIM 14: HİPERPARAMETRE OPTİMİZASYON RAPORU", 
    ["Grid Search ve Bayesian Optimization (Optuna) süreçlerinde test edilen tüm parametre aralıkları raporlandı.",
     "En iyi performansı veren n_estimators, max_depth ve learning_rate gibi parametreler tablolaştırıldı.",
     "Bu rapor, modelimizin en yüksek verimlilikte çalışması için yapılan tüm kalibrasyonları şeffaf bir şekilde sunar."], 
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/14_Optimization_Report/1_Best_Parameters_Table.png"), layout_type=4)

# FİNAL SLAYTI:
create_dynamic_slide(prs, "PROJE SONUCU: GENEL BAŞARI ÖZETİ", 
    ["Başlangıçtaki karmaşık ve gürültülü bankacılık verileri %99 oranında temizlenip onarıldı.",
     "Geliştirdiğimiz Gelişmiş İstifleme Modeli (Adım 10), %83.67 gibi rekor bir Test başarısı sergiledi.",
     "Ezberleme (Overfit) ve Veri Sızıntısı (Leakage) testlerinden başarıyla geçildi.",
     "Bu sistem sayesinde, manuel kredi skorlama süreçleri tamamen otomatize edilmiş ve insan hatası riski en aza indirilmiştir.",
     "Sonuç olarak, projemiz finansal karar destek mekanizmalarına entegre edilebilecek sağlam, şeffaf ve güvenilir bir yapıya kavuşmuştur."],
    image_path=get_image("3_Siniflandirma_Modelleri/Gorseller/10_Stacking_Model/Figure_10_4_Distribution_Comparison.png"), layout_type=0)

prs.save("5_Sunum/Sunum_Final.pptx")
print("Overfit ve Leakage kontrol slaytları eklendi.")
