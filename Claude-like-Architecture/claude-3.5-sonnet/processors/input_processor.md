### Sammanfattning av `processors/input_processor.py`

### **Klasser**
1. **`ProcessedInput`** *(Dataclass)*  
   - Representerar ett bearbetat indataobjekt.  
   - **Attribut:**  
     - `content`: Bearbetat innehåll.  
     - `metadata`: Metadata kopplad till indatat.  
     - `timestamp`: Tidpunkt då bearbetningen utfördes.  
     - `validation_result`: Resultat av valideringen, inklusive eventuella fel.  
   - **Relevans:** Används för att spåra och lagra detaljer om bearbetad indata.  

2. **`InputProcessor`**  
   - Huvudklassen för att validera och bearbeta indata.  
   - **Attribut:**  
     - `processed_inputs`: Lista över tidigare bearbetade indata.  
     - `validation_rules`: Ordbok med valideringsfunktioner för olika typer av indata.  
   - **Relevans:** Kärnmodul för att säkerställa att indata är korrekt och bearbetas enligt specifika regler.  

---

### **Viktiga metoder i `InputProcessor`**
#### **Publika metoder**
1. **`process_input(input_data, input_type=None, metadata=None)`**  
   - Validerar och bearbetar indatat baserat på dess typ.  
   - **Relevans:** Huvudmetod för att bearbeta indata innan den används i systemet.  

2. **`add_validator(input_type, validator)`**  
   - Lägger till en anpassad valideringsfunktion för en specifik datatyp.  
   - **Relevans:** Möjliggör flexibla valideringsregler beroende på behov.  

3. **`get_processed_history()`**  
   - Hämtar historiken över bearbetade indata.  

4. **`clear_history()`**  
   - Rensar historiken för bearbetade indata.  

#### **Privata metoder**
1. **`_initialize_validators()`**  
   - Initierar standardvalideringsregler för text, nummer, JSON och listor.  

2. **`_validate_input(input_data, input_type=None)`**  
   - Utför validering av indatat baserat på dess typ.  

3. **`_process_by_type(input_data, input_type=None)`**  
   - Använder specifika bearbetningsfunktioner beroende på datatyp.  

4. **Valideringsmetoder:**  
   - **`_validate_text(text)`**: Kontrollerar om texten är en icke-tom sträng.  
   - **`_validate_number(number)`**: Kontrollerar om indatat är ett nummer.  
   - **`_validate_json(json_data)`**: Kontrollerar om indatat är giltig JSON.  
   - **`_validate_list(data)`**: Kontrollerar om indatat är en lista.  

5. **Bearbetningsmetoder:**  
   - **`_process_text(text)`**: Trimmar text.  
   - **`_process_number(number)`**: Returnerar siffran som den är.  
   - **`_process_json(json_data)`**: Parsar JSON-strängar till Python-objekt.  
   - **`_process_list(data)`**: Returnerar en kopia av listan.  
