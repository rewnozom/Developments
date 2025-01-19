### **Sammanfattning av `core/config.py`**


### **Nyckelfunktioner**

---

#### **Datamodellen: `SystemConfig`**
1. **Hanterar systeminställningar:**
   - **Systemnamn:** `system_name`  
   - **Version:** `version`  
   - **Miljö:** `environment` *(t.ex. utveckling, produktion)*  
   - **Debug-läge:** `debug_mode` *(True/False)*

2. **Prestandainställningar:**
   - **`max_tokens`:** Max antal tokens för bearbetning *(standard: 100000)*  
   - **`response_timeout`:** Timeout för responsoperationer *(t.ex. 30 sekunder)*  
   - **`max_concurrent_operations`:** Max antal samtidiga operationer *(t.ex. 10)*  
   - **`memory_limit`:** Minnesgräns *(1GB som standard)*

3. **Säkerhetsinställningar:**
   - Säkerhetsfilter och innehållsbegränsningar:  
     **`enable_safety_filters`**, **`content_filtering`** *(standard: True)*  
   - **Max omförsök:** `max_retries` *(t.ex. 3)*

4. **Resurshantering:**
   - **Resurssökväg:** `resource_path` *(standard: `resources/`)*  
   - **Cache:** Aktiverat via `cache_enabled` och storlek definierad av `cache_size` *(t.ex. 1000)*

5. **Loggning och övervakning:**
   - **Loggnivå:** `log_level` *(t.ex. `INFO`)*  
   - **Loggfil:** `log_file` *(t.ex. `logs/claude.log`)*  
   - **Metrics:** Möjlighet att aktivera övervakning via `enable_metrics`.

---

#### **Metoder**

1. **Ladda konfiguration från fil: `from_file(config_path)`**
   - Stöder JSON- och YAML-format.  
   - Konverterar sökvägar för `resource_path` och `log_file` till `Path`.

2. **Spara konfiguration till fil: `save(config_path)`**
   - Sparar inställningar till en specifik fil i JSON eller YAML.  
   - Skapar nödvändiga kataloger om de inte existerar.

3. **Validera konfiguration: `validate()`**
   - Utför flera säkerhetskontroller, inklusive:  
     - `max_tokens` och `response_timeout` måste vara positiva heltal.  
     - `log_level` måste vara en giltig loggnivå.  
     - Validerar att kataloger för `resource_path` och `log_file` existerar.

4. **Konvertering till och från ordbok:**
   - **`to_dict()`**: Exporterar alla attribut till en ordbok.  
   - **`update(updates)`**: Tillåter dynamiska uppdateringar av attribut.

5. **Återställning av standardinställningar: `reset_defaults()`**
   - Nollställer alla inställningar till deras standardvärden.
