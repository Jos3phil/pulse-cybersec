# agents/ (compañero)

- `runtime.py`: `LLMClient` (Vertex AI, Gemini 4 Argon, versión fija), `FakeLLM` con secuencias grabadas y ciclo de herramientas.
- `prompts/`: instrucciones versionadas de Vigía, Escriba, Archivista y Folio.
- `folio.py`: redactor, autovalidación con `contract/validator.py` y respaldo determinista.

Las herramientas que cada agente puede llamar están en `tools/` (Timothy). El agente solo
puede elegir entre ellas; nunca escribe SQL ni rutas.
