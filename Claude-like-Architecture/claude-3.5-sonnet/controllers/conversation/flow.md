### **Sammanfattning av `flow.py`**

#### **1. Klasser och Dataklasser**

- **`FlowMetrics` (dataclass):**  
  Representerar mätvärden för en konversationsflöde:
  - `total_messages`: Totalt antal meddelanden.
  - `average_response_time`: Genomsnittlig svarstid.
  - `topic_changes`: Antal ämnesbyten.
  - `engagement_score`: Engagemangspoäng.
  - `coherence_score`: Sammanhållningspoäng.

- **`FlowControl` (dataclass):**  
  Definierar kontrollparametrar för konversationsflöde:
  - `max_turns`: Max antal meddelanden i konversationen.
  - `response_timeout`: Max svarstid i sekunder.
  - `topic_limit`: Max antal ämnesbyten.
  - `require_acknowledgment`: Kräver bekräftelse för att fortsätta.
  - `maintain_context`: Behåller kontexten genom hela konversationen.

#### **2. Klassen `ConversationFlow`**

`ConversationFlow` hanterar flöde och progression av konversationer.

- **Attribut:**
  - `active_conversations`: Aktivt spårade konversationer, mappade till deras ID.
  - `flow_metrics`: Mätvärden för varje konversation, mappade till dess ID.
  - `flow_controls`: Kontrollparametrar för varje konversation, mappade till dess ID.

- **Metoder:**
  - **`manage_flow`**: Initierar och hanterar en konversationsflöde.
  - **`add_message`**: Lägger till ett nytt meddelande i konversationen.
  - **`maintain_coherence`**: Beräknar och optimerar sammanhållning i konversationen.
  - **`optimize_engagement`**: Optimerar och beräknar engagemang i konversationen.
  - **`_update_metrics`**: Uppdaterar flödesmätvärden för en given konversation.
  - **`_check_flow_controls`**: Validerar och verkställer kontrollparametrar som `max_turns` och `response_timeout`.
  - **`get_metrics`**: Hämtar mätvärden för en specifik konversation.
  - **`get_control`**: Hämtar kontrollinställningarna för en konversation.
  - **`update_control`**: Uppdaterar kontrollparametrar för en konversation.
  - **`end_conversation`**: Avslutar och städar upp resurser för en konversation.

- **Interna beräkningsmetoder:**
  - **`_calculate_response_times`**: Beräknar genomsnittlig svarstid mellan meddelanden.
  - **`_calculate_topic_changes`**: Identifierar ämnesbyten baserat på innehåll.
  - **`_calculate_context_adherence`**: Mäter hur väl kontexten upprätthålls mellan meddelanden.
  - **`_calculate_flow_smoothness`**: Beräknar hur smidigt flödet är i konversationen.
  - **`_calculate_interaction_depth`**: Mäter djupet i interaktionen baserat på meddelandelängd.
  - **`_calculate_user_participation`**: Beräknar användarens deltagande som en andel av meddelanden.
  - **`_is_topic_change`**: Detekterar ämnesbyten mellan två meddelanden.
  - **`_calculate_message_context_score`**: Mäter kontextadherens mellan två meddelanden.
  - **`_calculate_transition_smoothness`**: Beräknar hur smidig övergången är mellan två meddelanden.

#### **3. Felhantering**

Fel vid hantering av konversationsflöde hanteras med undantag (`ConversationError`), till exempel:
- Ogiltiga kontrollparametrar.
- För många ämnesbyten eller svarstidsöverträdelser.
