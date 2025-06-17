import streamlit as st

st.title("Simple Chat Input Test")

# Test different input methods
st.write("Testing st.chat_input:")
user_input1 = st.chat_input("Test chat input")
if user_input1:
    st.write(f"Chat input received: {user_input1}")

st.write("Testing st.text_input:")
user_input2 = st.text_input("Test text input", key="text_input")
if user_input2:
    st.write(f"Text input received: {user_input2}")

st.write("Testing manual form:")
with st.form("test_form"):
    user_input3 = st.text_input("Manual form input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input3:
        st.write(f"Form input received: {user_input3}")