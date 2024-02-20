from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from twitchlivetranslation.settings import DEEPL_API_KEY

class DeepLTranslateView(APIView):
    def post(self, request, *args, **kwargs):
        # Return the DeepL response
        return Response(deepl_request(request.data['text'], request.data['target_lang']))


def deepl_request(text, target_lang):
    # Your DeepL API key
    deepl_api_key = DEEPL_API_KEY
    
    # DeepL API URL
    deepl_url = 'https://api-free.deepl.com/v2/translate'
    
    # Headers for DeepL API
    headers = {
        'Authorization': f'DeepL-Auth-Key {deepl_api_key}',
        'DeepL-Auth-Key': f'{deepl_api_key}',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'access-control-allow,access-control-allow-credentials,access-control-allow-headers,access-control-allow-methods,authorization,control-allow-headers,cross-origin-resource-policy,deepl-auth-key,wildcard',
        'Access-Control-Allow-Methods': 'DELETE, POST, GET, OPTIONS',
        'Access-Control-Allow-Origin': 'https://enthusiastic-beds-production.up.railway.app',
        'Access-Control-Expose-Headers': 'Server-Timing',
        'wildcard': '*',
        'Cross-Origin-Resource-Policy': 'cross-origin',
        'Access-Control-Allow': '*',
        
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'content-length': str(len(text)),
        'Content-Type': 'application/json',
        'Referrer-Policy': 'no-referrer',
    }
    
    # Data to be sent to DeepL
    data = {
        'text': [text],
        'source_lang': 'FR',  # 'FR' for 'French
        'target_lang': target_lang,
        'split_sentences': '0',
        'preserve_formatting': False,
        'formality': 'prefer_less',
    }
    # referrerPolicy: 'no-referrer',
    # Make the request to DeepL
    response = requests.post(deepl_url, headers=headers, json=data).json()['translations'][0]['text']
    return response