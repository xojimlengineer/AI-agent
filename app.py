import streamlit as st
import os
import pandas as pd
from ai_agent import rag_agent
st.title("Data Analyst Agent (Bank DB)")

query = st.text_input("Savolingizni yozing:")

if st.button("Javob"):
    if query.strip():
        result = rag_agent.invoke({
            "input": query,
            "chat_history": []
        })
        print("result:", result)

        #SQL preview
        st.subheader("Generated SQL")
        if "intermediate_steps" in result and result["intermediate_steps"]:
            try:
                sql_text = result["intermediate_steps"][0][0].tool_input
                st.code(sql_text, language="sql")
            except Exception as e:
                st.warning(f"SQL previewda muammo: {e}")

                # Agar output to‘g‘ridan tool natijasi bo‘lmasa, intermediate_steps ichidan chiqaramiz
                output = None
                if "output" in result and isinstance(result["output"], dict):
                    output = result["output"]
                elif "intermediate_steps" in result and result["intermediate_steps"]:
                    # oxirgi tool natijasini olamiz
                    try:
                        last_step = result["intermediate_steps"][-1][-1]
                        if isinstance(last_step, dict):
                            output = last_step
                    except Exception as e:
                        st.error(f"Natijani qayta ishlashda xato: {e}")

                # Excel faylni yuklab olish
                if "_file" in output:
                    file_path = output["_file"]["path"]
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="📥 Excelni yuklab olish",
                                data=f.read(),
                                file_name=os.path.basename(file_path),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.warning("⚠️ Excel fayl topilmadi.")
            else:
                st.warning("⚠️ Tool kutilgan formatda natija qaytarmadi.")

        # Default fallback: har doim oxirgi result.xlsx faylni berish
        if os.path.exists("result.xlsx"):
            with open("result.xlsx", "rb") as f:
                st.download_button(
                    label="📥 Excelni yuklab olish",
                    data=f.read(),
                    file_name="result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.error("Savol yozing.")

