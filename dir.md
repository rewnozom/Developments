📁 Developments
├── 📁 Auto_job_seaker
    ├── 📁 del1_Live
        ├── 📁 job
            ├── 📁 DataProcessing
                ├── 🐍 duplicate_handler.py
                ├── 🐍 job_filter.py
                ├── 🐍 job_scorer.py
            ├── 📁 DataSources
                ├── 🐍 job_parser.py
                ├── 🐍 job_scraper.py
            ├── 📁 Storage
                ├── 🐍 data_exporter.py
                ├── 🐍 data_importer.py
            ├── 📁 Utils
                ├── 🐍 config_manager.py
                ├── 🐍 delay_handler.py
                ├── 🐍 logger_setup.py
            ├── 📁 Visualization
                ├── 🐍 job_dashboard.py
        ├── 📁 logs
        ├── 📁 output
        ├── 📁 reverse
        ├── 🐍 main.py
        ├── 🐍 omvandla.py
├── 📁 Claude-like-Architecture
    ├── 📁 claude-3.5-sonnet
        ├── 📁 config
            ├── 🐍 __init__.py
            ├── 📝 constants.md
            ├── 🐍 constants.py
            ├── 📝 logging.md
            ├── 🐍 logging.py
            ├── 📝 settings.md
            ├── 🐍 settings.py
        ├── 📁 controllers
            ├── 📁 conversation
                ├── 🐍 __init__.py
                ├── 📝 context.md
                ├── 🐍 context.py
                ├── 📝 flow.md
                ├── 🐍 flow.py
                ├── 📝 state.md
                ├── 🐍 state.py
            ├── 📁 quality
                ├── 🐍 __init__.py
                ├── 📝 assurance.md
                ├── 🐍 assurance.py
                ├── 📝 metrics.md
                ├── 🐍 metrics.py
                ├── 📝 optimization.md
                ├── 🐍 optimization.py
            ├── 📁 safety
                ├── 🐍 __init__.py
                ├── 📝 boundary.md
                ├── 🐍 boundary.py
                ├── 📝 content.md
                ├── 🐍 content.py
                ├── 📝 validation.md
                ├── 🐍 validation.py
        ├── 📁 core
            ├── 🐍 __init__.py
            ├── 📝 base.md
            ├── 🐍 base.py
            ├── 📝 config.md
            ├── 🐍 config.py
            ├── 📝 constants.md
            ├── 🐍 constants.py
            ├── 📝 exceptions.md
            ├── 🐍 exceptions.py
        ├── 📁 generators
            ├── 📁 artifacts
                ├── 🐍 __init__.py
                ├── 📝 code.md
                ├── 🐍 code.py
                ├── 📝 markdown.md
                ├── 🐍 markdown.py
                ├── 📝 special.md
                ├── 🐍 special.py
            ├── 📁 response
                ├── 🐍 __init__.py
                ├── 📝 builder.md
                ├── 🐍 builder.py
                ├── 📝 formatter.md
                ├── 🐍 formatter.py
                ├── 📝 validator.md
                ├── 🐍 validator.py
        ├── 📁 interfaces
            ├── 🐍 __init__.py
            ├── 🐍 controller.py
            ├── 🐍 generator.py
            ├── 📝 interfaces.md
            ├── 🐍 processor.py
        ├── 📁 logs
        ├── 📁 managers
            ├── 🐍 __init__.py
            ├── 📝 context.md
            ├── 🐍 context.py
            ├── 📝 memory.md
            ├── 🐍 memory.py
            ├── 📝 resources.md
            ├── 🐍 resources.py
            ├── 📝 tokens.md
            ├── 🐍 tokens.py
        ├── 📁 models
            ├── 🐍 __init__.py
            ├── 📝 artifacts.md
            ├── 🐍 artifacts.py
            ├── 📝 conversation.md
            ├── 🐍 conversation.py
            ├── 🐍 llm_models.py
            ├── 📝 response.md
            ├── 🐍 response.py
        ├── 📁 processors
            ├── 🐍 __init__.py
            ├── 📝 content_processor.md
            ├── 🐍 content_processor.py
            ├── 📝 format_processor.md
            ├── 🐍 format_processor.py
            ├── 📝 input_processor.md
            ├── 🐍 input_processor.py
            ├── 📝 output_processor.md
            ├── 🐍 output_processor.py
        ├── 📁 requirements
            ├── 📄 base.txt
            ├── 📄 dev.txt
            ├── 📄 test.txt
        ├── 📁 scripts
            ├── 📁 utils
                ├── 🐍 cleanup.py
                ├── 🐍 install.py
                ├── 🐍 validate.py
            ├── 🐍 setup.py
        ├── 📁 services
            ├── 🐍 __init__.py
            ├── 📝 analytics.md
            ├── 🐍 analytics.py
            ├── 📝 optimization.md
            ├── 🐍 optimization.py
            ├── 📝 validation.md
            ├── 🐍 validation.py
        ├── 📁 tests
            ├── 📁 e2e
                ├── 🐍 __init__.py
                ├── 🐍 test_conversation.py
            ├── 📁 integration
                ├── 🐍 __init__.py
                ├── 🐍 test_conversation_flow.py
                ├── 🐍 test_system.py
            ├── 📁 unit
                ├── 🐍 __init__.py
                ├── 🐍 test_controllers.py
                ├── 🐍 test_core.py
                ├── 🐍 test_exceptions.py
                ├── 🐍 test_generators.py
                ├── 🐍 test_models.py
                ├── 🐍 test_processors.py
                ├── 🐍 test_services.py
                ├── 🐍 test_utils.py
                ├── 📝 unit.md
            ├── 🐍 conftest.py
            ├── 📝 test.md
        ├── 📁 utils
            ├── 🐍 __init__.py
            ├── 📝 formatters.md
            ├── 🐍 formatters.py
            ├── 📝 helpers.md
            ├── 🐍 helpers.py
            ├── 📝 validators.md
            ├── 🐍 validators.py
        ├── 📄 bash_api.bash
        ├── 📝 main.md
        ├── 🐍 main.py
        ├── 📄 requirements.txt
        ├── 🐍 setup.py
        ├── 📋 system_state.json
        ├── 🐍 test_message.py
        ├── 🐍 test_messages.py
    ├── 📁 frontend
        ├── 📁 docker
            ├── 📄 healthcheck.sh
        ├── 📁 docs
            ├── 📁 architecture
                ├── 📝 frontend.md
            ├── 📝 api.md
            ├── 📝 components.md
            ├── 📝 testing.md
            ├── 📝 theme.md
        ├── 📁 scripts
            ├── 📜 analyze.js
            ├── 📜 build.js
        ├── 📁 src
            ├── 📁 api
                ├── 📘 claude.ts
            ├── 📁 components
                ├── 📁 Artifacts
                    ├── ⚛️ ArtifactContainer.tsx
                    ├── ⚛️ CodeArtifact.tsx
                    ├── ⚛️ MarkdownArtifact.tsx
                ├── 📁 Chat
                    ├── 📁 __tests__
                        ├── ⚛️ ChatContainer.test.tsx
                        ├── ⚛️ ChatInput.test.tsx
                        ├── ⚛️ ConversationSearch.test.tsx
                    ├── ⚛️ ChatContainer.tsx
                    ├── ⚛️ ChatInput.tsx
                    ├── ⚛️ ChatMessage.test.tsx
                    ├── ⚛️ ChatMessage.tsx
                    ├── ⚛️ ConversationActions.tsx
                    ├── ⚛️ ConversationSearch.tsx
                    ├── 📘 types.ts
                ├── 📁 common
                    ├── 📁 Modal
                        ├── ⚛️ Modal.tsx
                    ├── 📁 Toast
                        ├── ⚛️ Toast.tsx
                        ├── ⚛️ ToastContainer.tsx
                    ├── ⚛️ ErrorBoundary.tsx
                    ├── ⚛️ IconWrapper.tsx
                    ├── ⚛️ Loading.tsx
                ├── 📁 Layout
                    ├── ⚛️ Header.tsx
                    ├── ⚛️ Sidebar.tsx
                ├── 📁 Response
                    ├── ⚛️ ResponseContainer.tsx
                    ├── ⚛️ ResponseContent.tsx
                    ├── 📘 types.ts
                ├── 📁 Settings
                    ├── ⚛️ AISettings.tsx
                    ├── ⚛️ SettingsModal.tsx
                    ├── ⚛️ ThemeSelector.tsx
            ├── 📁 config
                ├── 📘 apiConfig.ts
                ├── 📘 constants.ts
                ├── 📘 features.ts
            ├── 📁 constants
                ├── 📘 theme.ts
            ├── 📁 contexts
                ├── ⚛️ ChatContext.tsx
                ├── ⚛️ ConversationContext.tsx
                ├── ⚛️ SettingsContext.tsx
                ├── ⚛️ ThemeContext.tsx
            ├── 📁 hooks
                ├── 📁 __tests__
                    ├── 📘 useChat.test.ts
                ├── 📘 useArtifacts.ts
                ├── 📘 useChat.ts
                ├── 📘 useClaudeApi.ts
                ├── 📘 useDebounce.ts
                ├── 📘 useSearch.ts
                ├── 📄 useTheme.t
            ├── 📁 lib
                ├── 📘 claude.ts
                ├── 📘 markdown.ts
            ├── 📁 providers
                ├── 📁 __tests__
                    ├── ⚛️ StreamingProvider.test.tsx
                ├── 📘 base.ts
                ├── ⚛️ ChatProvider.tsx
                ├── 📘 groq.ts
                ├── 📘 index.ts
                ├── 📘 local-ai.ts
                ├── ⚛️ StreamingProvider.tsx
                ├── 📘 types.ts
            ├── 📁 services
                ├── 📘 conversationExporter.ts
                ├── 📘 draftManager.ts
                ├── 📘 storage.ts
            ├── 📁 styles
                ├── 🎨 globals.css
            ├── 📁 test
                ├── 📁 mocks
                    ├── 📘 handlers.ts
                    ├── 📘 server.ts
                ├── 📁 utils
                    ├── ⚛️ test-utils.tsx
                ├── 📘 setup.ts
            ├── 📁 types
                ├── 📘 api.ts
                ├── 📘 common.ts
                ├── 📘 conversation.ts
                ├── 📘 index.ts
                ├── 📘 remark-plugins.d.ts
                ├── 📘 settings.ts
                ├── 📘 theme.ts
                ├── 📘 unist-util-visit.d.ts
            ├── 📁 utils
                ├── 📘 index.ts
                ├── 📘 storage.ts
                ├── 📘 theme.ts
                ├── 📘 validation.ts
            ├── ⚛️ App.tsx
            ├── ⚛️ main.tsx
            ├── 📝 src_dir.md
            ├── 📘 vite-env.d.ts
        ├── ⚙️ docker-compose.yml
        ├── 📄 Dockerfile
        ├── 📄 dockerfile-updated
        ├── 🌐 index.html
        ├── 📜 jest.setup.js
        ├── 📄 nginx.conf
        ├── 📋 package.json
        ├── 📜 postcss.config.js
        ├── 📝 README.md
        ├── 📜 tailwind.config.js
        ├── 📋 tsconfig.json
        ├── 📋 tsconfig.node.json
        ├── 📘 vite.config.ts
        ├── 📘 vitest.config.ts
    ├── 📝 __Theme__.md
    ├── ⚙️ docker-compose.yml
    ├── 📋 package-lock.json
    ├── 📋 package.json
    ├── 📝 README.md
    ├── 📄 remove-pycache-script.ps1
    ├── 📋 system_state.json
├── 📁 Dashboard
    ├── 📁 utils
        ├── 🐍 __init__.py
        ├── 🐍 card_utils.py
        ├── 🐍 theme_utils.py
    ├── 🐍 _old_dashboard_note_.py
    ├── 🐍 ai_vault_tab.py
    ├── 🐍 dashboard.py
    ├── 📝 dir.md
    ├── 🐍 search_tab.py
├── 📁 Development Tools
    ├── 📁 Converter
        ├── 🐍 convert_hf_to_gguf.py
    ├── 📁 tools
        ├── 🐍 _auto_requirements_.py
        ├── 🐍 create_init_to_all_directories.py
        ├── 🐍 directory-creator.py
        ├── 🐍 file-organizer.py
        ├── 🐍 rensa_pycache.py
        ├── 🐍 tools.py
    ├── 📄 remove-pycache-script.ps1
    ├── 📄 STRUCTURE.ps1
├── 📁 fast_whisper_v2
    ├── 📋 config.json
    ├── 🐍 main.py
    ├── 📝 README.md
    ├── 📄 requirements.txt
    ├── 🐍 setup.py
    ├── 🐍 theme_manager.py
├── 📁 Frameworks
├── 📁 frontend
    ├── 📁 live
        ├── 📁 dashboard
            ├── 📁 json
                ├── 📋 search_fields.json
