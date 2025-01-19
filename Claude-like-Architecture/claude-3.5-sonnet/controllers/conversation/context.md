### **Sammanfattning av `context.py`**

#### **1. Dataklass och Funktionalitet**

- **`ContextItem` (dataclass):**  
  Representerar en individuell kontextpost:
  - `id`: Unikt ID för objektet.
  - `content`: Innehåll för kontextobjektet.
  - `timestamp`: När objektet skapades.
  - `importance`: Betydelsevärde (0-1) som används för prioritering.
  - `ttl`: Time-to-live (valfritt).
  - `metadata`: Metadata som kan innehålla ytterligare information.

#### **2. Klassen `ConversationContext`**

`ConversationContext` hanterar konversationens kontext och minne.

##### **Attribut**
- **`max_context_size`**: Max antal kontextobjekt som lagras.
- **`context_items`**: Kontextobjekt lagrade som en `deque` för varje konversation (identifieras med UUID).
- **`importance_thresholds`**: Tröskelvärde för att bestämma vilka objekt som lagras baserat på deras viktighet.
- **`context_handlers`**: Hanterare för olika typer av innehåll (t.ex. text, kod, sammanfattningar).

##### **Metoder**
- **Hantering och Uppdatering av Kontext**
  - **`manage_context`**: Hanterar kontexten för en konversation, inkluderar processande av nya meddelanden och rensning av föråldrade objekt.
  - **`add_context_item`**: Lägger till ett nytt kontextobjekt.
  - **`get_context`**: Hämtar lagrade kontextobjekt, filtrerar efter viktighet, antal eller innehållstyp.
  - **`update_importance`**: Uppdaterar viktigheten för ett specifikt objekt.
  - **`remove_context_item`**: Tar bort ett specifikt kontextobjekt.
  - **`clear_context`**: Rensar kontexten, antingen helt eller baserat på minimiviktighet.

- **Optimering och Styrning**
  - **`optimize_context`**: Optimerar kontexten genom att ta bort mindre viktiga objekt om det behövs.
  - **`update_importance_threshold`**: Uppdaterar tröskelvärdet för viktighet för en konversation.
  - **`add_context_handler`**: Lägger till en specialiserad hanterare för en viss innehållstyp.
  - **`remove_context_handler`**: Tar bort en befintlig innehållshanterare.

- **Interna Hjälpmetoder**
  - **`_process_new_messages`**: Processar nya meddelanden och uppdaterar kontexten.
  - **`_cleanup_expired_items`**: Tar bort objekt vars tidsgräns har gått ut.
  - **`_is_expired`**: Avgör om ett objekt är föråldrat.
  - **`_calculate_importance`**: Beräknar ett meddelandes viktighet baserat på längd, roll och ålder.
  - **`_determine_content_type`**: Identifierar innehållstyp (text, kod, sammanfattning, referens).
  - **`_handle_text_context`**: Bearbetar textinnehåll.
  - **`_handle_code_context`**: Bearbetar kodinnehåll, inklusive borttagning av kodblocksmärkning.
  - **`_handle_summary_context`**: Hanterar sammanfattningsinnehåll.
  - **`_handle_reference_context`**: Hanterar referensinnehåll.

##### **Felhantering**
Fel som uppstår under kontexthantering kastar ett `ContextError`-undantag. Exempel på fel inkluderar:
- Ogiltigt viktighetsvärde.
- Åtkomst till en icke-existerande konversation.
