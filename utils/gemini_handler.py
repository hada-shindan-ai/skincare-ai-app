import os
import requests
import streamlit as st

class GeminiHandler:
    def __init__(self):
        """Initialize Gemini API using requests."""
        try:
            # secrets.tomlからAPIキーを取得 (複数対応)
            keys = st.secrets.get("GEMINI_API_KEYS")
            if keys and isinstance(keys, list):
                self.api_keys = keys
            else:
                single_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
                self.api_keys = [single_key] if single_key else []
            
            if not self.api_keys:
                raise ValueError("GEMINI_API_KEY could not be found.")
                
            self.current_key_idx = 0

        except Exception as e:
            st.error(f"Gemini Handler Initialization Error: {e}")
            self.api_keys = []
            self.current_key_idx = 0

    def get_response(self, user_query, user_context, chat_history=[]):
        """
        Generate response using Gemini with grounding using REST API.
        
        Args:
            user_query (str): The user's question.
            user_context (dict): Dictionary containing 'skin_type', 'age', 'budget', etc.
            chat_history (list): List of chat messages [(role, message, sources), ...]
            
        Returns:
            tuple: (response_text, grounding_metadata)
        """
        if not self.api_keys:
            return "System Error: Gemini API Key is not initialized.", None

        target_items = user_context.get('target_items', [])
        target_str = ", ".join(target_items) if target_items else "Any skincare product"
        
        system_prompt = (
            f"Role: You are a professional dermatological advisor. "
            f"Prioritize medical and scientific sources from Google Search.\n"
            f"User Profile:\n"
            f"- Skin Type based on diagnosis: {user_context.get('skin_type', 'Unknown')}\n"
            f"- Age Group: {user_context.get('age', 'Unknown')}\n"
            f"- Budget Limit: {user_context.get('budget', 'Unknown')} JPY\n"
            f"- Concerns: {', '.join(user_context.get('concerns', []))}\n"
            f"- Target Items Requested: {target_str}\n\n"
            f"Instructions:\n"
            f"1. Acknowledge the user's specifics (e.g. skin type) and that they are looking for [{target_str}] in the opening.\n"
            f"2. Provide evidence-based advice specifically tailored to the requested Target Items.\n"
            f"3. Explain why certain ingredients are effective for their specific concerns within the context of the Target Items.\n"
        )
        
        if "フルライン（一式）" in target_items:
            system_prompt += (
                f"4. CRITICAL RULE: The user selected 'フルライン（一式）'. You MUST propose recommendations as a step-by-step skincare routine (e.g., Wash -> Toner -> Serum -> Cream), explaining the role of each step.\n"
                f"5. IMPORTANT: Make sure to clearly explain the benefits and synergistic effects of using these products in the correct step-by-step order.\n"
                f"6. Support your answer with retrieved information.\n"
                f"7. Be polite and helpful."
            )
        else:
            system_prompt += (
                f"4. Support your answer with retrieved information.\n"
                f"5. Be polite and helpful."
            )
        
        headers = {
            "Content-Type": "application/json"
        }
        
        contents = []
        for role, message, _ in chat_history:
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": message}]
            })
        
        # Add the current user query to the history
        contents.append({
            "role": "user",
            "parts": [{"text": user_query}]
        })
        
        payload = {
            "system_instruction": {
                "parts": {
                    "text": system_prompt
                }
            },
            "contents": contents,
            "tools": [{
                "googleSearch": {}
            }]
        }

        last_error = None
        for _ in range(len(self.api_keys)):
            api_key = self.api_keys[self.current_key_idx]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                # 自動フォールバック: Rate limit (429 Too Many Requests)
                if response.status_code == 429:
                    last_error = f"API Key ending in ...{api_key[-4:]} is rate limited."
                    self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                    continue
                    
                response.raise_for_status()
                response_data = response.json()
                
                # レスポンスの解析
                candidates = response_data.get("candidates", [])
                if not candidates:
                    return "Error: No response generated.", None
                    
                candidate = candidates[0]
                parts = candidate.get("content", {}).get("parts", [])
                response_text = ""
                for part in parts:
                    if "text" in part:
                        response_text += part["text"]
                        
                # Grounding metadata (Simple mock representation for stream compatibility or object access if needed)
                class MockWebChunk:
                    def __init__(self, uri, title):
                        class WebObj:
                            def __init__(self, u, t):
                                self.uri = u
                                self.title = t
                        self.web = WebObj(uri, title)
                
                class MockMetadata:
                    pass
                
                grounding_data = candidate.get("groundingMetadata", {})
                grounding_metadata = None
                
                if grounding_data and "groundingChunks" in grounding_data:
                    grounding_metadata = MockMetadata()
                    grounding_metadata.grounding_chunks = []
                    for chunk in grounding_data["groundingChunks"]:
                        if "web" in chunk:
                            grounding_metadata.grounding_chunks.append(
                                MockWebChunk(chunk["web"].get("uri", ""), chunk["web"].get("title", ""))
                            )
                
                return response_text, grounding_metadata
    
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                    last_error = f"API Key ending in ...{api_key[-4:]} is rate limited."
                    self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
                    continue
                return f"Error communicating with Gemini API: {e}", None
            except Exception as e:
                return f"Error processing response: {e}", None
                
        return f"Error: All provided API Keys are exhausted or rate limited. Please add more keys or wait. Last status: {last_error}", None