├── 📁 LoRA_data_prep_text_llm
    ├── 📁 random_parquet_examples
        ├── 📁 LLM_DATA
            ├── 🐍 llm_data- (1).py
            ├── 🐍 llm_data- (10).py
            ├── 🐍 llm_data- (11).py
            ├── 🐍 llm_data- (2).py
            ├── 🐍 llm_data- (3).py
            ├── 🐍 llm_data- (4).py
            ├── 🐍 llm_data- (5).py
            ├── 🐍 llm_data- (6).py
            ├── 🐍 llm_data- (7).py
            ├── 🐍 llm_data- (8).py
            ├── 🐍 llm_data- (9).py
        ├── 🐍 !llm_example0.py
        ├── 🐍 !llm_example1.py
        ├── 🐍 !Merge_pq_Data.py
        ├── 🐍 !merge.py
        ├── 🐍 !print.py
        ├── 📝 #example.md
        ├── 🐍 ai-agent-interaction-dataset.py
        ├── 🐍 Auto_llm_datas.py
        ├── 🐍 check.py
        ├── 🐍 convert_to_pq_IC.py
        ├── 🐍 convert_to_pq.py
        ├── 🐍 DATA_v001.py
        ├── 📝 generate simulate.md
        ├── 🐍 llm_1.py
        ├── 🐍 llm_data - Copy.py
        ├── 🐍 llm_data-x - Copy.py
        ├── 🐍 llm_data-x.py
        ├── 🐍 Merge_and_group_IC - claude.py
        ├── 🐍 Merge_and_group_IC - gpt.py
        ├── 🐍 Merge_and_group_IC.py
        ├── 📝 system_prompt.md
        ├── 🐍 test5.py
    ├── 🐍 chat.py
    ├── 🐍 config.py
    ├── 🐍 data_validator.py
    ├── 🐍 json_to_parquet.py
    ├── 🐍 main_lora_prep.py
    ├── 🐍 models.py
    ├── 🐍 parquet_conver_json.py
    ├── 🐍 theme_manager.py
    ├── 📝 theme.md
