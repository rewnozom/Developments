### **Sammanfattning av `boundary.py`**

#### **1. Dataklasser**
- **`Boundary`**  
  Representerar ett systemgränssnitt:
  - **`type`**: Typ av gränssnitt (t.ex. CONTENT, INTERACTION).
  - **`name`**: Gränssnittets namn.
  - **`constraints`**: Regler eller begränsningar för gränssnittet.
  - **`enabled`**: Anger om gränssnittet är aktivt.
  - **`metadata`**: Ytterligare information om gränssnittet.

- **`BoundaryViolation`**  
  Representerar en överträdelse av ett gränssnitt:
  - **`boundary`**: Det gränssnitt som överträtts.
  - **`violation_type`**: Typ av överträdelse.
  - **`details`**: Information om överträdelsen.
  - **`timestamp`**: Tidpunkten för överträdelsen.
  - **`metadata`**: Ytterligare information om överträdelsen.

---

#### **2. Klassen `BoundaryController`**
Hanterar systemgränssnitt och deras efterlevnad.

##### **Funktionalitet**
1. **Hantera och kontrollera gränssnitt**
   - **`enforce_boundary`**  
     Kontrollera om ett gränssnitt överträds baserat på en given kontext och dess regler.
   - **`_check_boundary`**  
     Kontrollera ett gränssnitt baserat på dess typ:
     - **CONTENT**: Begränsningar som maxlängd eller tillåten typ.
     - **INTERACTION**: Begränsningar som antal förfrågningar eller sessionstid.
     - **RESOURCE**: Begränsningar som minnes- eller CPU-användning.
     - **CAPABILITY**: Begränsningar för fil- eller nätverksåtkomst.
     - **CUSTOM**: Användardefinierade kontroller via specialskriven kod.

2. **Gränssnittshantering**
   - **`add_boundary`**: Lägger till ett nytt gränssnitt.
   - **`remove_boundary`**: Tar bort ett befintligt gränssnitt.
   - **`update_boundary`**: Uppdaterar begränsningar för ett gränssnitt.
   - **`enable_boundary`**/**`disable_boundary`**: Aktiverar eller inaktiverar ett gränssnitt.

3. **Undantagshantering**
   - **`add_exemption`**/**`remove_exemption`**: Lägger till eller tar bort undantag för specifika kontexter.

4. **Loggning och historik**
   - **`_record_violation`**: Loggar överträdelser av gränssnitt.
   - **`get_violations`**: Hämtar historik för överträdelser.
   - **`clear_violations`**: Rensar historik för överträdelser.
