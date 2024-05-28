if False:
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

class LLMClient():
    def __init__(self, client : LLM, model_name: str, max_token_per_message = 1024, inital_messages: List[Dict] = []):
        self.client = client
        self.model = model_name
        self.token_usage = 0
        self.max_token = max_token_per_message
        self.initial_messages = inital_messages
        self.answer_split_token = "#" * 20

        LLMClient.__instance = self

        logging.getLogger("StreamLogger").info("LLMClient initialied.")
        logging.getLogger("FileLogger").info("LLMClient initialied.")


    # 返回问题的答案
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6), retry=retry_if_exception_type(llm.APITimeoutError), reraise=True)
    def _get_answer(self, messages: List[Dict]) -> Optional[Dict]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        if response:
            ans = response.choices[0].message.content
            token = response["usage"]['total_tokens']
            self.token_usage += token
            return {"answer": ans, "token_usage": token}
    
    def translate(self, text: str, cur_language: str, target_language: str, style: str) -> Optional[str]:
        texts = self._split_translation_text(text)
        if len(self.initial_messages) == 0:
            with open("translation_template", 'r') as f:
                input_format = f.read()
            self.initial_messages = [
                {
                    "role": "system", "content": "You are a helpful translation assistant. You are going to translate some texts under some instructions.\
                 These instructions will stipulate the style and genre of your translation."
                },
                {
                    "role": "system", "content": "Each task will be input as the following format:" + input_format
                },
                {
                    "role": "system", "content": "You are going to translate the text segment from source language(CurrentLanguage segment) to target language(TargetLanguage segment) \
                        with style requirements in the Styles segment.\
                        You should also consider the context which is provided by the role assistant to make your translation more fluent and accurate."
                }
            ]
        
        messages = self.initial_messages
        context_idea = ""
        translation_texts = []
        for i in range(len(texts)):
            idea = {
                "role": "assistant",
                "content": context_idea
            }
            user = {
                    "role": "user",
                    "content": self._fill_format(texts[i], cur_language, target_language, style)
            }
            messages.append(idea)
            messages.append(user)
            response = self._get_answer(messages)
            token = response["usage"]
            self.token_usage += token
            translation_text, context_idea = self._split_answer(response["answer"])
            translation_texts.append(translation_text)
        
        return '\n'.join(translation_texts)

    def _split_translation_text(self, text: str) -> List[str]:
        # 先尝试分段符号
        initial_texts = text.split("\n  ")
        ret  = []
        for t in initial_texts:
            # 按句号切分
            if estimate_token_num(t, self.model) > self.max_token:
                ret.extend(self._split_with_end(t))
            else:
                ret.append(t)
        
        return ret
    
    def _split_with_end(self, t: str) -> List[str]:
        ret = []
        end = "[。\.]"
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


    def _split_answer(self, answer: str):
        ans = answer.split(self.answer_split_token)
        translation_text = ans[0].strip()
        idea = ans[1].strip()
        return translation_text, idea

    def _fill_format(self, text: str, cur_language: str, target_language: str, styles: str):
        with open("translation_template", 'r') as f:
            template = f.read()
        
        data = [cur_language, target_language, text, styles]
        for i in range(len(data)):
            template = template.replace(f"<INPUT {i}>", data[i])
        return template
    
    @staticmethod
    def get_instance():
        if LLMClient.__instance is not None:
            return LLMClient.__instance
        else:
            raise Exception("LLM Client is not initialized")