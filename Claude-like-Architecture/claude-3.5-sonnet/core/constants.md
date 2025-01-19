### **Sammanfattning av `core/constants.py`**


#### **Systemkonstanter**
1. **Allmänna konstanter:**
   - **`VERSION`**: Version för systemet. *(t.ex. "1.0.0")*
   - **`DEFAULT_ENCODING`**: Standardkodning. *(t.ex. UTF-8)*
   - **`TEMP_DIR`, `CACHE_DIR`**: Fördefinierade sökvägar för tillfälliga och cachedata.

2. **Token-relaterade konstanter:**
   - **`MAX_TOKENS`**: Maximalt antal tokens som stöds i en operation.  
   - **`TOKEN_PADDING`**, **`RESPONSE_BUFFER`**: Reserverade tokens för säkerhetsmarginal.

3. **Tidsinställningar:**
   - **`DEFAULT_TIMEOUT`**: Standardtimeout för operationer. *(t.ex. 30 sekunder)*  
   - **`MAX_RETRY_DELAY`**, **`RETRY_BACKOFF_FACTOR`**: För retry-hantering.

4. **Minnesrelaterade gränser:**
   - **`MAX_MEMORY_MB`**: Max tillgängligt minne i MB. *(t.ex. 1024 MB)*  
   - **`CLEANUP_THRESHOLD`**, **`GC_INTERVAL`**: För hantering av minnesrensning.

---

#### **Enum-typer**
1. **`Environment`** *(Systemmiljöer)*:  
   - Möjliga värden: `DEVELOPMENT`, `TESTING`, `STAGING`, `PRODUCTION`.

2. **`LogLevel`** *(Loggnivåer)*:  
   - Möjliga värden: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

3. **`SystemStatus`** *(Systemtillstånd)*:  
   - Möjliga värden: `INITIALIZING`, `READY`, `PROCESSING`, `ERROR`, `SHUTDOWN`.

4. **`ContentType`** *(Innehållstyper)*:  
   - Möjliga värden: `TEXT`, `CODE`, `MARKDOWN`, `HTML`, `SVG`, `MERMAID`.

5. **`SecurityLevel`** *(Säkerhetsnivåer)*:  
   - Möjliga värden: `LOW`, `MEDIUM`, `HIGH`, `STRICT`.

---

#### **API-konstanter**
- **`API_VERSION`**: Version för API:t. *(t.ex. "v1")*
- **`API_BASE_URL`**: Grundadress för API. *(t.ex. "https://api.anthropic.com")*
- **`DEFAULT_HEADERS`**: Standardhuvuden för API-anrop.

---

#### **Fel- och framgångsmeddelanden**
1. **`ERROR_MESSAGES`:**  
   Standardiserade felmeddelanden för vanliga feltyper:
   - **`validation`**, **`not_found`**, **`permission`**, **`rate_limit`**, **`timeout`**, m.m.

2. **`SUCCESS_MESSAGES`:**  
   Standardiserade framgångsmeddelanden för skapande, uppdatering och borttagning av resurser.

3. **`RESPONSE_TEMPLATES`:**  
   Mallar för API-respons. T.ex.:
   ```json
   {
       "status": "error",
       "message": "{message}",
       "code": "{code}",
       "details": "{details}"
   }
   ```

---

#### **Regex-mönster**
1. **`PATTERNS`:**
   Fördefinierade regex för validering av:
   - E-postadresser. *(t.ex. `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)*
   - URL:er. *(t.ex. `https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+`)*
   - Versioner. *(t.ex. `^\d+\.\d+\.\d+$`)*
   - UUID:er. *(t.ex. `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`)*

---

#### **Standardkonfiguration**
1. **System:**  
   - Lägen: `debug_mode`, `environment`.  
   - Retry-logik: `max_retries`, `timeout`.

2. **Säkerhet:**  
   - Säkerhetsfilter: `enable_safety_filters`, `content_filtering`.  
   - Gränser: `max_tokens`, `rate_limit`.

3. **Resurser:**  
   - Filstorlek: `max_file_size`.  
   - Tillåtna filtyper: `allowed_extensions`.  
   - Automatrensning: `auto_cleanup`.

4. **Loggning:**  
   - Nivå: `level`. *(t.ex. `INFO`)*
   - Format: `'%(asctime)s - %(name)s - %(levelname)s - %(message)s'`.
