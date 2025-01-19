### **Sammanfattning av `models/artifacts.py`**

#### **Klasser**
1. **`ArtifactType`** *(Enumeration)*  
   - Definierar tillgängliga typer av artifacts:  
     - `CODE`, `MARKDOWN`, `HTML`, `SVG`, `MERMAID`, `REACT`.

2. **`ArtifactMetadata`** *(Dataclass)*  
   - Representerar metadata för ett artifact:  
     - `created_at`, `modified_at`, `version`, `creator`, `size`, `checksum`, m.m.  

3. **`ValidationResult`** *(Dataclass)*  
   - Valideringsstatus och resultat:  
     - `valid` (bool): Anger om artifact är giltigt.  
     - `errors` (List): Lista över valideringsfel.  
     - `warnings` (List): Lista över varningar.  

4. **`Artifact`** *(Dataclass)*  
   - Representerar ett artifact:  
     - `id`, `type`, `content`, `metadata`, `validation`, `parent_id`.  
   - Innehåller funktioner för:  
     - Validering (`validate`), innehållsuppdatering (`update_content`), export till fil (`export_file`), XML-hantering m.m.

5. **`ArtifactCollection`** *(Samling av artifacts)*  
   - Hanterar en uppsättning artifacts med funktioner för:  
     - Tillagning och borttagning (`add_artifact`, `remove_artifact`).  
     - Filtrering efter typ (`get_artifacts_by_type`) och taggar (`get_artifacts_by_tag`).  

6. **Undantagsklasser**  
   - **`ArtifactError`**: Bas för artifact-relaterade fel.  
   - **`ArtifactValidationError`**: När validering misslyckas.  
   - **`ArtifactTypeError`**: Vid typmismatch.  
   - **`ArtifactNotFoundError`**: Artifact saknas.  

---

### **Viktiga funktioner i `Artifact`**
1. **Validering (`validate`)**  
   - Validerar artifact-innehåll och metadata baserat på typen.  
   - **Exempel på typ-specifika regler:**  
     - **`CODE`**: Kräver språk i metadata.  
     - **`REACT`**: Kräver `export default` i innehållet.  
     - **`SVG`**: Kräver `<svg>` som rot.  
     - **`HTML`**: Kontrollerar externa resurser och HTML-struktur.

2. **Innehållsuppdatering (`update_content`)**  
   - Uppdaterar artifact-innehåll, storlek och checksum och kör om validering.  

3. **Taggar och beroenden**  
   - Hantera taggar (`add_tag`, `remove_tag`) och beroenden (`add_dependency`, `remove_dependency`).  

4. **Exportfunktioner**  
   - Exportera till fil (`export_file`) eller XML (`to_xml`).  
