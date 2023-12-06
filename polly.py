from boto3 import Session # Amazon's Python SDK
import os
from tempfile import gettempdir
from contextlib import closing


def get_tts(text):
    session = Session()
    polly = session.client('polly')
    try:
        response = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
        with closing(response['AudioStream']) as stream:
            output = os.path.join(gettempdir())
            with open(f'{text}.mp3', "wb") as file:
                file.write(stream.read())
    except:
        print('Something went wrong.')
    return f'{text}.mp3'
