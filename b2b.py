import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="B2B GST Ledger & Tracker", page_icon="📊", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- DATABASE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect("b2b_gst_ledger.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gst_records (
            serial_no TEXT PRIMARY KEY,
            sale_comp_name TEXT,
            purch_comp_name TEXT,
            sale_owner TEXT,
            purch_owner TEXT,
            service_items TEXT,
            hsn_code TEXT,
            total_amt REAL,
            paid_amt REAL,
            dues_amt REAL,
            hm_percent REAL,
            hm_amount REAL,
            bill_date TEXT,
            bill_time TEXT,
            ref_person TEXT,
            sale_ac_no TEXT,
            purch_ac_no TEXT,
            cash_entry TEXT,
            sale_mo TEXT,
            purch_mo TEXT,
            sale_gst TEXT,
            purch_gst TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_record(data):
    conn = sqlite3.connect("b2b_gst_ledger.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO gst_records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', data)
    conn.commit()
    conn.close()

def get_next_serial_no():
    conn = sqlite3.connect("b2b_gst_ledger.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gst_records")
    count = cursor.fetchone()[0]
    conn.close()
    return f"GST-26-{count + 1:04d}"

init_db()

# --- PDF GENERATOR (LANDSCAPE) ---
def generate_pdf_report(dataframe):
    pdf_buffer = BytesIO()
    html_table = dataframe.to_html(index=False, classes='report-table')
    
    pdf_html = f"""
    <html>
    <head>
    <style>
        @page {{ size: A4 landscape; margin: 10mm; }}
        body {{ font-family: Helvetica, sans-serif; font-size: 8px; color: #333333; }}
        h2 {{ text-align: center; color: #1f497d; }}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .report-table th {{ background-color: #1f497d; color: white; padding: 4px; border: 1px solid #dddddd; }}
        .report-table td {{ padding: 4px; border: 1px solid #dddddd; text-align: center; word-wrap: break-word; }}
    </style>
    </head>
    <body>
        <h2>B2B GST Ledger Report - {datetime.now().strftime('%d %b %Y')}</h2>
        {html_table}
    </body>
    </html>
    """
    pisa_status = pisa.CreatePDF(BytesIO(pdf_html.encode("utf-8")), dest=pdf_buffer)
    if pisa_status.err:
        return None
    return pdf_buffer.getvalue()

# --- UI LAYOUT ---
st.markdown("<h2 style='text-align: center; color: #1f497d;'>📊 B2B GST Application & Ledger</h2>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["📝 New Data Entry", "🔍 View, Filter & Export Database"])

with tab1:
    with st.container():
        st.markdown("<h5 style='color: #1f497d;'>🏢 Company Details</h5>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sale Company Info**")
            sale_comp_name = st.text_input("Sale Company Name *")
            sale_owner = st.text_input("Sale Owner Name")
            sale_gst = st.text_input("Sale Company GST No.")
            sale_ac_no = st.text_input("Sale Company A/C No.")
            sale_mo = st.text_input("Sale Owner Mobile No.")

        with col2:
            st.markdown("**Purchase Company Info**")
            purch_comp_name = st.text_input("Purchase Company Name *")
            purch_owner = st.text_input("Purchase Owner Name")
            purch_gst = st.text_input("Purchase Company GST No.")
            purch_ac_no = st.text_input("Purchase Company A/C No.")
            purch_mo = st.text_input("Purchase Company Mobile No.")

        st.markdown("<hr style='border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)

        st.markdown("<h5 style='color: #1f497d;'>💼 Transaction & Service Details</h5>", unsafe_allow_html=True)
        col3, col4, col5 = st.columns(3)
        
        with col3:
            service_items = st.text_area("Service Items *", height=120)
            hsn_code = st.text_input("HSN Code")
            ref_person = st.text_input("Ref Person")
            
        with col4:
            total_amt = st.number_input("Total Amount (Rs.) *", min_value=0.0, value=0.0)
            paid_amt = st.number_input("Amount Received/Paid (Rs.)", min_value=0.0, value=0.0)
            
            # --- AUTO CALCULATION LOGIC ---
            dues_amt = total_amt - paid_amt
            st.info(f"**Auto Dues Balance:** Rs. {dues_amt:.2f}")
            
            hm_percent = st.number_input("H/M Percentage (%)", min_value=0.0, value=0.0)
            hm_amount = (total_amt * hm_percent) / 100
            st.info(f"**Auto H/M Amount:** Rs. {hm_amount:.2f}")
            
        with col5:
            bill_date = st.date_input("Bill Date", value=datetime.today())
            bill_time = st.time_input("Time", value=datetime.now().time())
            cash_entry = st.selectbox("Cash Entry Level", ["Level 1", "Level 2", "Level 3", "Pending", "Cleared"])

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        save_btn = st.button("💾 Save Entry to Database", type="primary", use_container_width=True)

    if save_btn:
        if not sale_comp_name or not purch_comp_name or not service_items:
            st.error("⚠️ Sale Company, Purchase Company, and Service Items are mandatory.")
        else:
            serial_no = get_next_serial_no()
            str_date = bill_date.strftime("%d-%m-%Y")
            str_time = bill_time.strftime("%I:%M %p")
            
            db_data = (
                serial_no, sale_comp_name, purch_comp_name, sale_owner, purch_owner,
                service_items, hsn_code, total_amt, paid_amt, dues_amt, hm_percent, hm_amount,
                str_date, str_time, ref_person, sale_ac_no, purch_ac_no,
                cash_entry, sale_mo, purch_mo, sale_gst, purch_gst
            )
            save_record(db_data)
            st.success(f"✅ Data saved successfully! Serial No: {serial_no}")

with tab2:
    st.markdown("<h5 style='color: #1f497d;'>🔎 Smart Filter & Records</h5>", unsafe_allow_html=True)
    
    conn = sqlite3.connect("b2b_gst_ledger.db")
    df = pd.read_sql_query("SELECT * FROM gst_records", conn)
    conn.close()
    
    if not df.empty:
        # Search Filter
        search_query = st.text_input("🔍 Search by Company Name, GST No, or Ref Person...", "")
        
        if search_query:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            filtered_df = df[mask]
        else:
            filtered_df = df

        st.dataframe(filtered_df, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📥 Download Reports (Filtered Data)**")
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Download as Excel (CSV)",
                data=csv_data,
                file_name=f"GST_Ledger_{datetime.now().strftime('%d_%b_%Y')}.csv",
                mime='text/csv',
                use_container_width=True
            )
            
        with col_dl2:
            pdf_bytes = generate_pdf_report(filtered_df)
            if pdf_bytes:
                st.download_button(
                    label="📄 Download as PDF (Landscape)",
                    data=pdf_bytes,
                    file_name=f"GST_Ledger_{datetime.now().strftime('%d_%b_%Y')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.info("No records found in the database. Add new entries from the first tab.")
