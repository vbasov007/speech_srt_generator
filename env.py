import os

environ={
    'temp_file_folder': 'output',
    'temp_play_folder': os.path.join('static', 'temp'),
    'polly_key_id': os.environ.get('polly_key_id'),
    'polly_secret_key': os.environ.get('polly_secret_key'),
    'polly_region': os.environ.get('polly_region'),
    'translator_key': os.environ.get('translator_key'),
    'translator_url': os.environ.get('translator_url'),
    'ignore_translator_ssl_cert': os.environ.get('ignore_translator_ssl_cert', False),
}