├── 📁 Markdown_csv_extract
    ├── 📁 summerize_extract
        ├── 🐍 __init__.py
        ├── 🐍 Extractorz.py
    ├── 📁 tests
        ├── 🐍 gui_test_Functionality_and_Interactions.py
        ├── 🐍 gui_testStructure_and_Widgets.py
        ├── 🐍 test_CodeBlock.py
        ├── 🐍 test_CSVEx.py
        ├── 🐍 test_ExtractorWorker.py
        ├── 🐍 test_MarkdownEx.py
        ├── 🐍 test_reverse_csv_extraction.py
        ├── 🐍 test_reverse_markdown_extraction.py
        ├── 🐍 test_ReverseCSVEx.py
        ├── 🐍 test_ReverseMarkdownEx.py
    ├── 🐍 _gui_.py
    ├── 📄 README
    ├── 📄 requirements.txt
    ├── ⚙️ settings.toml
    ├── 📄 settings.toml.example
├── 📁 Markdown_csv_extract_to_android
    ├── 📁 android
        ├── 🐍 __init__.py
        ├── 🐍 AppearanceSection.py
        ├── 🐍 BottomControls.py
        ├── 🐍 CheckboxFrame.py
        ├── 🐍 FileChooserDialog.py
        ├── 🐍 FileChooserModeSection.py
        ├── 🐍 FileSpecificSection.py
        ├── 🐍 GUI_Constants_and_Settings.py
        ├── 🐍 HeaderWidget.py
        ├── 🐍 Phone_Touch_and_Scroll.py
        ├── 🐍 SettingsSection.py
        ├── 🐍 Theme.py
    ├── 📁 backends
        ├── 📁 signals
        ├── 📁 workers
            ├── 🐍 extraction_manager.py
            ├── 🐍 extraction_worker.py
        ├── 🐍 __init__.py
        ├── 🐍 Extractorz.py
    ├── 📁 settings
        ├── ⚙️ settings.toml
    ├── 🐍 __phone_extr_v_00_0a1.py
    ├── 🐍 __phone_extr_v_00_0b1.py
    ├── 🐍 __phone_extr_v_00_0c1.py
    ├── 🐍 __phone_extr_v_01_1.py
    ├── 🐍 __phone_extr_v_01_2.py
    ├── 🐍 __phone_extr_v_01_3.py
