import streamlit as st
import os
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json

st.set_page_config(page_title="Programme Upload Form", layout="wide")

SUMMARY_FILE = "submissions_summary.xlsx"
DRIVE_FOLDER_ID = "1070AoxMzYtgClEakB7ydyRskBgil06qn"

# Authenticate with Google Drive API using st.secrets
service_account_info = json.loads(st.secrets["gdrive_credentials"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

def upload_to_drive(file, filename):
    if file is not None:
        file_data = io.BytesIO(file.getbuffer())
        media = MediaIoBaseUpload(file_data, mimetype=file.type)
        file_metadata = {
            "name": filename,
            "parents": [DRIVE_FOLDER_ID]
        }
        uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return filename
    return None

def upload_summary_to_drive():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, "rb") as f:
            file_data = io.BytesIO(f.read())
        media = MediaIoBaseUpload(file_data, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        file_metadata = {
            "name": f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "parents": [DRIVE_FOLDER_ID]
        }
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

def log_submission(timestamp, department, pname, excel_name, doc_names):
    row = {
        "Timestamp": timestamp,
        "Department": department,
        "Programme": pname,
        "Excel File": excel_name,
        "AY 2022-2023": doc_names[0],
        "AY 2023-2024": doc_names[1],
        "AY 2024-2025": doc_names[2],
    }

    if os.path.exists(SUMMARY_FILE):
        df = pd.read_excel(SUMMARY_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(SUMMARY_FILE, index=False)

st.title("📂 Multi-Programme Document Upload Portal")
st.write("Please fill out the form below and upload required documents.")

# 1. Department Name
department = st.text_input("1. Name of the Department")

# Function to create file upload blocks for each programme
def programme_section(programme_num):
    st.markdown(f"### Programme {programme_num}")
    pname = st.text_input(f"{programme_num*3 - 1}. Name of the Programme-{programme_num}")
    excel = st.file_uploader(f"{programme_num*3}. Upload 1.7 Excel for P-{programme_num}", type=["xls", "xlsx"])

    col1, col2, col3 = st.columns(3)
    with col1:
        doc1 = st.file_uploader(f"Upload 2022-2023 AY Supporting Documents for P-{programme_num}", type=["pdf", "doc", "docx"], key=f"p{programme_num}_doc1")
    with col2:
        doc2 = st.file_uploader(f"Upload 2023-2024 AY Supporting Documents for P-{programme_num}", type=["pdf", "doc", "docx"], key=f"p{programme_num}_doc2")
    with col3:
        doc3 = st.file_uploader(f"Upload 2024-2025 AY Supporting Documents for P-{programme_num}", type=["pdf", "doc", "docx"], key=f"p{programme_num}_doc3")

    return pname, excel, [doc1, doc2, doc3]

# Programme sections
p1_data = programme_section(1)
p2_data = programme_section(2)
p3_data = programme_section(3)
p4_data = programme_section(4)

# Submit button
if st.button("Submit All"):
    if not department:
        st.error("Please enter the Department Name.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i, (pname, excel, docs) in enumerate([p1_data, p2_data, p3_data, p4_data], start=1):
            if pname and excel and all(docs):
                prefix = f"P{i}_{pname.replace(' ', '_')}_{department.replace(' ', '_')}"
                excel_name = upload_to_drive(excel, f"{prefix}_Excel_{excel.name}")
                doc_names = [
                    upload_to_drive(docs[0], f"{prefix}_2022-2023_{docs[0].name}"),
                    upload_to_drive(docs[1], f"{prefix}_2023-2024_{docs[1].name}"),
                    upload_to_drive(docs[2], f"{prefix}_2024-2025_{docs[2].name}"),
                ]
                log_submission(timestamp, department, pname, excel_name, doc_names)
            else:
                st.warning(f"⚠️ Incomplete data for Programme {i}. Skipping.")

        upload_summary_to_drive()
        st.success("✅ All complete programmes submitted, uploaded to Drive, and logged successfully!")
        st.balloons()

# Manual download of the summary Excel file if it exists
if os.path.exists(SUMMARY_FILE):
    with open(SUMMARY_FILE, "rb") as f:
        st.download_button(
            label="📥 Download Latest Summary Excel",
            data=f,
            file_name="submissions_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )