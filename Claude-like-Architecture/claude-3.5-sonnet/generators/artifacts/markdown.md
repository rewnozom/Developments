### **Markdown Artifact Generator (`markdown.py`)**

### **Dataklasser**
1. **`MarkdownGenerationConfig`**
   - Definierar konfigurationsinställningar för Markdown-generering.
   - Viktiga fält:
     - **`style_guide`**: Stilguide som specificerar formateringsregler.
     - **`toc_enabled`**: Om innehållsförteckning (ToC) ska genereras.
     - **`link_validation`**, **`image_validation`**: Om länkar och bilder ska valideras.
     - **`max_length`**: Maximal längd för innehåll.

---

### **Klassen `MarkdownGenerator`**
Den centrala klassen för att generera och hantera Markdown-artfakter.

#### **Huvudfunktioner**

1. **`generate_markdown_artifact(content, identifier, title, metadata)`**
   - Genererar en Markdown-artfakt:
     - Bearbetar innehållet med `_process_content`.
     - Validerar innehållet med `_validate_content`.
     - Skapar en artfakt med metadata som checksumma, storlek och skapelsedatum.

2. **`_initialize_processors()`**
   - Initierar bearbetare och validerare för Markdown:
     - **Bearbetare** (t.ex. `_process_headers`, `_process_links`) för att formatera och standardisera innehåll.
     - **Validerare** (t.ex. `_validate_structure`, `_validate_links`) för att upptäcka fel och varningar.

3. **`_process_content(content)`**
   - Tillämpas bearbetare på innehållet, inklusive:
     - Automatisk generering av ToC.
     - Standardisering av rubriker, länkar, bilder och listor.

4. **`_validate_content(content)`**
   - Validerar Markdown-strukturen, länkar, bilder och formatering.
   - Genererar en `ValidationResult` med:
     - **`errors`**: Fel som kräver åtgärd.
     - **`warnings`**: Rekommendationer för förbättring.

---

#### **Bearbetare (`_process_*` Metoder)**
1. **`_process_headers(content)`**
   - Bearbetar rubriker (ATX och Setext).
   - Standardiserar rubriknivåer och konverterar Setext-rubriker till ATX om så behövs.

2. **`_process_links(content)`**
   - Normaliserar länkar, inklusive:
     - Procentkodning av mellanslag.
     - Hantering av referenslänkar och deras ordning.

3. **`_process_images(content)`**
   - Normaliserar bild-URL:er och säkerställer att alt-text finns.

4. **`_process_lists(content)`**
   - Standardiserar listindentering och hanterar blandade listtyper (ordnade/oordnade).

5. **`_process_code_blocks(content)`**
   - Standardiserar kodblock:
     - Konverterar indenterade block till stängda kodblock (fenced blocks).
     - Hanterar olika typer av kodfästen (` ``` ` eller ` ~~~ `).

6. **`_process_tables(content)`**
   - Justerar tabellformat för att säkerställa konsekvent kolumnbredd.

7. **`_add_table_of_contents(content)`**
   - Skapar en innehållsförteckning baserat på rubriker och infogar den i början av dokumentet.

---

#### **Validerare (`_validate_*` Metoder)**
1. **`_validate_structure(content)`**
   - Kontroll av rubrikhierarki:
     - Dokumentet bör börja med H1.
     - Rubriknivåer bör inte hoppa över (t.ex. från H1 direkt till H3).
   - Identifierar tomma sektioner.

2. **`_validate_links(content)`**
   - Kontrollerar länkar:
     - Identifierar brutna eller odefinierade referenslänkar.
     - Upptäcker olämpliga URL-format (t.ex. mellanslag utan `%20`).

3. **`_validate_images(content)`**
   - Kontrollerar bilder:
     - Kontroll av alt-text.
     - Validerar bildformat (t.ex. `.png`, `.jpg`).

4. **`_validate_formatting(content)`**
   - Kontrollerar Markdown-syntax:
     - Konsekvent användning av betoning (`*` vs `_`).
     - Korrekt listindentering.
     - Stängda kodblock.

---

#### **Ytterligare Funktioner**
1. **`cleanup_markdown(content)`**
   - Städar upp innehåll:
     - Tar bort överflödiga radbrytningar.
     - Normaliserar betoning (`*` eller `_`) och rubriker.

2. **`format_markdown(content)`**
   - Formaterar Markdown enligt stilguiden, inklusive:
     - Konvertering av rubriker mellan ATX och Setext.
     - Normalisering av list- och länkindentering.

3. **`extract_metadata(content)`**
   - Extraherar metadata från Markdown, t.ex.:
     - Titel, taggar, länkar och kodblockspråk.

