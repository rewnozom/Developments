### Sammanfattning av `models/response.py`


### **Klasser**
1. **`ResponseType`** *(Enumeration)*  
   - Representerar typer av svar: `TEXT`, `CODE`, `ERROR`, `FUNCTION`, `ARTIFACT`.  
   - **Relevans**: Används för att kategorisera svar och styra hur de hanteras.

2. **`ResponseMetadata`** *(Dataclass)*  
   - Representerar metadata för ett svar.  
   - **Attribut:**  
     - `created_at`: När svaret skapades.  
     - `processing_time`: Tid i sekunder för att generera svaret.  
     - `model`: Modell som genererade svaret.  
     - `tokens`: Antal tokens i svaret.  
     - `context_tokens`: Tokens från kontexten.  
     - `prompt_tokens`: Tokens från prompten.  
     - `finish_reason`: Orsak till att genereringen avslutades.  
     - `custom_data`: Anpassad metadata.  
   - **Relevans**: Viktigt för att analysera prestanda och kontext.  

3. **`ResponseFormat`** *(Dataclass)*  
   - Beskriver formatet för ett svar.  
   - **Attribut:**  
     - `type`: Typ av format (`ResponseType`).  
     - `template`: Formatmall för svaret (valfritt).  
     - `style`: Stil-attribut för svarspresentation (valfritt).  
     - `constraints`: Eventuella begränsningar i formatet (valfritt).  
   - **Relevans**: Används för att standardisera svarspresentation.  

4. **`Response`** *(Dataclass)*  
   - Representerar ett komplett svar.  
   - **Attribut:**  
     - `id`: Unikt UUID för svaret.  
     - `content`: Textinnehåll i svaret.  
     - `type`: Typ av svaret (`ResponseType`).  
     - `metadata`: Metadata som beskriver svaret (`ResponseMetadata`).  
     - `format`: Specificerar formatet (`ResponseFormat`, valfritt).  
     - `parent_id`: UUID för ett relaterat svar (valfritt).  
     - `references`: Lista av UUID för relaterade referenser.  
     - `artifacts`: Lista av UUID för relaterade artefakter.  
   - **Relevans**: Huvudklassen för att hantera och representera svar från assistenten.  

---

### **Viktiga metoder i `Response`**
1. **`to_dict()` / `from_dict(data: Dict[str, Any])`**  
   - Konverterar objektet till/från en ordbok.  
   - **Relevans**: Viktig för serialisering och deserialisering.  

2. **`add_reference(reference_id: UUID)`**  
   - Lägger till en referens till svaret.  

3. **`add_artifact(artifact_id: UUID)`**  
   - Lägger till en artefakt till svaret.  

4. **`update_metadata(key: str, value: Any)`**  
   - Uppdaterar anpassad metadata.  

5. **`total_tokens`** *(Property)*  
   - Beräknar det totala antalet tokens som används i svaret.  

6. **`validate()`**  
   - Validerar svarets innehåll och metadata.  
   - **Relevans**: Säkerställer att svaret uppfyller förväntade standarder.  
