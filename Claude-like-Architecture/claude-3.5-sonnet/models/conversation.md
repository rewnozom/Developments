### Sammanfattning av `models/conversation.py`


### **Klasser**
1. **`ConversationState`** *(Enumeration)*  
   - Representerar tillstånd för en konversation: `ACTIVE`, `PAUSED`, `COMPLETED`, `ARCHIVED`, `ERROR`.  
   - **Relevans**: Central för att spåra och hantera konversationens status.  

2. **`MessageRole`** *(Enumeration)*  
   - Representerar roller för ett meddelande: `SYSTEM`, `USER`, `ASSISTANT`, `FUNCTION`.  
   - **Relevans**: Viktig för att identifiera kontext i meddelanden.  

3. **`Message`** *(Dataclass)*  
   - Representerar ett enskilt meddelande i en konversation.  
   - **Attribut:**  
     - `id`: UUID för att unikt identifiera meddelandet.  
     - `role`: Meddelandets roll (ex. `USER`).  
     - `content`: Meddelandets textinnehåll.  
     - `timestamp`: Tidpunkt då meddelandet skapades.  
     - `metadata`: Extra information om meddelandet.  
     - `function_call`: Detaljer om en eventuell funktion som anropas.  
     - `tokens`: Antal tokens som används av meddelandet.  
   - **Relevans:** Central del av en konversation, används i hanteringen av meddelanden.  

4. **`ConversationMetadata`** *(Dataclass)*  
   - Innehåller metadata om en konversation.  
   - **Attribut:**  
     - `created_at`, `modified_at`: Tidsstämplar för skapande och senaste ändring.  
     - `total_messages`: Totalt antal meddelanden i konversationen.  
     - `total_tokens`: Totalt antal tokens som används.  
     - `user_id`: Användar-ID kopplat till konversationen.  
     - `labels`: Lista av etiketter som tilldelats konversationen.  
     - `custom_data`: Anpassad metadata.  

5. **`Conversation`** *(Dataclass)*  
   - Representerar en fullständig konversation.  
   - **Attribut:**  
     - `id`: UUID för att identifiera konversationen.  
     - `messages`: Lista över alla meddelanden i konversationen.  
     - `state`: Konversationens tillstånd (`ConversationState`).  
     - `metadata`: Metadata om konversationen.  
   - **Relevans:** Huvudklassen för att hantera och spåra konversationer.  

---

### **Viktiga metoder i `Conversation`**
1. **`add_message(message: Message)`**  
   - Lägger till ett meddelande till konversationen och uppdaterar metadata.  

2. **`get_message(message_id: UUID)`**  
   - Hämtar ett specifikt meddelande baserat på dess UUID.  

3. **`get_context_window(max_tokens: int, from_message_id: Optional[UUID])`**  
   - Hämtar ett fönster av meddelanden som håller sig inom en token-gräns.  

4. **`update_state(new_state: ConversationState)`**  
   - Uppdaterar konversationens tillstånd och tidsstämpel.  

5. **`add_label(label: str)` / `remove_label(label: str)`**  
   - Lägger till eller tar bort etiketter från metadata.  

6. **`to_dict()` / `from_dict(data: Dict[str, Any])`**  
   - Konverterar konversationen till/från en ordboksrepresentation.  
