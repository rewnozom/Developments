### **Sammanfattning av `metrics.py`**

#### **1. Dataklasser**
- **`MetricType` (Enum)**  
  Definierar typer av kvalitetsmått:
  - **ACCURACY**, **COMPLETENESS**, **CONSISTENCY**, **RELEVANCE**, **CLARITY**, **CUSTOM**.

- **`Metric`**  
  Representerar ett enskilt kvalitetsmått:
  - **`type`**: Typ av mått (`MetricType`).
  - **`value`**: Poäng för måttet (0–1).
  - **`timestamp`**: Tidpunkt då måttet registrerades.
  - **`metadata`**: Ytterligare information om måttet.

- **`MetricsReport`**  
  En rapport för kvalitetsmått:
  - **`metrics`**: Senaste måtten per typ.
  - **`averages`**: Genomsnittliga värden per typ.
  - **`trends`**: Trender för varje typ.
  - **`timestamp`**: Tidpunkt då rapporten genererades.

---

#### **2. Klassen `QualityMetrics`**
Hanterar insamling, analys och rapportering av kvalitetsmått.

##### **Huvudfunktioner**
- **`track_metric`**  
  Lägger till ett nytt kvalitetsmått för ett visst innehåll:
  - **Parametrar**: `content_id`, `metric_type`, `value`, `metadata`.

- **`get_metrics`**  
  Hämtar historiska mått för ett innehåll:
  - Stödjer filter som typ (`metric_type`), start- och sluttid.

- **`generate_report`**  
  Skapar en rapport som inkluderar:
  - **`metrics`**: Senaste måtten.
  - **`averages`**: Genomsnitt per måttyp.
  - **`trends`**: Förändringar över tid.

- **`export_metrics` / `import_metrics`**  
  Exporterar/importerar mått till/från format som JSON eller CSV.

##### **Anpassning**
- **`register_custom_metric`**  
  Registrerar en användardefinierad typ av mått.
  
- **`remove_custom_metric`**  
  Tar bort en användardefinierad måttyp.

##### **Historikhantering**
- **`clear_metrics`**  
  Rensar historiken för ett specifikt innehåll eller måttyp.
