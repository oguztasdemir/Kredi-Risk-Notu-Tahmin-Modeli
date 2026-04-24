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
        os.path.join(scripts_dir, "3_veri_birlestirme.py")
    ]
    
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
