### **Sammanfattning av `content.py`**

#### **1. Dataklasser**
- **`SafetyCheck`**  
  Representerar resultatet av en säkerhetskontroll:
  - **`name`**: Namnet på kontrollen.
  - **`passed`**: Om kontrollen godkänts.
  - **`issues`**: Lista över identifierade problem.
  - **`level`**: Säkerhetsnivån för kontrollen (t.ex. LOW, MEDIUM).
  - **`timestamp`**: Tidpunkten för kontrollen.
  - **`metadata`**: Ytterligare information om kontrollen.

- **`SafetyReport`**  
  En rapport över samtliga säkerhetskontroller:
  - **`checks`**: Lista över genomförda säkerhetskontroller.
  - **`passed`**: Om alla kontroller klarades.
  - **`issues`**: Samlade problem som identifierades.
  - **`timestamp`**: Tidpunkten för rapporten.

---

#### **2. Klassen `ContentSafety`**
Hanterar säkerhetskontroller och filtrering av innehåll.

##### **Konstruktor**
- **`__init__(default_level=SafetyLevel.MEDIUM)`**  
  Ställer in standard säkerhetsnivå och initierar säkerhetskontroller.

---

#### **Funktionalitet**

1. **Säkerhetskontroller**
   - **`check_safety(content, content_id, content_type, safety_level)`**  
     Utför säkerhetskontroller på innehållet. Genererar en **`SafetyReport`** som innehåller resultaten från kontrollerna.

2. **Initiering av kontroller**
   - **`_initialize_checks()`**  
     Skapar en lista av fördefinierade säkerhetskontroller:
     - **`content_filter`**: Filtrerar otillåtet innehåll.
     - **`code_safety`**: Kontroll av potentiellt farlig kod.
     - **`link_safety`**: Validerar länkar.
     - **`xss_protection`**: Upptäcker XSS-mönster.
     - **`input_validation`**: Validerar text- och kodinmatning.

3. **Detaljerade kontroller**
   - **`_check_content_filter(content, content_type, safety_level)`**  
     Söker efter otillåtet innehåll baserat på säkerhetsnivå.
   - **`_check_code_safety(content, content_type, safety_level)`**  
     Upptäcker farliga kodmönster, t.ex. `eval()` eller `subprocess`.
   - **`_check_link_safety(content, content_type, safety_level)`**  
     Validerar länkar och markerar potentiellt osäkra URL:er.
   - **`_check_xss_protection(content, content_type, safety_level)`**  
     Söker efter XSS-mönster som `<script>` eller `javascript:`.
   - **`_check_input_validation(content, content_type, safety_level)`**  
     Kontrollerar om inmatningen uppfyller valideringskrav.

4. **Stödmetoder**
   - **`_get_prohibited_patterns(safety_level)`**  
     Returnerar förbjudna mönster baserat på säkerhetsnivå.
   - **`_get_dangerous_code_patterns(safety_level)`**  
     Returnerar farliga kodmönster baserat på säkerhetsnivå.
   - **`_get_xss_patterns(safety_level)`**  
     Returnerar mönster som kan användas för XSS-attacker.
   - **`_is_safe_link(link, safety_level)`**  
     Validerar om en länk är säker baserat på säkerhetsnivå.

5. **Anpassning av kontroller**
   - **`add_safety_check(name, check_function)`**  
     Lägger till en anpassad säkerhetskontroll.
   - **`remove_safety_check(name)`**  
     Tar bort en befintlig säkerhetskontroll.

6. **Loggning och historik**
   - **`get_safety_history(content_id)`**  
     Hämtar historiken över säkerhetsrapporter för ett visst innehåll.
   - **`clear_history(content_id=None)`**  
     Rensar säkerhetsloggar, antingen globalt eller för ett specifikt innehåll.
