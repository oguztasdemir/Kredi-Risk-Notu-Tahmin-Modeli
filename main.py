import subprocess
import os
import time

def run_step(step_number, script_path):
    print(f"\n{'='*50}")
    print(f"ADIM {step_number} BAŞLATILIYOR: {os.path.basename(script_path)}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        # Scripti çalıştır
        result = subprocess.run(["python", script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        
        end_time = time.time()
        print(f"Adım {step_number} başarıyla tamamlandı. Süre: {end_time - start_time:.2f} saniye.")
        
    except subprocess.CalledProcessError as e:
        print(f"HATA: Adım {step_number} çalıştırılırken bir sorun oluştu!")
        print(e.stderr)
        return False
    return True

def main():
    try:
        from kullanici import klasor as base_path
    except ImportError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    scripts_dir = os.path.join(base_path, "1_Veri_Manipülasyonu", "Python_Kodlari")
    
    # Çalıştırılacak scriptlerin listesi
    steps = [
        os.path.join(scripts_dir, "1_veri_temizleme_ve_cevirme.py"),
        os.path.join(scripts_dir, "2_id_kontrolu.py"),
        os.path.join(scripts_dir, "3_veri_birlestirme.py"),
        os.path.join(scripts_dir, "4_doluluk_analizi.py"),
        os.path.join(scripts_dir, "5_kritik_sutun_temizligi.py"),
        os.path.join(scripts_dir, "6_veri_tutarlilik_denetimi.py"),
        os.path.join(scripts_dir, "7_finansal_sutun_temizligi.py"),
        os.path.join(scripts_dir, "8_finansal_tutarlilik_denetimi.py")
    ]
    
    # İnteraktif Kontrol: Eğer çıktılar varsa kullanıcıya sor
    check_file = os.path.join(base_path, "1_Veri_Manipülasyonu", "Ciktilar", "3_Veri_Birlestirme", "birlesik_veri_türkçe.xlsx")
    if os.path.exists(check_file):
        print("\n" + "="*50)
        print("BİLGİ: Proje daha önce çalıştırılmış ve birleşik veriler mevcut.")
        print("1 - Tüm adımları baştan sona yeniden çalıştır (Full Reset)")
        print("2 - Sadece analizleri ve raporları tazele (Quick Audit)")
        print("="*50)
        secim = input("Seçiminizi yapın (1/2): ")
        if secim == "2":
            print("\n>>> Hızlı mod seçildi. Sadece raporlama ve temizlik adımları (4, 5, 6, 7) çalıştırılacak...")
            os.environ['QUICK_MODE'] = '1'
            steps = [s for s in steps if any(x in s for x in ["4_", "5_", "6_", "7_"])]
        else:
            os.environ['QUICK_MODE'] = '0'
    
    total_start = time.time()
    
    print("KREDİ HESAPLAMA VERİ HAZIRLIK OTOMASYONU BAŞLATILDI")
    
    for i, script in enumerate(steps, 1):
        if not run_step(i, script):
            print("\nOtomasyon bir hata nedeniyle durduruldu.")
            break
    else:
        total_end = time.time()
        print(f"\n{'#'*50}")
        print(f"TÜM ADIMLAR BAŞARIYLA TAMAMLANDI!")
        print(f"Toplam İşlem Süresi: {total_end - total_start:.2f} saniye.")
        print(f"{'#'*50}")

if __name__ == "__main__":
    main()
