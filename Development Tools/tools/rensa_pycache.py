import os
import shutil
import platform

def detect_device():
    # Kolla om det är en telefon eller dator baserat på path
    phone_path = "/storage/emulated/0"
    computer_path = "A:\\0rginize\\0dev"
    
    # Kontrollera vilken path som existerar
    if os.path.exists(phone_path):
        return "phone", phone_path
    elif os.path.exists(computer_path):
        return "computer", computer_path
    else:
        raise Exception("Kunde inte identifiera enhet - varken telefon eller dator path hittades")

def clean_pycache(start_path):
    """
    Rekursivt hitta och ta bort alla __pycache__ mappar från start_path
    """
    pycache_dirs = []
    total_size = 0
    
    # Gå igenom alla mappar rekursivt
    for root, dirs, files in os.walk(start_path):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            size = get_dir_size(pycache_path)
            total_size += size
            pycache_dirs.append((pycache_path, size))
    
    # Ta bort alla hittade __pycache__ mappar
    for pycache_path, size in pycache_dirs:
        try:
            shutil.rmtree(pycache_path)
            print(f"Raderat: {pycache_path} ({format_size(size)})")
        except Exception as e:
            print(f"Kunde inte radera {pycache_path}: {str(e)}")
    
    return len(pycache_dirs), total_size

def get_dir_size(path):
    """Beräkna total storlek för en mapp"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def format_size(size):
    """Formatera bytes till läsbar storlek"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"

def main():
    try:
        # Identifiera enhet och få rätt path
        device_type, base_path = detect_device()
        print(f"Kör på {device_type} med path: {base_path}")
        
        # Rensa __pycache__ mappar
        print("\nLetar efter __pycache__ mappar...")
        num_deleted, total_size = clean_pycache(base_path)
        
        # Visa sammanfattning
        print(f"\nRensning klar!")
        print(f"Antal raderade __pycache__ mappar: {num_deleted}")
        print(f"Total frigjord storlek: {format_size(total_size)}")
        
    except Exception as e:
        print(f"Ett fel uppstod: {str(e)}")

if __name__ == "__main__":
    main()