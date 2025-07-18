# llm_utils.py
from llama_cpp import Llama
import os
import json
from huggingface_hub import hf_hub_download

HF_MODEL_REPO_ID = "TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF"
MODEL_FILENAME = "tinyllama-1.1b-chat-v0.3.Q4_K_M.gguf"

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

llm_model = None

def load_llm_model():
    global llm_model
    if llm_model is None:
        os.makedirs(MODELS_DIR, exist_ok=True)

        if not os.path.exists(MODEL_PATH):
            print(f"Model not found, downloading {MODEL_FILENAME} from {HF_MODEL_REPO_ID}...")
            try:
                hf_hub_download(
                    repo_id=HF_MODEL_REPO_ID,
                    filename=MODEL_FILENAME,
                    local_dir=MODELS_DIR,
                    local_dir_use_symlinks=False
                )
                print("Model downloaded successfully.")
            except Exception as e:
                raise RuntimeError(f"Failed to download LLM model: {e}")

        print(f"Loading LLM model from {MODEL_PATH}...")
        llm_model = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=0,
            n_ctx=2048,
            n_threads=os.cpu_count() // 2 or 1,
            verbose=False
        )
        print("LLM model loaded.")
    return llm_model

def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 512) -> dict | None:
    global llm_model
    if llm_model is None:
        try:
            load_llm_model()
        except RuntimeError as e:
            print(f"Error: {e}")
            return None

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        output = llm_model.create_chat_completion(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=max_tokens
        )
        
        llm_response_content = None
        if 'choices' in output and len(output['choices']) > 0:
            llm_response_content = output['choices'][0]['message']['content']
        
        if llm_response_content:
            try:
                if llm_response_content.startswith("```json") and llm_response_content.endswith("```"):
                    json_str = llm_response_content[len("```json"):-len("```")].strip()
                else:
                    json_str = llm_response_content
                
                parsed_json = json.loads(json_str)
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"Warning: LLM did not return valid JSON. Error: {e}\nRaw LLM output: {llm_response_content}")
                return None
        else:
            print("Warning: LLM response content was empty.")
            return None
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None