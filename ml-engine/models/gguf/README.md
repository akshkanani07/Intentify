# Local GGUF Model Directory

This directory is monitored by Intentify's `LocalGGUFEngine`.

## How to activate local quantized LLM mode:
1. Download any compatible quantized GGUF model (e.g. `Qwen2.5-3B-Instruct-Q4_K_M.gguf` or `Llama-3.2-3B-Instruct.Q4_K_M.gguf`).
2. Place the `.gguf` file in this directory: `ml-engine/models/gguf/`.
3. Intentify will automatically detect the model file and enable offline local generative augmentation alongside the deterministic contracts and S7 validators.
