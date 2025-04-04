import config
import re
import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

llm_instance = None


def llm_ini():
    global llm_instance

    
        

    try:
        print(f"Loading model {config.MODEL}.")
       
        tokenizer = AutoTokenizer.from_pretrained(config.MODEL)        

        # Add pad token if missing
        if tokenizer.pad_token is None:
            print("Model tokenizer missing pad token, setting to eos_token.")
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            config.MODEL,
            device_map="auto",
            torch_dtype=torch.float16,
            pad_token_id=tokenizer.pad_token_id,
            
            )

        # Create pipeline
        llm_pipeline_instance = pipeline("text-generation",model=model,tokenizer=tokenizer,torch_dtype=torch.float16,device_map="auto")
        print("LLM Pipeline created!")
        return llm_pipeline_instance
    except ImportError as e:
        print(f"Error: Library not found. Make sure 'torch', 'transformers', and 'accelerate' are installed. {e}")
        return None
    except Exception as e:
        print(f"Error initializing LLM pipeline: {e}")
       
        return None
    
def extract_llm(usermessage):
    pipe = llm_ini()
    if not pipe:
        return None
    
    prompt = f"""<s>[INST] Your task is to extract event scheduling information from the user's request.
Identify the event title, date, start time, and end time.

Rules:
- Provide the output strictly in JSON format with the keys: "title", "date", "start_time", "end_time".
- If a value is not mentioned or unclear, use null for that key.
- For the date, try to capture it as specifically as possible (e.g., "next Tuesday", "May 5th", "tomorrow", "April 10th 2025").
- For times, include AM/PM if specified (e.g., "3 PM", "14:00").
- If an end time isn't specified, set "end_time" to null.

User request: "{usermessage}"

[/INST]
```json
"""
    
    try:
        print("Sending request to LLM...")
        sequences = pipe(
            prompt,
            do_sample=True,
            temperature=0.1,
            max_new_tokens=250, 
            num_return_sequences=1,
            eos_token_id=pipe.tokenizer.eos_token_id,
            pad_token_id=pipe.tokenizer.pad_token_id 
        )
        raw_output = sequences[0]['generated_text']
        print(f"Raw LLM Output:\n{raw_output}")

        inst_end_marker = "[/INST]"
        json_block_marker = "```json"
        json_start_index = raw_output.find(json_block_marker, raw_output.find(inst_end_marker))

        if json_start_index == -1:
            print("Could not find ```json marker after [/INST] in LLM response.")
            
            json_start_index_fallback = raw_output.find('{', raw_output.find(inst_end_marker))
            if json_start_index_fallback != -1:
                 json_end_index_fallback = raw_output.rfind('}') + 1
                 if json_end_index_fallback != -1 and json_start_index_fallback < json_end_index_fallback:
                      json_string = raw_output[json_start_index_fallback:json_end_index_fallback].strip()
                      print(f"Extracted JSON String: {json_string}")
                 else:
                      print("Fallback JSON extraction failed (could not find matching braces).")
                      return None
            else:
                 print("Fallback JSON extraction failed (could not find '{').")
                 return None
        else:
             # Find the closing ```
             json_end_marker = "```"
             json_end_index = raw_output.find(json_end_marker, json_start_index + len(json_block_marker))

             if json_end_index == -1:
                  print("Warning: Found ```json start marker but no closing ``` marker. Attempting to parse till end.")
                  # Take everything after ```json marker
                  json_string = raw_output[json_start_index + len(json_block_marker):].strip()
                  
                  last_brace = json_string.rfind('}')
                  if last_brace != -1:
                       json_string = json_string[:last_brace+1]
                  else:
                       print("Could not find closing brace in remaining string.")
                       return None

             else:
                  
                  json_string = raw_output[json_start_index + len(json_block_marker):json_end_index].strip()

             print(f"Extracted JSON String: {json_string}")


        # Parse the JSON string
        extracted_data = json.loads(json_string)
        expected_keys = ["title", "date", "start_time", "end_time"]
        normalized_data = {key: extracted_data.get(key) for key in expected_keys}


        print(f"Parsed & Normalized LLM Data: {normalized_data}")
        return normalized_data

    except json.JSONDecodeError:
        print(f"Could not decode JSON from extracted string: '{json_string}'")
        return None
    except Exception as e:
        print(f"An error occurred during LLM inference or processing: {e}")
        if "max_new_tokens" in str(e):
             print("Consider increasing max_new_tokens if the JSON response was cut short.")
        return None    
