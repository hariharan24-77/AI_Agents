import streamlit as st
import pandas as pd
import re
import json
 
from db import execute_query, refresh_schema, get_tables
from history import save_history
from styles import load_css
from agents import (
    intent_agent, 
    general_agent,
    get_query_agent,
    get_crud_agent,
    ddl_agent,
    view_agent,
    procedure_agent,
    function_agent,
    trigger_agent,
    index_agent,
    transaction_agent,
    validator_agent,
    debug_agent,
    explanation_agent,
    optimization_agent,
    security_agent
)

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="SQL Query Assistant",
    page_icon="database.png",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)
col1, col2 = st.columns([1,5])

with col1:
    st.image("database.png", width=80)

with col2:
    st.markdown("""
            <h1 style='
            color:#00E5FF;
            font-size:48px;
            font-weight:700;
            text-shadow:0 0 15px rgba(0,229,255,0.5);
            '>
            SQL Query Assistant
            </h1>
            """, unsafe_allow_html=True)
# ---------------------------
# SESSION STATE
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.title("📊 Database Tables")

tables = get_tables()
selected_table = st.sidebar.selectbox("Select Table", tables)

if st.sidebar.button("📋 View Table"):
    query = f"SELECT * FROM {selected_table} LIMIT 100"
    df, error = execute_query(query)

    if error:
        st.sidebar.error(error)
    else:
        st.sidebar.dataframe(df)

st.sidebar.title("🕘 Query History")

try:
    with open("chat_history.json", "r") as f:
        history = json.load(f)

    for item in reversed(history[-10:]):
        st.sidebar.write(item["user_query"])
        st.sidebar.write(item["timestamp"])
        st.sidebar.write("---")

except FileNotFoundError:
    st.sidebar.write("No history yet")

if st.sidebar.button("🗑 Clear History"):
    with open("chat_history.json", "w") as f:
        json.dump([], f)
    st.sidebar.success("History cleared")
    st.rerun()
 
# ---------------------------
# DISPLAY OLD MESSAGES
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------
# CHAT INPUT
# ---------------------------
question = st.chat_input("Ask Anything...")

# ---------------------------
# MAIN LOGI
# ---------------------------
if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            # STEP 1: INTENT
            intent = intent_agent.run(question)
            intent_text = intent.content.strip()
            intent_type = intent_text.split()[0].upper() if intent_text else "QUERY"
            st.write("Intent Type:", intent_type)
           
            # GENERAL
            if intent_type == "GENERAL":
                response = general_agent.run(question)
                final_response = response.content

                st.write(final_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_response
                })

                save_history(question, "GENERAL_QUERY", final_response)

            else:
                # STEP 2: ROUTER
                if intent_type == "QUERY":
                    agent = get_query_agent()
                elif intent_type == "CRUD":
                    agent = get_crud_agent()
                elif intent_type == "DDL":
                    agent = ddl_agent
                elif intent_type == "VIEW":
                    agent = view_agent
                elif intent_type == "PROCEDURE":
                    agent = procedure_agent
                elif intent_type == "FUNCTION":
                    agent = function_agent
                elif intent_type == "TRIGGER":
                    agent = trigger_agent
                elif intent_type == "INDEX":
                    agent = index_agent
                elif intent_type == "TRANSACTION":
                    agent = transaction_agent
                elif intent_type == "DEBUG":
                    agent = debug_agent
                elif intent_type == "OPTIMIZATION":
                    agent = optimization_agent
                else:
                    agent = get_query_agent()

                # STEP 3: SQL GENERATION
                response = agent.run(question)

                match = re.search(
                    r"```(?:sql)?(.*?)```",
                    response.content,
                    re.DOTALL
                )

                generated_sql = (
                    match.group(1).strip()
                    if match
                    else response.content.strip()
                )

                st.subheader("📝 Generated SQL")
                st.code(generated_sql, language="sql")

                # SECURITY
                security = security_agent.run(generated_sql)

                if "UNSAFE" in security.content.upper():
                    st.error("Unsafe SQL blocked")
                    st.stop()

                # VALIDATION
                validation = validator_agent.run(generated_sql)

                if "INVALID" in validation.content.upper():
                    st.error("Validation failed")
                    st.stop()

                # EXECUTE
                db_result, error = execute_query(generated_sql)

                if error:
                    st.error(error)
                    assistant_reply = error

                elif isinstance(db_result, pd.DataFrame):
                    st.dataframe(db_result, use_container_width=True)

                    assistant_reply = (
                        f"Returned {len(db_result)} rows"
                    )

                    save_history(
                        question,
                        generated_sql,
                        db_result.to_dict(orient="records")
                    )

                else:
                    st.success(db_result)
                    assistant_reply = db_result

                # OPTIMIZATION
                if intent_type in ["QUERY", "CRUD"]:
                    optimized = optimization_agent.run(generated_sql)

                    st.subheader("⚡ Optimization")
                    st.write(optimized.content)

                # DDL REFRESH
                if intent_type in ["DDL", "VIEW", "TRIGGER"]:
                    refresh_schema()

                # EXPLANATION
                explanation = explanation_agent.run(generated_sql)

                st.subheader("📖 Explanation")
                st.write(explanation.content)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply
                })