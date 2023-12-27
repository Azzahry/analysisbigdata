import google.generativeai as palm
import streamlit as st
palm.configure(api_key="AIzaSyAlptuKGaJcuANXUZD6xUR_-RujrA9Z2YY")

def initiate(user_input, model):
  return palm.chat(messages=user_input)

def reply(self, user_input):
  return self.reply(user_input)

models = [m for m in palm.list_models() if 'generateMessage' in m.supported_generation_methods]
model = models[0].name
print(model)


st.title("Question Answering")
prompt = st.text_input("Enter a message:")

if st.button('Generate'):
  response = initiate(
      user_input=prompt,
      model=model,
  )
  st.write(response.last)