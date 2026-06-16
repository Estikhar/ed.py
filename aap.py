import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import textwrap
from io import BytesIO
from xhtml2pdf import pisa

# Page Configuration
st.set_page_config(page_title="Hotel Royale Paradise Billing", page_icon="🏨", layout="centered")

# --- DATABASE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect("royal_paradise_hotel.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            bill_no TEXT PRIMARY KEY,
            bill_date TEXT,
            customer_name TEXT,
            customer_gstin TEXT,
            room_no TEXT,
            no_of_person INTEGER,
            check_in TEXT,
            check_out TEXT,
            days INTEGER,
            rate REAL,
            total_taxable REAL,
            cgst REAL,
            sgst REAL,
            grand_total REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_invoice(data):
    conn = sqlite3.connect("royal_paradise_hotel.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO invoices VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', data)
    conn.commit()
    conn.close()

def get_next_bill_no():
    conn = sqlite3.connect("royal_paradise_hotel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]
    conn.close()
    return f"23{count + 1:02d}"

init_db()

# --- PDF GENERATOR HELPER ---
def generate_pdf(html_content):
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html_content.encode("utf-8")), dest=pdf_buffer)
    if pisa_status.err:
        return None
    return pdf_buffer.getvalue()

# --- APP INTERFACE ---
st.title("🏨 Hotel Royale Paradise")
st.subheader("Cloud-Based GST Billing Engine")

tab1, tab2 = st.tabs(["🆕 New Invoice", "📊 GST Reports & History"])

