### **Sammanfattning av `code.py`**


### **Dataklasser**
1. **`CodeGenerationConfig`**
   - Representerar konfigurationsinställningar för kodgenerering.
   - Nyckelfält:
     - **`language`**: Programmeringsspråk (t.ex. Python, JavaScript).
     - **`include_comments`**, **`include_docstrings`**: Om kommentarer och docstrings ska inkluderas.
     - **`linting_rules`**, **`style_guide`**: Specifika regler för linting och stilkontroll.

2. **`ImportChecker`**
   - Besöker AST-träd och identifierar potentiellt osäkra moduler som `os` eller `subprocess`.

3. **`ComplexityChecker`**
   - Kontrollerar cyklomatisk komplexitet i funktioner och flaggar hög komplexitet (>10).

---

### **Klassen `CodeGenerator`**
Den centrala klassen för att generera, formatera och validera kod.

#### **Huvudfunktioner**

1. **`generate_code_artifact(content, identifier, title, metadata)`**
   - Genererar en kodartefakt:
     - Formaterar koden med `_format_code`.
     - Validerar koden med `_validate_code`.
     - Skapar en artefakt med metadata som språk, storlek och checksumma.

2. **`_format_code(content)`**
   - Väljer formatterare baserat på språket och anropar specifika formateringsmetoder:
     - `_format_python`
     - `_format_javascript`
     - `_format_typescript`

3. **`_validate_code(content)`**
   - Validerar koden med flera steg:
     - Kontroll av syntax (t.ex. via AST för Python).
     - Stilkontroll baserat på språk (via `style_checkers`).
     - Kontroll av maxlängd för innehåll.

4. **`_check_*_style(content)`**
   - Stilkontroll för specifika språk:
     - Python:
       - Kontroll av linjelängd och namnkonventioner.
     - JavaScript och TypeScript:
       - Kontroll av semikolon, operatorers mellanrum och specifika regler (t.ex. "I" för interface).

5. **`_generate_checksum(content)`**
   - Skapar en SHA-256 checksumma för kodens innehåll.

---

#### **Språksspecifika Formatterare och Validatorer**
1. **Formatterare**
   - **`_format_python`**
     - Använder `autopep8` och `black` för att standardisera stil.
   - **`_format_javascript` och `_format_typescript`**
     - Implementerar enkel indenteringsbaserad formatering.

2. **Validatorer**
   - **`_validate_python`**
     - Kontroll av syntax via AST.
     - Identifierar osäkra moduler via `ImportChecker`.
     - Analys av komplexitet via `ComplexityChecker`.

   - **`_validate_javascript` och `_validate_typescript`**
     - Kontrollerar syntax, matchning av parenteser, och farliga mönster som `eval`.

