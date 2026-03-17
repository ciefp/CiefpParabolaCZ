# [modified file]: components/translator.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import requests
import json
import os

# Podržani jezici sa njihovim kodovima
SUPPORTED_LANGUAGES = [
    ("Serbian", "sr"),
    ("Croatian", "hr"),
    ("Slovenian", "sl"),
    ("Macedonian", "mk"),
    ("Slovak", "sk"),        # Added Slovak
    ("Spanish", "es"),        # Added Spanish
    ("Greek", "el"),          # Added Greek
    ("Arabic", "ar"),         # Added Arabic
    ("English", "en"),
    ("German", "de"),
    ("French", "fr"),
    ("Italian", "it"),
    ("Russian", "ru"),
    ("Hungarian", "hu"),
    ("Romanian", "ro"),
    ("Bulgarian", "bg"),
]

class Translator:
    def __init__(self, api_key=None):
        self.api_key = api_key or self._load_api_key()
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        # Zamenjeno sa aktivnim modelom
        self.model = "llama-3.3-70b-versatile"  # Ovaj model radi
        
    def _load_api_key(self):
        """Učitava API ključ iz konfiguracionog fajla"""
        try:
            config_path = "/etc/enigma2/ciefp_translate.conf"
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return ""
    
    def save_api_key(self, api_key):
        """Čuva API ključ u konfiguracioni fajl"""
        try:
            config_path = "/etc/enigma2/ciefp_translate.conf"
            with open(config_path, "w") as f:
                f.write(api_key.strip())
            self.api_key = api_key.strip()
            return True
        except Exception as e:
            print("Greška pri čuvanju API ključa:", str(e))
            return False
    
    def translate(self, text, target_language="sr", source_language="cs"):
        """
        Prevedi tekst sa češkog na odabrani jezik koristeći Groq API
        
        Args:
            text: Tekst za prevođenje
            target_language: Ciljni jezik (kod, npr. "sr", "hr", "en")
            source_language: Izvorni jezik (podrazumevano češki "cs")
        
        Returns:
            Prevedeni tekst ili original ako dođe do greške
        """
        if not self.api_key or not text:
            return text
        
        # Mapa jezičkih kodova za prompt
        
        language_names = {
            "sr": "Serbian",
            "hr": "Croatian",
            "sl": "Slovenian",
            "mk": "Macedonian",
            "sk": "Slovak",           # Added Slovak
            "es": "Spanish",           # Added Spanish
            "el": "Greek",             # Added Greek
            "ar": "Arabic",            # Added Arabic
            "en": "English",
            "de": "German",
            "fr": "French",
            "it": "Italian",
            "ru": "Russian",
            "hu": "Hungarian",
            "ro": "Romanian",
            "bg": "Bulgarian",
        }
        
        target_lang_name = language_names.get(target_language, "srpski")
        
        # Prompt za prevod
        system_prompt = f"Ti si profesionalni prevodilac. Prevedi tačno ono što ti je dato sa češkog na {target_lang_name} jezik. Zadrži formatiranje, nove redove i strukturu teksta. Prevedi samo tekst, bez dodavanja komentara."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3,
            "max_tokens": 8000
        }
        
        try:
            print("Šaljem zahtev ka Groq API...")  # Debug
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result["choices"][0]["message"]["content"]
                print("Prevod uspešan!")  # Debug
                return translated_text.strip()
            else:
                print(f"Groq API greška: {response.status_code} - {response.text}")
                return text
                
        except Exception as e:
            print("Greška pri prevođenju:", str(e))
            return text

    def test_connection(self):
        """Testira da li je API ključ validan"""
        if not self.api_key:
            return False, "API key is not set"

        try:
            print("Testing connection with API key...")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Minimalni test zahtev
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Hello"}  # Vrlo kratko
                ],
                "max_tokens": 5
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                print("Connection test successful!")
                return True, "Connection successful! API key is valid."
            else:
                print(f"Connection test failed: {response.status_code}")
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                return False, error_msg

        except Exception as e:
            print(f"Connection test exception: {str(e)}")
            return False, f"Connection test failed: {str(e)}"
