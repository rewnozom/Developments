### Sammanfattning av `core/exceptions.py`


### **Klasser**
1. **`SystemError`** *(Bas-klass)*  
   - Grunden för alla systemrelaterade undantag.  
   - **Relevans**: Alla undantagsklasser i modulen ärver från denna.  

#### Specifika undantagsklasser:
2. **`SystemInitializationError`**  
   - Indikerar fel vid systeminitiering.  
   - **Relevans**: Används av initieringslogik (`BaseSystem.initialize`).  

3. **`SystemOperationError`**  
   - Indikerar fel vid systemoperationer.  
   - **Relevans**: Används för att hantera fel vid systemoperationer.  

4. **`ConfigurationError`**  
   - Indikerar fel i systemkonfigurationen.  
   - **Attribut:**  
     - `config_key` *(str)*: Specifik konfigurationsnyckel relaterad till felet.  
   - **Relevans**: Används vid validering av konfigurationsdata.  

5. **`ValidationError`**  
   - Indikerar valideringsfel.  
   - **Attribut:**  
     - `validation_errors` *(list)*: Lista över specifika valideringsfel.  
   - **Relevans**: Används för att säkerställa giltiga operationer och data.  

6. **`ResourceError`**  
   - Indikerar resursrelaterade fel (t.ex. minne, disk, nätverk).  
   - **Attribut:**  
     - `resource_id` *(str)*: Identifierar den felaktiga resursen.  
   - **Relevans**: Viktig för resurshantering.  

7. **`OperationError`**  
   - Indikerar fel i en operation.  
   - **Attribut:**  
     - `operation_id` *(str)*: Identifierar operationen.  
     - `details` *(dict)*: Ytterligare detaljer om felet.  
   - **Relevans**: Används i operationshantering.  

8. **`TokenError`**  
   - Indikerar fel relaterade till tokenhantering.  
   - **Attribut:**  
     - `current_tokens` *(int)*: Nuvarande antal använda tokens.  
     - `max_tokens` *(int)*: Maximalt antal tillåtna tokens.  
   - **Relevans**: Används för att övervaka och hantera resursgränser.  

9. **`ContentError`**  
   - Indikerar fel relaterade till innehåll (t.ex. ogiltig data).  
   - **Attribut:**  
     - `content_type` *(str)*: Typ av innehåll som orsakade felet.  
   - **Relevans**: Relevant för säkerhets- och datavalidering.  

10. **`MemoryError`**  
    - Indikerar minnesrelaterade fel.  
    - **Attribut:**  
      - `current_usage` *(int)*: Nuvarande minnesanvändning.  
      - `limit` *(int)*: Tillåten minnesgräns.  

11. **`TimeoutError`**  
    - Indikerar att en operation har tidsöverskridit.  
    - **Attribut:**  
      - `timeout` *(int)*: Specificerad timeout (i sekunder).  
      - `operation_type` *(str)*: Typ av operation som misslyckades.  

12. **`RateLimitError`**  
    - Indikerar att en gräns för operationer har överskridits.  
    - **Attribut:**  
      - `limit` *(int)*: Maximal tillåten användning.  
      - `reset_time` *(int)*: Tidpunkt för återställning av begränsning.  

13. **`AuthenticationError`**  
    - Indikerar autentiseringsfel.  
    - **Attribut:**  
      - `auth_type` *(str)*: Typ av autentisering som misslyckades.  

14. **`AuthorizationError`**  
    - Indikerar att en åtgärd saknar tillräckliga rättigheter.  
    - **Attribut:**  
      - `required_permissions` *(list)*: Lista över nödvändiga rättigheter.  

15. **`BoundaryError`**  
    - Indikerar att en gräns i systemet har överskridits.  
    - **Attribut:**  
      - `boundary_type` *(str)*: Typ av gräns.  

16. **`StateError`**  
    - Indikerar fel relaterade till systemets aktuella tillstånd.  
    - **Attribut:**  
      - `current_state` *(str)*: Det aktuella tillståndet.  

---

### **Dekoratorer**
1. **`handle_system_errors`**  
   - Fångar systemrelaterade och generiska undantag, loggar dem och konverterar dem till `SystemError`.  

2. **`validate_operation`**  
   - Utför validering av funktionens argument. Höjer `ValidationError` vid ogiltiga argument.  

3. **`with_retry(max_retries=3, delay=1.0)`**  
   - Försöker köra funktionen upp till `max_retries` gånger med en fördröjning mellan försök.  

4. **`validate_args(*args, **kwargs)`**  
   - Placeholder för argumentvalidering. Returnerar `True` om valideringen är lyckad.  

---

### **Interaktion med andra moduler**
- **`BaseSystem`** från `core/base.py`: Fångar och hanterar fel med dessa undantagsklasser.  
- **`SystemConfig`** från `core/config.py`: Kan ge upphov till `ConfigurationError`.  
