import polly_config
import boto3 # Amazon's Python SDK

aws_access_key_id = polly_config.aws_access_key_id
aws_secret_access_key = polly_config.aws_secret_access_key
aws_region = polly_config.aws_region

'''
In your local repo, create a polly_config.py file. Write the following and put in your own keys and region.

aws_access_key_id = 'YOUR_ACCESS_KEY'
aws_secret_access_key = 'YOUR_SECRET_KEY'
aws_region = 'YOUR_AWS_REGION'
'''

try:
    # Configure Boto3
    polly = boto3.client('polly', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

    # Specify text and voice
    # In the context of our web app, the front end should include the text to convert to audio in its API request
    text = 'Hello world! This is a test of Amazon\'s Polly Text-to-Speech API!'
    voice_id = 'Joanna'

    # Invoke Amazon Polly API
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id
    )

    # Save the audio to a file 'output.mp3'
    with open('output.mp3', 'wb') as audio_file:
        audio_file.write(response['AudioStream'].read())

except boto3.exceptions.Boto3Error as e:
    # Handle general Boto3 errors
    print(f"Boto3 error: {e}")

except polly.exceptions.PollyError as e:
    # Handle specific Polly errors
    print(f"Amazon Polly error: {e}")

except Exception as e:
    # Handle other unexpected errors
    print(f"Unexpected error: {e}")

else:
    # Code to execute if there are no errors
    print("Text-to-speech conversion successful!")