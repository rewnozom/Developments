import os
import shutil

def organize_files():
    # Definiera bas-sökvägar
    source_dir = "./Pages/desktop"
    layout_dir = os.path.join(source_dir, "Layout")
    
    # Säkerställ att Layout-mappen existerar
    if not os.path.exists(layout_dir):
        os.makedirs(layout_dir)
    
    # Lista alla Python-filer i källmappen
    files = [f for f in os.listdir(source_dir) if f.endswith('.py')]
    
    for file in files:
        # Skapa mappnamn från filnamnet (ta bort .py)
        folder_name = os.path.splitext(file)[0]
        
        # Skapa full sökväg för den nya mappen
        new_folder_path = os.path.join(layout_dir, folder_name)
        
        # Skapa mappen om den inte existerar
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        
        # Källfilens sökväg
        source_file = os.path.join(source_dir, file)
        
        # Målfilens sökväg (renamed to Page.py)
        dest_file = os.path.join(new_folder_path, "Page.py")
        
        # Flytta och byt namn på filen
        try:
            shutil.move(source_file, dest_file)
            print(f"Flyttade {file} -> {folder_name}/Page.py")
        except Exception as e:
            print(f"Fel vid flyttning av {file}: {str(e)}")

if __name__ == "__main__":
    # Bekräfta med användaren
    print("Detta script kommer att:")
    print("1. Skapa mappar under ./Pages/desktop/Layout/")
    print("2. Flytta varje .py-fil till sin egen mapp")
    print("3. Döpa om varje fil till Page.py")
    
    confirm = input("Vill du fortsätta? (ja/nej): ")
    
    if confirm.lower() == 'ja':
        organize_files()
        print("\nOrganisering slutförd!")
    else:
        print("Avbryter...")
