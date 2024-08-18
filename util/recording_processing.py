import whisper
import re
import ast
from openai import OpenAI
from util.speaker_ID import *



model = whisper.load_model('base')
agent = OpenAI(base_url = base_url, api_key = api_key)


def processing_recording(filepath, callback = None):
    
    sys_prompt = """ For the following sentences, identify the activity being described and any relevant details associated with the activity. Output your response in JSON format as {'activity': '<activity>', 'details': '<details>'}. If there are no details, leave the details field empty. Examples:
1. "I jsut finished a 5-mile run." Response: {'activity': 'finish run', 'details': '5 miles'}
2. "Had breakfast with scrambled eggs and toast." Response: {'activity': 'have breakfast', 'details': 'scrambled eggs and toast'}
3. "Completed a 30-minute yoga session in the living room." Response: {'activity': 'complete yoga session', 'details': '30 minutes in the living room'}
4. "Start working." Response: {'activity': start work, 'details':}
Now given the following sentence: 
"""
    user_promt = model.transcribe(filepath, language = "en")['text']
    speaker = who_is_the_speaker(filepath, sample_files)
    date = datetime.datetime.now().date().strftime("%m/%d/%Y")
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    
    chat = agent.chat.completions.create(messages=[
    {
        "role": "system",
        "content": sys_prompt
    },
    {
        "role": "user",
        "content": user_promt
    }],
    model = model_name,
    temperature = 0,
    max_tokens = 50
    )
    
    chat_content = chat.choices[0].message.content

    # Try to find and evaluate the dictionary-like structure
    try:
        dic_match = re.search(r"\{.*?\}", chat_content)
        
        if dic_match:
            dic = ast.literal_eval(dic_match.group(0))
        else:
            dic = {'activity': 'error', 'details': 'error'}  # No match found
    except (ValueError, SyntaxError):
        dic = {'activity': 'error', 'details': 'error'}
    
    result = {'speaker': speaker, 'date': date, 'time': time, 'activity': dic["activity"], 'details': dic["details"], 'transcript': user_promt}
    
    if callback:
        callback(result)
    
    return(result)