import os
import subprocess
import sys
import time

# Ana dizin
try:
    from kullanici import klasor as base_path
except ImportError:
    base_path = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path):
    """Scripti çalıştırır. Model sorma ekranında otomatik '2' (Mevcutu Kullan) seçer."""
    if not os.path.exists(script_path):
        return False
    print(f"\n>>> İŞLENİYOR: {os.path.basename(script_path)}")
    try:
        # '2' girişi göndererek mevcut modelleri kullanmasını sağlıyoruz (Hızlı güncelleme için)
        result = subprocess.run([sys.executable, script_path], input="2\n", capture_output=False, text=True)
        return result.returncode == 0
    except:
        return False

def show_sub_menu(title, scripts):
    while True:
        print(f"\n" + "="*50)
        print(f"ALT MENÜ: {title}")
        print("="*50)
        print("A - Tüm Adımları Sırayla Çalıştır")
        for i, script in enumerate(scripts, 1):
            print(f"{i} - {os.path.basename(script)}")
        print("\n0 - GERİ DÖN | Q - ÇIKIŞ")
        
        choice = input("\nSeçiminiz: ").strip().upper()
        if choice == '0': return
        if choice == 'Q': sys.exit()
        if choice == 'A':
            for s in scripts:
                if not run_script(s): break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(scripts): run_script(scripts[idx])
            except: print("Geçersiz seçim!")

def get_sorted_scripts(path):
    """Dosyaları başındaki sayılara göre doğal sırada (1, 2... 10) sıralar."""
    if not os.path.exists(path): return []
    def extract_number(filename):
        parts = filename.split('_')
        return int(parts[0]) if parts[0].isdigit() else 999
    
    files = [f for f in os.listdir(path) if f.endswith(".py")]
    files.sort(key=extract_number)
    return [os.path.join(path, f) for f in files]

def main():
    p1 = os.path.join(base_path, "1_Veri_Manipülasyonu", "Python_Kodlari")
    p2 = os.path.join(base_path, "2_Feature_Selection", "Python_Kodlari")
    p3 = os.path.join(base_path, "3_Siniflandirma_Modelleri", "Python_Kodlari")

    phase1 = get_sorted_scripts(p1)
    phase2 = get_sorted_scripts(p2)
    phase3 = get_sorted_scripts(p3)

    while True:
        print("\n" + "#"*70)
        print("   KREDİ NOTU SINIFLANDIRMA SİSTEMİ - MASTER KONTROL PANELİ (v100)")
        print("#"*70)
        print("1 - [FAZ 1] Veri Manipülasyonu ve Restorasyon")
        print("2 - [FAZ 2] Özellik Mühendisliği ve VIP Seçimi")
        print("3 - [FAZ 3] Sınıflandırma, AI ve 50k Tahmin")
        print("-" * 35)
        print("F - [FULL PIPELINE] Tüm Projeyi Baştan Sona Çalıştır ve Güncelle")
        print("Q - SİSTEMDEN ÇIK")
        
        choice = input("\nSeçiminiz: ").strip().upper()
        if choice == '1': show_sub_menu("Veri Restorasyonu", phase1)
        elif choice == '2': show_sub_menu("Özellik Seçimi", phase2)
        elif choice == '3': show_sub_menu("AI ve Tahminleme", phase3)
        elif choice == 'F':
            for scripts in [phase1, phase2, phase3]:
                for s in scripts:
                    if not run_script(s): break
        elif choice == 'Q': break

if __name__ == "__main__":
    main()
