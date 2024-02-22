from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from twitchlivetranslation.settings import DEEPL_API_KEY, IBM_API_KEY, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY

class DeepLTranslateView(APIView):
    def post(self, request, *args, **kwargs):
        # Return the DeepL response
        return Response(deepl_request(request.data['text'], request.data['target_lang']))



# def ibm_request(text, source_lang, target_lang):
#     url = 'https://api.au-syd.language-translator.watson.cloud.ibm.com/instances/7c38f7cc-1af1-4725-86cd-478107f8cdbd'
#     london = 'https://api.eu-gb.language-translator.watson.cloud.ibm.com'
#     authenticator = IAMAuthenticator(IBM_API_KEY)
#     language_translator = LanguageTranslatorV3(
#         version='2018-05-01',
#         authenticator=authenticator
#     )
    
#     language_translator.set_service_url('https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances/7c38f7cc-1af1-4725-86cd-478107f8cdbd')
    
#     # translate(
#     #         self,
#     #         text: List[str],
#     #         *,
#     #         model_id: str = None,
#     #         source: str = None,
#     #         target: str = None,
#     #         **kwargs,
#     #     ) -> DetailedResponse
#     translation = language_translator.translate(
#         text=[text],
#         model_id='fr-en', source=source_lang, target=target_lang).get_result()
#     print(translation)
# ibm_request('Bonjour, comment vas-tu aujourd\'hui?', 'fr-FR', 'en-US')


import boto3
def aws_request(text, source_lang, target_lang):
    if len(text) == 0:
        return ''
    translate = boto3.client(service_name='translate', region_name='eu-west-1', use_ssl=True, aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    result = translate.translate_text(Text=text, 
                SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)
    print('TranslatedText: ' + result.get('TranslatedText'))
    print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
    print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))


def deepl_request(text, target_lang):
    if len(text) == 0:
      return ''
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