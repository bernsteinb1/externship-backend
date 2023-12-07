from boto3 import Session  # Amazon's Python SDK
import os
import tempfile
from tempfile import gettempdir
from contextlib import closing
from botocore.exceptions import NoCredentialsError

'''
Helper functions for get_tts_s3()
'''
# key is the text from the card (front or back) to be converted to audio
def check_dynamodb_key(table, key):
    dynamodb = Session().client('dynamodb')
    table = dynamodb.Table(table)
    
    response = table.get_item(
        Key={'cardText': {
            'S': key
            }
        }
    )

    return 'Item' in response

def upload_s3_audio(text, s3_bucket):
    polly = Session().client('polly')
    s3 = Session().client('s3')
    
    response = polly.start_speech_synthesis_task(
        OutputFormat='mp3',
        Text=text,
        VoiceId='Joanna'
    )
    
    task_id = response['SynthesisTask']['TaskId']
    
    # Wait for the task to complete
    waiter = polly.get_waiter('speech_synthesis_task_completed')
    waiter.wait(TaskId=task_id)
    
    # Get the URL of the generated audio file
    audio_url = polly.get_speech_synthesis_task(TaskId=task_id)['SynthesisTask']['OutputUri']
    
    # Download the audio file to a temporary local file
    _, local_audio_path = tempfile.mkstemp(suffix=".mp3")
    s3.download_file(s3_bucket, audio_url.split('/')[-1], local_audio_path)
    
    return local_audio_path

def upload_to_s3(s3_bucket, local_file_path, s3_key):
    s3 = Session().client('s3')
    
    try:
        s3.upload_file(local_file_path, s3_bucket, s3_key)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    
def update_dynamodb(table, key, s3_key):
    dynamodb = Session().client('dynamodb')
    table = dynamodb.Table(table)
    
    table.put_item(
        Item={
            'cardText': key,
            's3_key': s3_key
        }
    )

'''
End of helper functions
'''

def get_tts_s3(text):
    table = 'TTS_Audio'
    s3_bucket = 'externship23-audiobucket'

    key = text

    if check_dynamodb_key(table, key):
        # Key exists, fetch the corresponding S3 audio file
        response = Session().client('dynamodb').get_item(
            TableName=table,
            Key={'cardText': {
                'S': key
                }
            }
        )
        s3_key = response['Item']['s3_key']['S']
    else:
        # Key does not exist, generate and upload S3 audio file
        local_audio_path = upload_s3_audio(key, s3_bucket)
        s3_key = f"{key}.mp3"
        upload_to_s3(s3_bucket, local_audio_path, s3_key)
        update_dynamodb(table, key, s3_key)

    print(f"S3 audio file key: {s3_key}")
    return s3_key

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