├── 📁 tobias-raanaes_v10
    ├── 📁 public
        ├── 📁 icons
        ├── 📁 images
            ├── 🖼️ 11.png
            ├── 🖼️ BAM.png
    ├── 📁 src
        ├── 📁 components
            ├── 📁 common
                ├── ⚛️ Button.jsx
                ├── ⚛️ HelpModal.jsx
                ├── ⚛️ LockedDiagram.jsx
                ├── ⚛️ LockMessageModal.jsx
                ├── ⚛️ MobileDisabledMessage.jsx
                ├── ⚛️ PhoneContact.jsx
                ├── ⚛️ ToggleSection.jsx
            ├── 📁 diagrams
                ├── 📜 diagramDefinition.js
                ├── 📝 mermaid.md
                ├── 📜 MermaidViewer.js
                ├── 📜 NavigationController.js
                ├── ⚛️ ProjectMermaid.jsx
                ├── 📜 ReactDiagram.js
                ├── 📝 ReactDiagram.md
                ├── 📝 test.md
                ├── 📜 ZoomController.js
            ├── 📁 layout
                ├── ⚛️ Footer.jsx
                ├── ⚛️ Header.jsx
                ├── ⚛️ SectionWrapper.jsx
            ├── 📁 sections
                ├── ⚛️ Contact.jsx
                ├── ⚛️ Education.jsx
                ├── ⚛️ Experience.jsx
                ├── ⚛️ Kontaktformular.jsx
                ├── ⚛️ Languages.jsx
                ├── ⚛️ Profile.jsx
                ├── ⚛️ Projects.jsx
                ├── ⚛️ Skills.jsx
            ├── 📁 ui
                ├── ⚛️ Card.jsx
                ├── ⚛️ ListItem.jsx
                ├── ⚛️ Title.jsx
            ├── 📁 utils
                ├── ⚛️ ProjectCard.jsx
                ├── ⚛️ SkillCard.jsx
            ├── ⚛️ App.jsx
            ├── ⚛️ ErrorBoundary.jsx
            ├── ⚛️ LanguageSwitcher.jsx
            ├── ⚛️ Navigationbar.jsx
            ├── ⚛️ TableOfContents.jsx
            ├── ⚛️ ThemeSwitcher.jsx
        ├── 📁 context
            ├── 📜 LanguageContext.js
            ├── 📜 ThemeContext.js
        ├── 📁 hooks
            ├── 📜 useIsMobile.js
            ├── 📜 useIsSmallScreen.js
            ├── 📜 useToggle.js
        ├── 📁 styles
            ├── 📁 default
                ├── 🎨 animations.css
                ├── 🎨 cards.css
                ├── 🎨 components.css
                ├── 🎨 index.css
                ├── 🎨 layout.css
                ├── 🎨 reset.css
                ├── 🎨 responsive.css
                ├── 🎨 sections.css
                ├── 🎨 typography.css
                ├── 🎨 utilities.css
                ├── 🎨 variables.css
            ├── 📁 themes
                ├── 🎨 dark.css
            ├── 🎨 animations.css
            ├── 🎨 base.css
            ├── 🎨 components.css
            ├── 🎨 mermaid_phone.css
        ├── 📁 tests
            ├── 📜 App.test.js
            ├── 📜 utils.test.js
        ├── 📁 translations
            ├── 📁 projects
                ├── 📜 ai_integration.js
                ├── 📜 auto_docs.js
                ├── 📜 auto_schema.js
                ├── 📜 business_value.js
                ├── 📜 gui_framework.js
                ├── 📜 index.js
                ├── 📜 main_system.js
                ├── 📜 structure_management.js
                ├── 📜 synthetic_data.js
            ├── 📜 aiAgent.js
            ├── 📜 arbetslivserfarenhet.js
            ├── 📜 index.js
            ├── 📜 kontaktformulartext.js
            ├── 📜 projectTranslation.js
            ├── 📜 projekt.js
            ├── 📜 sprakkunskaper.js
            ├── 📜 tekniska_fardigheter.js
            ├── 📜 utbildning.js
        ├── ⚛️ App.jsx
        ├── 📜 index.js
    ├── 📁 style
        ├── 🎨 index.css
    ├── 📝 __Theme__.md
    ├── 📄 .env.local.example
    ├── 📄 .eslintrc.cjs
    ├── 📜 .eslintrc.js
    ├── 👁️ .gitignore
    ├── 🌐 index.html
    ├── ⚙️ netlify.toml
    ├── 📘 next-env.d.ts
    ├── 📘 next.config.ts
    ├── 📋 package.json
    ├── 📜 postcss.config.js
    ├── 📝 README.md
    ├── 📘 tailwind.config.ts
    ├── 📋 tsconfig.json
    ├── 📜 vite.config.js
├── 👁️ .gitignore
├── 📄 auto_requirements.txt
├── 📝 dir.md
├── 📝 README.md
├── 📋 search_fields.json