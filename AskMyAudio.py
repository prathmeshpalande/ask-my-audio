import streamlit as st
from openai import OpenAI
client = OpenAI()
import os
import datetime
# Function to transcribe audio file
@st.cache_data
def transcribe_audio(audio_file):
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
        file=audio_file
    )
    print(transcription.text)
    return transcription.text

@st.cache_data
def call_chat_completions_api(model, message, response_format='text', system_message = None, messages=None, stream=False, temperature=0):
    if not messages:
        messages = []
        if system_message:
            messages.append(
                {'role': 'system', 'content': system_message}
            )
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        response_format={ "type": 'text' if response_format == 'text' else 'json_object' },
        temperature=temperature,
        stream=stream, # True,
        model=model, # "gpt-4-0125-preview",
        messages=messages # [
        #     {"role": "system", "content": "You are a web scraping expert in Python and Beautiful Soup that provides error-free code to the user"},
        #     {"role": "user", "content": ''}
        # ]
    )
    return response

@st.cache_data
def generate_file_name(uploaded_file_name):
    return f'{str(datetime.datetime.now()).replace(":", "-")}-{uploaded_file_name}'

@st.cache_data
def write_to_disk(file_path, open_type, _data):
    with open(file_path, open_type) as f:
            f.write(_data)

# Main Streamlit app
def main():
    st.title("Ask My Audio")

    # Upload audio file
    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"])
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        file_name = generate_file_name(uploaded_file.name)
        # file_name = f'{str(datetime.datetime.now()).replace(":", "-")}-{uploaded_file.name}'
        file_path = os.path.join("uploads", file_name)
        write_to_disk(file_path, "wb", uploaded_file.getbuffer())
        # Transcribe audio file
        transcript = transcribe_audio(uploaded_file)
        file_path = os.path.join("transcripts", file_name)
        write_to_disk(f'{file_path}.txt', "w", transcript)
        st.subheader("Transcript")
        transcript_editable = st.text_area("Editable Transcript", transcript)

        # Ask a question
        st.subheader("Ask a Question")
        question = st.text_area("Enter your question here")

        if st.button("Send"):
            # Process question and provide response
            message = f'''
                Context:
                Transcript of an audio file:
                `
                {transcript}
                `
                
                Prompt:
                `
                {question}
                `
            '''

            response = call_chat_completions_api(
                model='gpt-4-0125-preview',
                message=message,
                response_format='text'
                # messages=messages
            )
            # chunks = []
            # for chunk in response:
            #     content = chunk.choices[0].delta.content
            #     if content is not None:
            #         chunks.append(content)
            #         print(content, end="")
            #         # print(f'{chunk = }')
            #     else:
            #         print(f'\n\n{chunk.choices[0].finish_reason = }')


            # response = ''.join(chunks)
            st.subheader("Response")
            response = response.choices[0].message.content
            st.write(response)

            file_path = os.path.join("qa", file_name)
            write_to_disk(f'{file_path}-{hash(question)}.txt', "w", f'''
                {transcript = }

                {question = }

                {response = }
            ''')

if __name__ == "__main__":
    main()