with tab1:
    st.info("Fill guest details below to generate a print-ready PDF invoice.")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Guest Name *")
        customer_gstin = st.text_input("Guest GSTIN (Optional)")
        room_no = st.text_input("Room No. *")
    with col2:
        no_of_person = st.number_input("No. Of Persons", min_value=1, value=1)
        check_in = st.text_input("From (Date & Time)", value=datetime.now().strftime("%d-%m-%Y 12:00 PM"))
        check_out = st.text_input("To (Date & Time)", value=datetime.now().strftime("%d-%m-%Y 11:00 AM"))

    col3, col4 = st.columns(2)
    with col3:
        rate = st.number_input("Lodging Charges per Day (₹) *", min_value=0.0, value=2000.0)
    with col4:
        days = st.number_input("Total Days *", min_value=1, value=1)

    total_taxable = rate * days
    cgst = total_taxable * 0.025
    sgst = total_taxable * 0.025
    grand_total = total_taxable + cgst + sgst

    if st.button("Generate Bill"):
        if not customer_name or not room_no:
            st.error("Please fill required fields (Guest Name & Room No.)")
        else:
            bill_no = get_next_bill_no()
            bill_date = datetime.now().strftime("%d-%m-%Y")
            
            db_data = (bill_no, bill_date, customer_name, customer_gstin, room_no, 
                       no_of_person, check_in, check_out, days, rate, total_taxable, cgst, sgst, grand_total)
            save_invoice(db_data)
            
            st.success(f"Invoice {bill_no} successfully stored in database! Click below to download PDF.")

            raw_html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12px; color: #333; }}
                .container {{ padding: 20px; border: 2px solid #d6336c; background-color: #fff0f5; }}
                .header-table {{ width: 100%; font-size: 10px; margin-bottom: 10px; }}
                .title-section {{ text-align: center; margin-bottom: 15px; }}
                .main-title {{ color: #d6336c; font-size: 24px; font-weight: bold; font-style: italic; margin: 5px 0; }}
                .info-table {{ width: 100%; margin-bottom: 15px; border: none; }}
                .item-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                .item-table th {{ background-color: #d6336c; color: white; padding: 6px; border: 1px solid #d6336c; text-align: left; }}
                .item-table td {{ padding: 6px; border: 1px solid #d6336c; }}
                .text-right {{ text-align: right; }}
                .text-center {{ text-align: center; }}
            </style>
            </head>
            <body>
            <div class="container">
                <table class="header-table">
                    <tr>
                        <td><strong>CIN :</strong> U54132UP1999PTC024452</td>
                        <td class="text-right"><strong>GSTIN :</strong> 09AADCA6394B2ZP</td>
                    </tr>
                </table>
                
                <div class="title-section">
                    <div style="font-size: 14px; font-weight: bold; text-decoration: underline; letter-spacing: 2px;">BILL</div>
                    <div class="main-title">Hotel Royale Paradise</div>
                    <div style="font-size: 10px; font-weight: bold;">(A Unit of Akhand Enterprises (P) Ltd.)</div>
                    <div style="font-size: 9px;">Regd. Off. : Kishori Kunj, 105-B, Gaushala Road, New Mandi, Muzaffarnagar (U.P.)</div>
                    <div style="font-size: 10px; font-weight: bold; background-color: #f8d7e3; padding: 3px; margin-top: 4px;">
                        Y-349 C, Sector-12, NOIDA-201301 (U.P.) Ph. : 91-120-2536460, 2533391, 9818675476
                    </div>
                </div>
                <hr color="#d6336c" size="1">
                
                <table class="info-table">
                    <tr>
                        <td width="55%" valign="top">
                            <strong>GUEST DETAILS:</strong><br>
                            Name: {customer_name}<br>
                            GSTIN: {customer_gstin if customer_gstin else 'N/A'}
                        </td>
                        <td width="45%" valign="top">
                            <strong>BILL NO. : {bill_no}</strong><br>
                            BILL DATE : {bill_date}<br>
                            ROOM NO. : {room_no}<br>
                            NO. OF PERSON : {no_of_person}
                        </td>
                    </tr>
                </table>

                <table class="item-table">
                    <tr>
                        <th width="60%">PARTICULARS</th>
                        <th width="20%" class="text-center">RATE (₹)</th>
                        <th width="20%" class="text-right">AMOUNT (₹)</th>
                    </tr>
                    <tr>
                        <td valign="top" height="100">
                            <strong>Lodging Charges for {days} days</strong><br>
                            <span style="font-size: 10px; color: #555;">From: {check_in}<br>To: {check_out}</span>
                        </td>
                        <td valign="top" class="text-center">{rate:.2f}</td>
                        <td valign="top" class="text-right">{total_taxable:.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="2" class="text-right"><strong>TOTAL</strong></td>
                        <td class="text-right"><strong>{total_taxable:.2f}</strong></td>
                    </tr>
                    <tr>
                        <td colspan="2" class="text-right">CGST (2.5%)</td>
                        <td class="text-right">{cgst:.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="2" class="text-right">SGST (2.5%)</td>
                        <td class="text-right">{sgst:.2f}</td>
                    </tr>
                    <tr style="background-color: #f8d7e3;">
                        <td colspan="2" class="text-right" style="font-weight: bold; font-size: 13px;">GRAND TOTAL</td>
                        <td class="text-right" style="font-weight: bold; font-size: 13px; color: #d6336c;">₹ {grand_total:.2f}</td>
                    </tr>
                </table>

                <div style="font-size: 10px; margin-top: 20px;">
                    <strong>TERMS & CONDITIONS :</strong><br>
                    1. Check out Time 12:00 Noon<br>
                    2. Subject to Muzaffarnagar Jurisdiction Only<br>
                    E. & O.E.
                </div>

                <table width="100%" style="margin-top: 40px;">
                    <tr>
                        <td width="50%" valign="bottom">Guest Signature</td>
                        <td width="50%" class="text-right">
                            For <strong>Hotel Royale Paradise</strong><br><br><br>
                            Auth. Signatory
                        </td>
                    </tr>
                </table>
            </div>
            </body>
            </html>
            """
            
            clean_html = textwrap.dedent(raw_html)
            
            # Print to screen for preview
            st.markdown(clean_html, unsafe_allow_html=True)
            
            # Generate PDF and show Download Button
            pdf_bytes = generate_pdf(clean_html)
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF Bill",
                    data=pdf_bytes,
                    file_name=f"Hotel_Royal_Paradise_Invoice_{bill_no}.pdf",
                    mime="application/pdf"
                )

with tab2:
    st.subheader("Database History")
    conn = sqlite3.connect("royal_paradise_hotel.db")
    df = pd.read_sql_query("SELECT * FROM invoices", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Monthly GST Ledger for CA (Excel/CSV)",
            data=csv,
            file_name=f"GST_Report_{datetime.now().strftime('%m_%Y')}.csv",
            mime='text/csv',
        )
    else:
        st.warning("No invoices generated yet.")
