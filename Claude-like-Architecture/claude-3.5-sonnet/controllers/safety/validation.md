### **Sammanfattning av `validation.py`**

#### **1. Dataklasser**
- **`ValidationRule`**  
  Representerar en valideringsregel:
  - **`name`**: Regelns namn.
  - **`type`**: Typ av validering (t.ex. INPUT, OUTPUT, SYSTEM, CUSTOM).
  - **`validator`**: Funktion för att utföra validering.
  - **`enabled`**: Om regeln är aktiverad.
  - **`metadata`**: Ytterligare information om regeln.

- **`ValidationResult`**  
  Representerar resultatet av en validering:
  - **`rule_name`**: Namnet på regeln som applicerades.
  - **`passed`**: Om valideringen godkändes.
  - **`issues`**: Lista över identifierade problem.
  - **`timestamp`**: Tidpunkten för valideringen.
  - **`metadata`**: Ytterligare data om resultatet.

---

#### **2. Klassen `SafetyValidator`**
Hanterar säkerhetsvalidering och loggning.

##### **Konstruktor**
- **`__init__()`**  
  Initialiserar valideringsregler och historik.

---

#### **Funktionalitet**

1. **Validering av innehåll**
   - **`validate_safety(content, content_id, validation_type, rules)`**  
     Utför säkerhetsvalidering baserat på specificerade regler och typ. Returnerar en lista över **`ValidationResult`**.

2. **Initiering av standardregler**
   - **`_initialize_validators()`**  
     Skapar standardvalideringsregler:
     - **Input-regler**:
       - `input_sanitization`: Kontrollerar för farliga mönster i inmatning.
       - `input_size`: Kontrollerar storleken på inmatning.
     - **Output-regler**:
       - `output_safety`: Söker efter känslig information i utdata.
       - `output_formatting`: Kontrollerar korrekt format för utdata.
     - **System-regler**:
       - `system_state`: Kontrollerar CPU, minne och diskutnyttjande.
       - `resource_usage`: Kontrollerar resursanvändning av innehåll.

3. **Specifika valideringar**
   - **`_validate_input_sanitization(content)`**  
     Söker efter farliga mönster som `<script>` och `javascript:`.
   - **`_validate_input_size(content)`**  
     Kontroll av innehållets storlek mot maxgränser (t.ex. 1 MB för text).
   - **`_validate_output_safety(content)`**  
     Identifierar känslig information som e-post, kreditkort eller personnummer.
   - **`_validate_output_formatting(content)`**  
     Söker efter otillåtna tecken (t.ex. nullbytes eller icke-utskrivbara tecken).
   - **`_validate_system_state(content)`**  
     Kontrollerar systemets CPU-, minnes- och diskutnyttjande.
   - **`_validate_resource_usage(content)`**  
     Analyserar innehållets resurskrav (t.ex. minne).

4. **Hantera regler**
   - **`add_validation_rule(name, rule_type, validator, metadata)`**  
     Lägger till en anpassad valideringsregel.
   - **`remove_validation_rule(name)`**  
     Tar bort en befintlig regel.
   - **`enable_validation_rule(name)`** och **`disable_validation_rule(name)`**  
     Aktiverar eller inaktiverar en regel.
   - **`get_enabled_rules(validation_type)`**  
     Hämtar alla aktiverade regler för en viss typ.

5. **Loggning och historik**
   - **`get_validation_history(content_id)`**  
     Hämtar valideringshistorik för ett specifikt innehåll.
   - **`clear_history(content_id=None)`**  
     Rensar historik, antingen globalt eller för en specifik innehållsidentifierare.

6. **Hjälpmetoder**
   - **`_get_applicable_rules(validation_type, rule_names)`**  
     Filtrerar regler som är relevanta baserat på typ och namn.
   - **`get_rule_metadata(name)`** och **`update_rule_metadata(name, metadata)`**  
     Hanterar metadata för specifika regler.
