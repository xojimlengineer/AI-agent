import os
import streamlit as st
from langchain_core.messages import HumanMessage
from ai_agent import rag_agent

st.set_page_config(page_title="Bank DB Analyst", page_icon="📊", layout="wide")
st.title("Data Analyst Agent (Bank DB)")

q = st.text_input("Savolingizni yozing:")
go = st.button("Javob")

def run_agent(prompt: str):
    return rag_agent.invoke({"messages": [HumanMessage(content=prompt)]})

if go:
    if not q.strip():
        st.error("Savol kiriting.")
    else:
        with st.spinner("Hisoblayapman..."):
            try:
                result = run_agent(q.strip())
            except Exception as e:
                st.error(f"Xatolik: {e}")
                st.stop()

        file_given = False
        outbox = result.get("outbox") or []
        for item in outbox:
            path = item.get("path")
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(
                        "📥 Excelni yuklab olish",
                        data=f.read(),
                        file_name=os.path.basename(path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                file_given = True
                break

        if not file_given and os.path.exists("result.xlsx"):
            with open("result.xlsx", "rb") as f:
                st.download_button(
                    "📥 Excelni yuklab olish",
                    data=f.read(),
                    file_name="result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )