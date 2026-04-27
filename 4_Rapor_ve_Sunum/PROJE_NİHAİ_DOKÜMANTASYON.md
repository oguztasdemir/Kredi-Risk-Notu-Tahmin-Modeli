# KREDİ NOTU SINIFLANDIRMA VE TAHMİNLEME PROJESİ: MİKRO-TEKNİK DOKÜMANTASYON

Bu doküman, projenin ham veri aşamasından nihai tahmine kadar geçen tüm teknik süreçlerin (26 Adım) detaylı dökümüdür.

---

## 📂 FAZ 1: VERİ MANİPÜLASYONU VE ADLİ RESTORASYON (14 ADIM)
Bu fazda amaç; %35 eksiklik oranına sahip "kirli" veriyi, AI modelleri için kusursuz bir "altın standart" veriye dönüştürmektir.

1.  **1_veri_temizleme_ve_cevirme.py:** Veri setindeki UTF-8/ASCII uyumsuzluklarını giderir, Türkçe karakter bozukluklarını onarır ve sütun tiplerini (float/int) standardize eder.
2.  **2_id_kontrolu.py:** Müşteri ID'lerindeki mükerrer kayıtları ve bozuk ID dizilerini tespit eder. Veri bütünlüğünün temelini atar.
3.  **3_veri_birlestirme.py:** Farklı kaynaklardan gelen finansal tabloları "Müşteri ID" anahtarı üzerinden tek bir master veri setinde birleştirir.
4.  **4_karakter_temizleme.py:** Metin tabanlı sütunlardaki (Meslek, Şehir vb.) gereksiz boşlukları, özel sembolleri ve sayısal gürültüleri temizler.
5.  **5_kritik_sutun_temizligi.py:** Hedef değişkeni (Kredi Skoru) doğrudan etkileyen kritik sütunlardaki "Unknown" veya "Belirtilmemiş" etiketlerini ayıklar.
6.  **6_akilli_veri_doldurma.py (Kritik):** Eksik verileri sadece ortalama ile değil, Müşteri ID bazlı geçmiş trendlere göre akıllıca doldurur.
7.  **7_aykiri_deger_kontrolu.py:** Z-Score ve IQR yöntemlerini kullanarak finansal uç değerleri (Outliers) tespit eder.
8.  **8_finansal_tutarlilik_denetimi.py:** "Gelir < Gider" veya "Borç > Varlık" gibi mantıksal finansal tutarsızlıkları denetler.
9.  **9_anomali_duzeltme.py:** İmkansız değerleri (Negatif yaş, 200+ yaş, negatif borç) mantıksal eşiklerle onarır.
10. **10_derin_temizlik_belirtilmemis.py:** Kategorik sütunlardaki anlamsız "Diğer" veya "Belirsiz" kayıtlarını en yakın komşu mantığıyla restore eder.
11. **11_final_kiyaslama_ve_denetim.py:** Temizlik öncesi ve sonrası verinin istatistiksel dağılımını kıyaslayarak restorasyonun başarısını kanıtlar.
12. **12_musteri_tutarlilik_raporu.py:** Her müşteri için bir "Veri Sağlık Skoru" üretir.
13. **13_mantiksal_hata_tespiti.py:** Sektörel kurallar çerçevesinde (Bankacılık regülasyonları vb.) verideki son mantık hatalarını süzer.
14. **14_gercek_hata_onarimi.py:** Manuel müdahale gerektiren son kritik hataları adli (forensic) yöntemlerle finalize eder.

---

## 📂 FAZ 2: ÖZELLİK MÜHENDİSLİĞİ VE STRATEJİK SEÇİM (5 ADIM)
Bu fazda amaç; 50+ değişken arasından model başarısına en çok katkı sağlayan "VIP" özellikleri izole etmektir.

15. **1_filter_method_korelasyon.py:** Değişkenler arası çoklu doğrusallığı (Multicollinearity) ölçer ve birbiriyle %95+ korelasyonlu gereksiz sütunları eler.
16. **2_embedded_method_onem.py:** Random Forest algoritması üzerinden her özelliğin hedef değişken üzerindeki "bilgi kazancı" (Information Gain) puanını hesaplar.
17. **3_pca_analizi.py:** Temel Bileşen Analizi ile verinin boyutunu indirger ve varyans açıklama oranlarını (Scree Plot) raporlar.
18. **4_manifold_learning_tsne.py:** Yüksek boyutlu veriyi 2 boyuta indirgeyerek kredi skor gruplarının (0-1-2) veride ne kadar ayrışabildiğini görselleştirir.
19. **5_final_ozet_karsilastirma.py (Köprü):** Tüm analizlerden süzülen "En İyi 20" özelliği belirler ve bunu Phase 3'e "Selected_Features.joblib" olarak teslim eder.

---

## 📂 FAZ 3: SINIFLANDIRMA VE HİBRİT AI MODELLEME (7 ADIM)
Bu fazda amaç; en yüksek doğruluğa sahip, kararlı ve ölçeklenebilir bir tahmin motoru kurmaktır.

20. **1_veri_hazirlik_ve_bolme.py:** Phase 2'den gelen VIP listesini kullanarak veriyi süzer ve %80 Eğitim - %20 Doğrulama olarak böler.
21. **2_karar_agaci_modeli.py:** Temel (baseline) başarı oranını belirlemek için Karar Ağacı modelini eğitir.
22. **3_random_forest_modeli.py:** Tekil modeller arasında en güçlü aday olan Random Forest'ı optimize eder.
23. **4_mega_benchmark_20_model.py:** 20 farklı algoritmayı **StandardScaler (Scaling)** sarmalıyla en adil şartlarda yarıştırır ve 10 akademik grafik üretir.
24. **5_hibrit_ve_optimizasyon.py:** En başarılı 11 model arasından 11C3 (165 kombinasyon) hibrit yapı kurar ve ağırlık optimizasyonu yapar.
25. **6_final_model_egitimi.py:** Şampiyon Hibrit yapıyı (ET + RF + XGB) tüm veriyle eğitir ve final performans tablolarını (Precision/Recall) Türkçe üretir.
26. **7_final_tahminleme.py:** Etiketsiz 50.000 kişilik liste üzerinde nihai tahminleri gerçekleştirir ve "50k_Final_Tahmin_Listesi.xlsx"i oluşturur.

---

## 📂 FAZ 4: NİHAİ RAPORLAMA VE SUNUM
- **PROJE_NİHAİ_DOKÜMANTASYON.md:** Tüm bu teknik sürecin akademik özeti ve kullanıcı rehberi.

---
**Sonuç:** Bu 26 adımlık hat, ham verideki hataları %99 oranında temizlemiş ve model başarısını baseline (%60) seviyesinden **%82.56** seviyesine taşımıştır.
