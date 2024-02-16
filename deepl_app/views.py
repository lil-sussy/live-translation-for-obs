from rest_framework.views import APIView
from rest_framework.response import Response
import requests

class DeepLTranslateView(APIView):
    def post(self, request, *args, **kwargs):
        # Your DeepL API key
        deepl_api_key = 'your_deepl_api_key'
        
        # DeepL API URL
        deepl_url = 'https://api-free.deepl.com/v2/translate'
        
        # Headers for DeepL API
        headers = {
            'Authorization': f'DeepL-Auth-Key {deepl_api_key}'
        }
        
        # Data to be sent to DeepL
        data = {
            'text': request.data.get('text'),
            'target_lang': request.data.get('target_lang')
        }
        
        # Make the request to DeepL
        response = requests.post(deepl_url, headers=headers, data=data)
        
        # Return the DeepL response
        return Response(response.json())
