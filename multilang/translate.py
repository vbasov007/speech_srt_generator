import requests


class Translation:

    def __init__(self, url, api_key, verify=True):
        self.api_key = api_key
        self.base_url = url
        self._verify = verify

    def translate_text(self, text, target_lang, source_lang=None):
        params = {
            'auth_key': self.api_key,
            'text': text,
            'target_lang': target_lang,
            'source_lang': source_lang,
            'tag_handling': 'xml'
        }
        # response = requests.post(self.base_url, data=params,
        #                          headers={'Content-Type': 'application/json',
        #                                   'Authorization': 'DeepL-Auth-Key ' + self.api_key})

        # headers = {'accept':'application/json','Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.base_url, data=params, verify=self._verify)
        if response.status_code == 200:
            translation = response.json()['translations'][0]['text']
            return translation
        else:
            raise Exception('Translation request failed with status code: ' + str(response.status_code))
