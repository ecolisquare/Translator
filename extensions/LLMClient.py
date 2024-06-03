import json
with open("config.json", "r") as f:
    config_data = json.load(f)["LLM"]
    if config_data["service"] == "OpenAI":
        from openai import OpenAI as LLM
        import openai as llm
    else:
        from zhipuai import ZhipuAI as LLM
        import zhipuai as llm


from typing import Optional, List, Dict
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type
from utils import estimate_token_num
import re
import logging
import numpy as np

def cosine_similarity(embedding1, embedding2):
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

class LLMClient():
    def __init__(self, client : LLM, service_name: str, model_name: str, embedding_model_name: str, max_token_per_chunk = 1024, model_config={}, inital_messages: List[Dict] = []):
        self.client = client
        self.model = model_name
        self.embedding_model_name = embedding_model_name
        self.token_usage = 0
        self.max_token = max_token_per_chunk
        self.model_config = model_config
        self.initial_messages = inital_messages
        self.service_name = service_name
        self.use_embedding = True
        LLMClient.__instance = self

        logging.getLogger("StreamLogger").info("LLMClient initialied.")
        logging.getLogger("FileLogger").info("LLMClient initialied.")

    # 返回问题的答案
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(4), retry=retry_if_exception_type(llm.APITimeoutError), reraise=False)
    def _get_answer(self, messages: List[Dict]) -> Optional[Dict]:
        if self.service_name == "OpenAI":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                top_p=self.model_config.get("top_p", 1.0),
                max_tokens=self.model_config.get("max_tokens", 100),
                frequency_penalty=self.model_config.get("frequency_penalty", 0.0),
                presence_penalty=self.model_config.get("presence_penalty", 0.0),
            )
        elif self.service_name == "ZhipuAI":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                top_p=self.model_config.get("top_p", 1.0),
                max_tokens=self.model_config.get("max_tokens", 100),
            )
        if response:
            ans = response.choices[0].message.content
            token = response.usage.total_tokens
            self.token_usage += token
            return {
                    "answer": ans, 
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

    @retry(wait=wait_random_exponential(min=300, max=600), stop=stop_after_attempt(6), retry=retry_if_exception_type(llm.APITimeoutError), reraise=True)
    def _get_str_embedding(self, text: str) -> Optional[List[float]]:
        response = self.client.embeddings.create(
            model=self.embedding_model_name,
            input=[text],
        )
        if response:
            return response.data[0]["embedding"]
        else:
            logging.getLogger("FileLogger").error(f"Failed to get embedding for text: {text}. No more similarity algorithms will be used for this text.")
            self.use_embedding = False
            return []

    def translate(self, target_language: str, messages) -> Optional[str]:
        preference = self._extract_preference(messages)
        style = preference["style"]
        user_dict = preference["user_dict"]
        prompts = {}
        summary = {}
        with open("prompts.json", 'r') as f:
            all_prompts = json.load(f)["value"]
            for possible_prompt in all_prompts:
                if target_language in possible_prompt["language"]:
                    prompts = possible_prompt["translate"]
                    summary = possible_prompt["summary"]
                    break
        
        if prompts == {}:
            logging.getLogger("FileLogger").error("No prompts found for the given language pair. Using default prompts.")
            prompts = all_prompts[0]

        whole_text = self._extract_texts(messages)
        paragraphs = self._split_text(whole_text)
        
        translation_texts = []
        global_context = "None"
        para_contexts = []
        para_context_embeddings = []

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        chunk_id = 0
        last_chunk = 'None'
        for paragraph in paragraphs:
            chunk_contexts = []
            for chunk_text in paragraph:
                messages = []
                # prompts
                messages.append(self._generate_llm_message(text=self._fill_format(data=[target_language], to_fill=prompts["defaultMessage"]) , role="system"))
                messages.append(self._generate_llm_message(text=prompts["init_prompt"], role="system"))
                messages.append(self._generate_llm_message(text=prompts["context_prompt"], role="system"))
                messages.append(self._generate_llm_message(text=self._fill_format(data=[','.join(style)], to_fill=prompts["style_prompt"]), role="system"))
                
                filtered_dict = self._filter_user_dict(user_dict, chunk_text)
                if len(filtered_dict) > 0:
                    input_0 = ''
                    for key, value in filtered_dict.items():
                        input_0 += key
                        input_0 += ':'
                        input_0 += value
                        input_0 += ';'
                    messages.append(self._generate_llm_message(text=self._fill_format(data=[input_0], to_fill=prompts["user_dict_prompt"]), role="system"))
                messages.append(self._generate_llm_message(text=prompts["format_prompt"], role="system"))

                
                messages.append(self._generate_llm_message(text=prompts["translate_prompt"], role="user"))

                similar_local_context = self._get_similar_local_context(chunk_text, para_contexts, para_context_embeddings)
                messages.append(self._generate_llm_message(text=self._fill_format(data=[similar_local_context, global_context], to_fill=prompts["input_context_prompt"]), role="user"))
                messages.append(self._generate_llm_message(text=self._fill_format(data=[last_chunk, str(chunk_id), chunk_text], to_fill=prompts["input_text_prompt"]), role="user"))
                
                
                response = self._get_answer(messages)
                if response is None:
                    return None
                token = response["total_tokens"]
                self.token_usage += token

                # TODO
                chunk_id, translation_text, chunk_context = self._parse_answer(response["answer"], "chunk_num", "text", "chunk_context")
                translation_texts.append(translation_text)
                chunk_contexts.append(chunk_context)
                last_chunk = chunk_text
                chunk_id += 1

                prompt_tokens += response["prompt_tokens"]
                completion_tokens += response["completion_tokens"]
                total_tokens += response["total_tokens"]

            new_messages = []
            new_messages.append(self._generate_llm_message(text=summary["defaultMessage"], role="system"))
            new_messages.append(self._generate_llm_message(text=summary["init_prompt"], role="system"))
            new_messages.append(self._generate_llm_message(text=summary["summarize_idea_prompt"], role="system"))
            new_messages.append(self._generate_llm_message(text=summary["format_prompt"], role="system"))
            
            all_chunk_context = ""
            for i in range(len(chunk_contexts)):
                all_chunk_context += f"<CHUNK_CONTEXT_{i}>:"
                all_chunk_context += chunk_contexts[i]
                all_chunk_context += "\n"
            
            new_messages.append(self._generate_llm_message(text=self._fill_format(data=[global_context, all_chunk_context], to_fill=summary["input_context_prompt"]), role="user"))
            

            response = self._get_answer(new_messages)
            global_context, new_para_context = self._parse_answer(response["answer"], "GLOBAL_CONTEXT", "PARA_CONTEXT")
            para_contexts.append(new_para_context)
            para_context_embeddings.append(self._get_str_embedding(new_para_context))

            prompt_tokens += response["prompt_tokens"]
            completion_tokens += response["completion_tokens"]
            total_tokens += response["total_tokens"]

        data = {}
        data["text"] = ''.join(translation_texts)
        data["prompt_tokens"] = prompt_tokens
        data["completion_tokens"] = completion_tokens
        data["total_tokens"] = total_tokens
        return data


    def _split_with_end(self, t: str, end = "[。\.]") -> List[str]:
        ret = []
        endings = [iter.gtoup(1) for iter in re.finditer(end, t)]
        endings.insert(0, 0)
        cur = 0
        next = 1
        while next < len(endings):
            while estimate_token_num(t[endings[cur]:endings[next]], self.model) < self.max_token:
                next += 1
            if next == cur + 1:
                ret.extend(self._split_with_violence(t[endings[cur]:endings[next]]))
                cur = next
            else:
                ret.append(t[endings[cur]:endings[next - 1]])
                cur = next - 1
        ret.extend(self._split_with_violence(t[endings[cur]:]))
        return ret

    def _split_with_violence(self, t: str) -> List[str]:
        ret = []
        cur = next = 0
        while next < len(t):
            if estimate_token_num(t[cur:next], self.model) < self.max_token:
                next += 100
            else:
                ret.append(t[cur:next - 100])
                cur = next - 100
        ret.append(t[cur:])
        return ret

    def _split_text(self, text: str):
        # paragraphs
        initial_texts = text.split("\n")

        ret  = []
        for t in initial_texts:
            # 按句号切分
            if estimate_token_num(t, self.model) > self.max_token:
                ret.append(self._split_with_end(t))
            else:
                ret.append([t])
        
        return ret

    def _get_similar_local_context(self, chunk_text, para_contexts: List, para_context_embeddings: List) -> str:
        if len(para_contexts) == 0:
            return "None"
        
        if self.use_embedding == False:
            return para_contexts[-1]
            
        chunk_embedding = self._get_str_embedding(chunk_text)
        similarity = 0
        similar_index = -1
        for i in range(len(para_contexts)):
            new_sim = cosine_similarity(chunk_embedding, para_context_embeddings[i])
            if new_sim > similarity:
                similarity = new_sim
                similar_index = i
        return para_contexts[similar_index]

    def get_total_token_usage(self):
        return self.token_usage
    
    def infer_translation_style(self, modifications: List[Dict]) -> str:
        system_message = "You are a good reader who is sensitive to expressions, and a good translator. You are good at summarize the style of a text, as well as inferring the translation style \
            with the usage of vocabulary. You are going to check some modifications in vocabulary, then infer a corresponding translation style."
        system_message = "In the translation task, the user modified some texts, which are listed below. Please infer a translation style for them:\n"
        user_message = ""
        for i in range(modifications):
            user_t = modifications[i]["user_translation"] 
            original_s = modifications[i]["original_sentence"]
            model_t = modifications[i]["model_translation"]
            ith_modification = f"{i + 1}: The user used the word {user_t} to translate the original word {original_s} \
                instead of {model_t}.\n"
            user_message += ith_modification
        
        messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        response = self.client.chat.completions.create(messages=messages, model=self.model)
        return response.choices[0].message.content


    def _parse_answer(self, answer: str, *keys):
        try:
            pattern = "\{.*\}"
            data = json.loads(re.search(pattern, answer, re.S).group(0))
            return [data[key] for key in keys]
            return data['chunk_num'], data['text'], data["chunk_context"]
        except Exception as e:
            logging.getLogger("FileLogger").error(e)
            logging.getLogger("FileLogger").error("Error in parsing chunk translation! Returned answer:" + answer)

    def _parse_chunk_answer(self, answer: str):
        try:
            data = json.loads(answer)
            return data['chunk_num'], data['text'], data["chunk_context"]
        except Exception as e:
            logging.getLogger("FileLogger").error(e)
            logging.getLogger("FileLogger").error("Error in parsing chunk translation!")

    def _parse_paragraph_answer(self, answer: str):
        try:
            data = json.loads(answer)
            return data['PARA_CONTEXT'], data['GLOBAL_CONTEXT']
        except Exception as e:
            logging.getLogger("FileLogger").error(e)
            logging.getLogger("FileLogger").error("Error in parsing summarizing idea!")

    def _fill_format(self, data: list, to_fill: str, format="<INPUT \n>", split_token='\n'):
        pre, lat = format.split(split_token)
        for i in range(len(data)):
            to_fill = to_fill.replace(pre + str(i) + lat, data[i])
        return to_fill
    
    def _extract_preference(self, messages):
        ret = {
            "style": [],
            "user_dict": {}
        }
        for i in range(len(messages)):
            if messages[i]['role'] == 'style':
                ret['style'].append(messages[i]['content'])
            elif messages[i]['role'] == 'dict':
                contents = messages[i]['content'].split(':')
                key = contents[0].strip()
                value = contents[1].strip()
                ret['user_dict'][key] = value
        return ret

    def _extract_texts(self, messages):
        text = ""
        for i in range(len(messages)):
            if messages[i]['role'] == 'user':
                text += messages[i]['content']
        return text

    def _filter_user_dict(self, user_dict: dict, text):
        filtered_dict = {}
        for key, value in user_dict.items():
            if key in text:
                filtered_dict[key] = value
        return filtered_dict
    
    def _generate_llm_message(self, text, role='user'):
        return {
            'role': role,
            'content': text
        }

    @staticmethod
    def get_instance():
        if LLMClient.__instance is not None:
            return LLMClient.__instance
        else:
            raise Exception("LLM Client is not initialized")