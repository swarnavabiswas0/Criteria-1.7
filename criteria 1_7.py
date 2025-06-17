import streamlit as st
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Programme Upload Form", layout="wide")

UPLOAD_DIR = "uploaded_files"
SUMMARY_FILE = "submissions_summary.xlsx"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file, prefix, label):
    if file is not None:
        filename = f"{prefix}_{label}_{file.name}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        return filename
    return None

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
                excel_name = save_file(excel, prefix, "Excel")
                doc_names = [
                    save_file(docs[0], prefix, "2022-2023"),
                    save_file(docs[1], prefix, "2023-2024"),
                    save_file(docs[2], prefix, "2024-2025"),
                ]
                log_submission(timestamp, department, pname, excel_name, doc_names)
            else:
                st.warning(f"⚠️ Incomplete data for Programme {i}. Skipping.")

        st.success("✅ All complete programmes submitted and logged successfully!")
        st.balloons()
