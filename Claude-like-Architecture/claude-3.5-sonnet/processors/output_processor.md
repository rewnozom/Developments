### Sammanfattning av `processors/output_processor.py`

### **Klasser**
1. **`ProcessedOutput`** *(Dataclass)*  
   - Representerar bearbetad utdata.  
   - **Attribut:**  
     - `content`: Bearbetad utdata.  
     - `format_type`: Formattyp för utdatat (t.ex. `text`, `json`).  
     - `metadata`: Metadata kopplad till bearbetningen.  
     - `timestamp`: Tidpunkt då bearbetningen utfördes.  
     - `validation`: Resultat av valideringen (inkl. felmeddelanden).  
   - **Relevans:** Dokumenterar och spårar detaljer om bearbetad utdata.  

2. **`OutputProcessor`**  
   - Huvudklassen för bearbetning och validering av utdata.  
   - **Attribut:**  
     - `processors`: Ordbok med bearbetningsfunktioner för olika formattyper.  
     - `validators`: Ordbok med valideringsfunktioner för olika formattyper.  
     - `processed_outputs`: Lista över tidigare bearbetade utdatan.  
   - **Relevans:** Central modul för att hantera korrekt formatering och validering av utdata.  

---

### **Viktiga metoder i `OutputProcessor`**
#### **Publika metoder**
1. **`process_output(content, output_type, metadata=None)`**  
   - Bearbetar och validerar utdata baserat på angivet format.  
   - **Relevans:** Huvudmetod för att hantera och validera utdata.  

2. **`add_processor(output_type, processor, validator=None)`**  
   - Lägger till en anpassad processor och validerare för en specifik formattyp.  

3. **`remove_processor(output_type)`**  
   - Tar bort en processor och validerare för en specifik formattyp.  

4. **`get_processing_history()`**  
   - Hämtar historiken över tidigare bearbetade utdatan.  

5. **`clear_history()`**  
   - Rensar historiken över bearbetade utdatan.  

#### **Privata metoder**
1. **`_initialize_processors()`**  
   - Initierar standardprocessorer för text, JSON, HTML och XML.  

2. **`_initialize_validators()`**  
   - Initierar standardvaliderare för text, JSON, HTML och XML.  

3. **Bearbetningsmetoder:**  
   - **`_process_text_output(content)`**: Bearbetar text (t.ex. trimning).  
   - **`_process_json_output(content)`**: Kontrollerar och formaterar JSON.  
   - **`_process_html_output(content)`**: Escapar HTML.  
   - **`_process_xml_output(content)`**: Kontrollerar och validerar XML.  

4. **Valideringsmetoder:**  
   - **`_validate_text_output(content)`**: Validerar textutdata.  
   - **`_validate_json_output(content)`**: Validerar JSON-utdata.  
   - **`_validate_html_output(content)`**: Validerar HTML-utdata.  
   - **`_validate_xml_output(content)`**: Validerar XML-utdata.  
