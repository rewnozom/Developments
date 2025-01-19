### **Sammanfattning av `state.py`**

#### **1. Klasser och Enums**

- **`ConversationState` (Enum):**  
  Representerar tillstånd i en konversation:
  - `INITIALIZED`: Konversationen är skapad men inte aktiv.
  - `ACTIVE`: Konversationen pågår.
  - `PAUSED`: Konversationen är pausad.
  - `COMPLETED`: Konversationen är avslutad.
  - `ERROR`: Ett fel har uppstått.

- **`StateTransition` (dataclass):**  
  Representerar en övergång mellan två tillstånd:
  - `from_state`: Tillstånd före övergången.
  - `to_state`: Tillstånd efter övergången.
  - `timestamp`: Tidpunkt för övergången.
  - `reason`: Orsak till övergången (valfritt).
  - `metadata`: Ytterligare data om övergången (valfritt).

#### **2. Klassen `StateManager`**

`StateManager` hanterar konversationers tillstånd och tillståndsövergångar.

- **Attribut:**
  - `states`: En mappning av konversations-ID till dess aktuella tillstånd.
  - `transitions`: En historik av tillståndsövergångar per konversations-ID.
  - `valid_transitions`: Lista över tillåtna tillståndsövergångar.
  - `state_handlers`: Funktioner som hanterar specifika tillstånd.
  - `transition_handlers`: Funktioner som hanterar specifika övergångar mellan tillstånd.

- **Metoder:**
  - `initialize_state(conversation: Conversation) -> bool`: Initierar tillståndet för en ny konversation.
  - `transition_state(conversation_id: UUID, to_state: ConversationState, reason: str, metadata: Dict[str, Any]) -> bool`: Utför en övergång till ett nytt tillstånd.
  - `get_state(conversation_id: UUID) -> Optional[ConversationState]`: Hämtar det aktuella tillståndet för en konversation.
  - `get_transitions(conversation_id: UUID) -> List[StateTransition]`: Hämtar historiken av övergångar för en konversation.
  - `validate_state(conversation_id: UUID, expected_state: ConversationState) -> bool`: Validerar om konversationen är i ett förväntat tillstånd.
  - `can_transition(conversation_id: UUID, to_state: ConversationState) -> bool`: Kontrollerar om en övergång till ett specifikt tillstånd är tillåten.
  - `get_valid_transitions(conversation_id: UUID) -> List[ConversationState]`: Returnerar en lista över möjliga övergångar från det aktuella tillståndet.
  - `reset_state(conversation_id: UUID) -> bool`: Återställer en konversation till initialiserat tillstånd.
  - `clear_state(conversation_id: UUID) -> bool`: Tar bort en konversations tillstånd och historik.
  - `get_state_duration(conversation_id: UUID, state: Optional[ConversationState]) -> float`: Beräknar hur länge en konversation har varit i ett specifikt tillstånd.

- **Handlers:**
  - Standard- och anpassningsbara funktioner för att hantera tillstånd och övergångar, t.ex. `_handle_initialized`, `_handle_active`.

#### **3. Validering och Felhantering**
- Kontroll av tillåtna övergångar sker med `valid_transitions`.
- Felhantering via `StateError` används vid ogiltiga operationer.

