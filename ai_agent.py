import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_openai_functions_agent, AgentExecutor

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList

#.env yuklash
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

MODEL_OPENAI = os.getenv("MODEL_OPENAI")
API_KEY_OPENAI = os.getenv("API_KEY_OPENAI")

SYSTEM_PROMPT = """
Siz — data analitiklarga yordam ko'rsatadigan sun'iy intellekt yordamchi botsiz.

VAZIFANGIZ:
Mijoz kiritgan savoli bo'yicha sql query yozish. Ma'lumotlar bazasi quyidagicha strukturaga ega:
clients (id, name, birth_date, region)
accounts (id, client_id, balance, open_date)
transactions (id, account_id, amount, date, type)

Qoidalar:
- Sana uchun: t.date >= DATE 'YYYY-MM-01' AND t.date < DATE 'YYYY-MM-01'
- Region uchun clients.region ishlatiladi.
- Region mapping (O‘zbekcha → DBdagi format):
'Toshkent' → 'Tashkent'
'Jizzax' → 'Jizzakh'
'Samarqand' → 'Samarkand'
'Andijon' → 'Andijan'
'Farg‘ona' → 'Fergana'
'Namangan' → 'Namangan'
'Buxoro' → 'Bukhara'
'Xorazm' → 'Khorezm'
'Qashqadaryo' → 'Qashqadarya'   -- agar DB’da bor bo‘lsa
'Surxondaryo' → 'Surxondaryo'
'Navoiy' → 'Navoi'
'Sirdaryo' → 'Sirdarya'          -- agar DB’da bor bo‘lsa
'Qoraqalpog‘iston' → 'Karakalpakstan'  -- agar DB’da bor bo‘lsa'

FORMAT:
- Agar savol DB bo‘yicha bo‘lsa → SQL query yozib 'assistant_excel' ga yubor.
- Oddiy savollarga javob ber.
- Agar DB bilan umuman aloqasi bo‘lmasa → "Bu savolingizni javobini bilmayman" de.
"""



# SQLAlchemy engine
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

#Excel + grafik
def save_with_chart(df: pd.DataFrame):
    filepath = Path(__file__).parent / "result.xlsx"
    filepath = filepath.as_posix()

    wb = Workbook()
    sheet = wb.active

    for r in dataframe_to_rows(df, index=False, header=True):
        sheet.append(r)

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        wb.save(filepath)
        return filepath

    first_num_col = df.columns.get_loc(numeric_cols[0]) + 1
    last_num_col = df.columns.get_loc(numeric_cols[-1]) + 1

    bar_chart = BarChart()
    bar_chart.varyColors = True
    data = Reference(sheet, min_row=1, max_row=sheet.max_row,
                     min_col=first_num_col, max_col=last_num_col)
    cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)

    bar_chart.add_data(data, titles_from_data=True)
    bar_chart.set_categories(cats)
    bar_chart.dataLabels = DataLabelList()
    bar_chart.dataLabels.showVal = True

    line_chart = LineChart()
    line_chart.add_data(data, titles_from_data=True)
    line_chart.set_categories(cats)

    bar_chart += line_chart
    last_col = sheet.max_column + 3
    sheet.add_chart(bar_chart, f"{get_column_letter(last_col)}2")

    wb.save(filepath)
    return filepath

@tool
def assistant_excel(prompt: str):
    """Postgres DB da SELECT query bajarib, natijani Excel + chart sifatida chiqaradi """
    engine = get_engine()
    df = pd.read_sql(prompt, engine)
    filename = save_with_chart(df)
    return {
        "reply": "Excel raeady",
        "_file": {
            "path": filename,
            "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "caption": "file"
        },
        "data": df.to_dict(orient="records"),
        "columns": list(df.columns)
    }

#LLM
llm = ChatOpenAI(model=MODEL_OPENAI, temperature=0, api_key=API_KEY_OPENAI)

#Tools
tools = [assistant_excel]

#Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Agent
agent = create_openai_functions_agent(llm, tools, prompt)

# AgentExecutor
rag_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)
