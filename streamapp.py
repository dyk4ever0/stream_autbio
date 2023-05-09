import streamlit as st
import openai
import re
import requests
from PIL import Image
import sys

from googletrans import Translator
translator = Translator()

if "tags_list" not in st.session_state:
    st.session_state.tags_list = []

openai.api_key = ""
IMAGGA_API_KEY = "Basic YWNjXzBiMzgyNTRiNTk5YWI4NDo1OTZkNjdiZjcwYjE5ZmNkZjljMWMwYmJkMGRhZjA4Zg=="
IMAGGA_API_URL = "https://api.imagga.com/v2/tags"

def call_imagga_api(image):
    headers = {
        "accept": "application/json",
        "authorization": IMAGGA_API_KEY,  # Update this line
    }

    try:
        response = requests.post(
            IMAGGA_API_URL,
            headers=headers,
            files={"image": image},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error in Imagga API call: {e}")
        return []

    tags = response.json()["result"]["tags"]
    tags_list = [tag["tag"]["en"] for tag in tags][:10]
    #print(tags_list)
    return tags_list

def call_openai_api(tags_list, prompt):
    prompt = f"{prompt} The following are the top 10 tags that describe the photo: {', '.join(tags_list)}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    generated_text = response.choices[0].text
    return generated_text

def translate_to_korean(tags_list):
    korean_tags_list = [translator.translate(tag, dest="ko").text for tag in tags_list]
    return korean_tags_list


import sys


def get_tags_list():
    uploaded_file = st.file_uploader("업로드할 사진을 선택해 주세요", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.session_state.tags_list = call_imagga_api(uploaded_file.getvalue())

    if len(st.session_state.tags_list) > 0:
        st.write("자동 생성 태그:")

        korean_tags_list = translate_to_korean(st.session_state.tags_list)

        tags_to_remove = []
        for tag, korean_tag in zip(st.session_state.tags_list, korean_tags_list):
            col1, col2, col3 = st.columns(3)
            col1.write(f"{tag} ({korean_tag})")
            if col3.checkbox(f"- {tag}"):
                tags_to_remove.append(tag)

        if st.button("완료"):
            for tag in tags_to_remove:
                st.session_state.tags_list.remove(tag)
            st.markdown("### 최종 태그 리스트:")
            korean_final_tags_list = translate_to_korean(st.session_state.tags_list)
            st.write(", ".join(
                f"{tag} ({korean_tag})" for tag, korean_tag in zip(st.session_state.tags_list, korean_final_tags_list)))
            print("Removed tags:", tags_to_remove)
            print("Final tags list:", st.session_state.tags_list)

    tags_input = st.text_input('추가로 사용하실 태그를 컴마(,)로 구분하여 작성해 주세요')

    if tags_input:
        st.session_state.tags_list = [tag.strip() for tag in re.split(',', tags_input)]

    return st.session_state.tags_list



def get_prompt():
    prompt = st.text_input('Enter the prompt:')
    return prompt

def main():
    st.title("GPT 추모관 자동생성 데모")

    st.header("Step 1: 사진을 업로드합니다.")
    tags_list = get_tags_list()

    st.header("Step 2: Enter the prompt")
    prompt = get_prompt()

    if st.button("Generate Text"):
        if len(tags_list) > 0 and len(prompt) > 0:
            generated_text = call_openai_api(tags_list, prompt)
            st.header("Generated Text:")
            st.write(generated_text)
        else:
            st.error("Please provide both tags and a prompt.")

if __name__ == "__main__":
    main()
