### Sammanfattning av `processors/format_processor.py`

### **Klasser**
1. **`FormattedContent`** *(Dataclass)*  
   - Representerar formaterat innehåll.  
   - **Attribut:**  
     - `content`: Det formaterade innehållet.  
     - `format_type`: Typ av formatering som tillämpats.  
     - `metadata`: Metadata relaterad till formateringen.  
     - `timestamp`: Tidpunkt då formateringen utfördes.  
   - **Relevans:** Spårar och lagrar detaljer om formaterat innehåll.  

2. **`FormatProcessor`**  
   - Huvudklassen för innehållsformatering. Hanterar olika formattyper och tillåter anpassade formatterare.  
   - **Attribut:**  
     - `formatters`: Ordbok med formateringsfunktioner för olika typer av innehåll.  
     - `formatted_content`: Lista över tidigare formaterat innehåll.  
   - **Relevans:** Central modul för att standardisera och anpassa innehållsformatering.  

---

### **Viktiga metoder i `FormatProcessor`**
#### **Publika metoder**
1. **`format_content(content, format_type, options=None)`**  
   - Formaterar innehåll med en specificerad formatterare.  
   - **Relevans:** Huvudmetod för att formatera innehåll i systemet.  

2. **`add_formatter(format_type, formatter)`**  
   - Lägger till en anpassad formatterare för en specifik typ av innehåll.  

3. **`remove_formatter(format_type)`**  
   - Tar bort en formatterare för en specifik innehållstyp.  

4. **`get_formatting_history()`**  
   - Hämtar historiken över tidigare formaterat innehåll.  

5. **`clear_history()`**  
   - Rensar historiken över formaterat innehåll.  

#### **Privata metoder**
1. **`_initialize_formatters()`**  
   - Initierar standardformatterare för text, kod, markdown och HTML.  

2. **Formateringsmetoder:**  
   - **`_format_text(content, options)`**: Formaterar text (t.ex. radbrytning, centrering).  
   - **`_format_code(content, options)`**: Formaterar kod med valfria språkspecifika markeringar.  
   - **`_format_markdown(content, options)`**: Formaterar markdown (t.ex. TOC, numrerade rubriker).  
   - **`_format_html(content, options)`**: Formaterar HTML (t.ex. escaping, inbäddning i taggar).  

3. **Hjälpmetoder:**  
   - **`_wrap_text(text, width)`**: Radbryter text till specificerad bredd.  
   - **`_center_text(text)`**: Centrera text.  
   - **`_add_table_of_contents(content)`**: Lägger till en innehållsförteckning för markdown.  
   - **`_number_headers(content)`**: Lägger till nummerering för markdown-rubriker.  
