import streamlit as st
from cerebras.cloud.sdk import Cerebras
import os
import json

# Set up the Cerebras API key
os.environ["CEREBRAS_API_KEY"] = ""

# Initialize the Cerebras client
client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

# System message
system_message = "You are a helpful chat assistant"

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]

if 'user_msgs_array' not in st.session_state:
    st.session_state.user_msgs_array = []

# Subcontext technique function
def subcontext(msg, num_user_msgs=30):
    st.session_state.conversation_history.append({"role": "user", "content": msg})
    st.session_state.user_msgs_array.append(msg)

    if len(st.session_state.conversation_history) < 3:
        return st.session_state.conversation_history

    user_msgs_string = []
    start = 1
    for x in range(len(st.session_state.user_msgs_array)):
        user_msgs_string.append(f"{start}. {st.session_state.user_msgs_array[x]}")
        start += 2

    user_msgs_string = "\n".join(user_msgs_string[:-1])

    subcontext_prompt = [{
        "role": "system",
        "content": (
            f"Below is a list of user messages and the current user query from a conversation with a chatbot. "
            f"Based on these, select the previous messages whose context is required for answering the current user query. "
            f"You can select multiple messages. Please return the result as a JSON object with two keys: "
            f"'reasoning' for the explanation and 'indices' for the list of indices. "
            f"Example: {{'reasoning': 'Explanation here', 'indices': [0, 3, 7]}}.\n\n"
            f"User Message List:\n{user_msgs_string}\n\nUser Query:\n{msg}"
        )
    }]

    result = chatgpt(subcontext_prompt, model="llama3.1-8b", response_format={"type": "json_object"})

    try:
        response_json = json.loads(result)
        list_obj = response_json.get("indices", [])
        if not isinstance(list_obj, list):
            raise ValueError("The response 'indices' is not a list.")
    except (ValueError, json.JSONDecodeError) as e:
        st.error(f"Error parsing response: {e}")
        return st.session_state.conversation_history

    subcontext_array = [st.session_state.conversation_history[0]]
    for y in list_obj:
        subcontext_array.append(st.session_state.conversation_history[y])
        subcontext_array.append(st.session_state.conversation_history[y + 1])

    subcontext_array.append(st.session_state.conversation_history[-1])

    if len(st.session_state.user_msgs_array) > num_user_msgs:
        trim_prompt = [{
            "role": "system",
            "content": (
                f"Given below a list of user msgs from a conversation with a chatbot. "
                f"We want to trim it so have a look at them, determine which ones are worth retaining based on what the conversation is progressing towards "
                f"and return only corresponding 'list of indices' (ex: [0,2,3]).\n\nUser Msg List:\n{user_msgs_string}"
            )
        }]
        trim_result = chatgpt(trim_prompt, model="llama3.1-8b", response_format={"type": "json_object"})
        try:
            trim_response_json = json.loads(trim_result)
            trim_list = trim_response_json.get("indices", [])
            if not isinstance(trim_list, list):
                raise ValueError("The trim response 'indices' is not a list.")
        except (ValueError, json.JSONDecodeError) as e:
            st.error(f"Error parsing trim response: {e}")
            return st.session_state.conversation_history

        new_list = []
        new_convo = [st.session_state.conversation_history[0]]
        for z in trim_list:
            new_list.append(st.session_state.user_msgs_array[z])
            new_convo.append(st.session_state.conversation_history[z])
            new_convo.append(st.session_state.conversation_history[z + 1])
        st.session_state.user_msgs_array = new_list
        st.session_state.conversation_history = new_convo

    return subcontext_array

# LLM call function
def chatgpt(messages_array, model="llama3.1-70b", response_format=None):
    response = client.chat.completions.create(
        model=model,
        messages=messages_array,
        temperature=0,
        max_completion_tokens=750,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=response_format
    )

    assistant_reply = response.choices[0].message.content
    return assistant_reply

# Streamlit app
st.title("UserSubContext Chatbot")

# Chat input widget
user_msg = st.chat_input("Enter your message:")

if user_msg:
    # Process the user message
    selected_context = subcontext(user_msg)
    reply = chatgpt(selected_context)

    # Update conversation history
    st.session_state.conversation_history.append({"role": "assistant", "content": reply})

# Display the entire conversation history
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(message["content"])

# Display selected context in an expander
if user_msg:
    with st.expander("Selected Context for This Turn"):
        for message in selected_context:
            if message["role"] == "user":
                st.write(f"User: {message['content']}")
            elif message["role"] == "assistant":
                st.write(f"Assistant: {message['content']}")

# ---                