### Sammanfattning av `processors/content_processor.py`


### **Klasser**
1. **`ProcessedContent`** *(Dataclass)*  
   - Representerar bearbetat innehåll.  
   - **Attribut:**  
     - `original`: Ursprungligt innehåll.  
     - `processed`: Bearbetat innehåll.  
     - `metadata`: Metadata för bearbetningen.  
     - `timestamp`: Tidpunkt då bearbetningen utfördes.  
     - `processing_time`: Tidsåtgång för bearbetningen (i sekunder).  
   - **Relevans:** Spårar och lagrar information om bearbetat innehåll.  

2. **`ContentProcessor`**  
   - Huvudklassen för innehållsbearbetning och hantering av processorer.  
   - **Attribut:**  
     - `processors`: Ordbok med bearbetningsfunktioner för olika typer av innehåll.  
     - `processed_content`: Lista över tidigare bearbetat innehåll.  
   - **Relevans:** Kärnmodul för att bearbeta innehåll enligt specifika regler och typer.  

---

### **Viktiga metoder i `ContentProcessor`**
#### **Publika metoder**
1. **`process_content(content, content_type, options=None)`**  
   - Bearbetar innehåll med en specificerad processor.  
   - **Relevans:** Huvudmetod för att bearbeta innehåll i systemet.  

2. **`add_processor(content_type, processor)`**  
   - Lägger till en anpassad processor för en specifik innehållstyp.  

3. **`remove_processor(content_type)`**  
   - Tar bort en processor för en specifik innehållstyp.  

4. **`get_processed_history()`**  
   - Hämtar historiken över tidigare bearbetat innehåll.  

5. **`clear_history()`**  
   - Rensar historiken över bearbetat innehåll.  

#### **Privata metoder**
1. **`_initialize_processors()`**  
   - Initierar standardprocessorer för text, kod, markdown och JSON.  

2. **Bearbetningsmetoder:**  
   - **`_process_text(content, options)`**: Bearbetar text (t.ex. trimning, case-transformation).  
   - **`_process_code(content, options)`**: Bearbetar kod (t.ex. ta bort kommentarer, formatering).  
   - **`_process_markdown(content, options)`**: Normaliserar markdown-innehåll (t.ex. rubriker, listor).  
   - **`_process_json(content, options)`**: Bearbetar JSON-innehåll (t.ex. formatering, parsning).  
