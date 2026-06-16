import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
import streamlit.components.v1 as components

# --- PAGE CONFIGURATION (Professional Look) ---
st.set_page_config(page_title="Hotel Royale Paradise | Billing System", page_icon="🏨", layout="wide")

# Hide Streamlit Branding for a White-Label SaaS look
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

# --- PDF GENERATOR ---
def generate_pdf(html_content):
    pdf_buffer = BytesIO()
    pdf_html = f"""
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: Helvetica, sans-serif; font-size: 11px; color: #1a1a1a; }}
        .header-table {{ width: 100%; border-bottom: 2px solid #d6336c; padding-bottom: 10px; margin-bottom: 15px; }}
        .rp-logo {{ background-color: #d6336c; color: #ffffff; padding: 12px 8px; border: 2px solid #9c1c49; text-align: center; width: 65px; }}
        .main-title {{ color: #d6336c; font-size: 26px; font-weight: bold; font-style: italic; margin: 4px 0; font-family: serif; }}
        .item-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .item-table th {{ background-color: #d6336c; color: white; padding: 8px; border: 1px solid #d6336c; text-align: left; font-size: 10px; }}
        .item-table td {{ padding: 8px; border: 1px solid #d6336c; }}
        .text-right {{ text-align: right; }}
        .text-center {{ text-align: center; }}
    </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    pisa_status = pisa.CreatePDF(BytesIO(pdf_html.encode("utf-8")), dest=pdf_buffer)
    if pisa_status.err:
        return None
    return pdf_buffer.getvalue()

# --- UI LAYOUT ---
st.markdown("<h2 style='text-align: center; color: #d6336c;'>🏨 Hotel Royale Paradise Dashboard</h2>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🧾 Generate New Invoice", "📊 GST & Data Management"])

with tab1:
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            customer_name = st.text_input("Guest Name *", placeholder="e.g. Rahul Verma")
            room_no = st.text_input("Room No. *", placeholder="e.g. 101")
        with col2:
            customer_gstin = st.text_input("Guest GSTIN (Optional)", placeholder="For B2B Billing")
            no_of_person = st.number_input("No. Of Persons", min_value=1, value=1)
        with col3:
            check_in = st.text_input("Check-In (Date & Time)", value=datetime.now().strftime("%d-%m-%Y 12:00 PM"))
            rate = st.number_input("Room Rate per Day (Rs.) *", min_value=0.0, value=2000.0)
        with col4:
            check_out = st.text_input("Check-Out (Date & Time)", value=datetime.now().strftime("%d-%m-%Y 11:00 AM"))
            days = st.number_input("Total Days *", min_value=1, value=1)

    st.markdown("<br>", unsafe_allow_html=True)
    
    total_taxable = rate * days
    cgst = total_taxable * 0.025
    sgst = total_taxable * 0.025
    grand_total = total_taxable + cgst + sgst

    # Centered Generate Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_btn = st.button("🚀 Generate Professional Invoice", type="primary", use_container_width=True)

    if generate_btn:
        if not customer_name or not room_no:
            st.error("⚠️ Guest Name and Room Number are mandatory.")
        else:
            bill_no = get_next_bill_no()
            bill_date = datetime.now().strftime("%d-%m-%Y")
            
            db_data = (bill_no, bill_date, customer_name, customer_gstin, room_no, 
                       no_of_person, check_in, check_out, days, rate, total_taxable, cgst, sgst, grand_total)
            save_invoice(db_data)
            
            st.success(f"✅ Invoice {bill_no} stored safely. Ready for print!")

            # --- THE INVOICE TEMPLATE (With CSS Recreated Logo) ---
            core_html = f"""
            <table class="header-table">
                <tr>
                    <td style="width: 15%; vertical-align: middle;">
                        <div class="rp-logo">
                            <div style="font-family: serif; font-size: 28px; font-weight: bold; line-height: 1;">Rp</div>
                            <div style="font-size: 7px; margin-top: 4px; letter-spacing: 0.5px;">ROYALE<br>PARADISE</div>
                        </div>
                    </td>
                    <td style="width: 70%; text-align: center;">
                        <div style="font-size: 14px; font-weight: bold; letter-spacing: 2px;"><u>BILL</u></div>
                        <div class="main-title">Hotel Royale Paradise</div>
                        <div style="font-size: 10px; font-weight: bold;">(A Unit of Akhand Enterprises (P) Ltd.)</div>
                        <div style="font-size: 9px; color: #444;">Regd. Off. : Kishori Kunj, 105-B, Gaushala Road, New Mandi, Muzaffarnagar (U.P.)</div>
                        <div style="font-size: 10px; font-weight: bold; background-color: #fcebf0; padding: 4px; margin-top: 5px;">
                            Y-349 C, Sector-12, NOIDA-201301 (U.P.) Ph. : 91-120-2536460, 2533391, 9818675476
                        </div>
                    </td>
                    <td style="width: 15%; text-align: right; vertical-align: top; font-size: 9px; line-height: 1.5;">
                        <strong>CIN:</strong><br>U54132UP1999PTC024452<br><br>
                        <strong>GSTIN:</strong><br>09AADCA6394B2ZP
                    </td>
                </tr>
            </table>
            
            <table style="width: 100%; border: none; margin-bottom: 15px; font-size: 11px;">
                <tr>
                    <td style="width: 55%; vertical-align: top; line-height: 1.6;">
                        <strong>GUEST DETAILS:</strong><br>
                        Name: <strong>{customer_name}</strong><br>
                        GSTIN: {customer_gstin if customer_gstin else 'N/A'}
                    </td>
                    <td style="width: 45%; vertical-align: top; line-height: 1.6;">
                        <strong>BILL NO. : <span style="color: #d6336c;">{bill_no}</span></strong><br>
                        BILL DATE : {bill_date}<br>
                        ROOM NO. : {room_no}<br>
                        NO. OF PERSON : {no_of_person}
                    </td>
                </tr>
            </table>

            <table class="item-table">
                <tr>
                    <th style="width: 60%;">PARTICULARS</th>
                    <th style="width: 20%;" class="text-center">RATE (Rs.)</th>
                    <th style="width: 20%;" class="text-right">AMOUNT (Rs.)</th>
                </tr>
                <tr>
                    <td style="vertical-align: top; height: 120px;">
                        <strong>Lodging Charges for {days} days</strong><br>
                        <span style="font-size: 10px; color: #555;">From: {check_in}<br>To: {check_out}</span>
                    </td>
                    <td style="vertical-align: top;" class="text-center">{rate:.2f}</td>
                    <td style="vertical-align: top;" class="text-right">{total_taxable:.2f}</td>
                </tr>
                <tr>
                    <td colspan="2" class="text-right"><strong>TOTAL TAXABLE VALUE</strong></td>
                    <td class="text-right"><strong>{total_taxable:.2f}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" class="text-right" style="color: #555;">CGST (2.5%)</td>
                    <td class="text-right" style="color: #555;">{cgst:.2f}</td>
                </tr>
                <tr>
                    <td colspan="2" class="text-right" style="color: #555;">SGST (2.5%)</td>
                    <td class="text-right" style="color: #555;">{sgst:.2f}</td>
                </tr>
                <tr style="background-color: #fcebf0;">
                    <td colspan="2" class="text-right" style="font-weight: bold; font-size: 13px; padding: 10px 8px;">GRAND TOTAL</td>
                    <td class="text-right" style="font-weight: bold; font-size: 14px; color: #d6336c; padding: 10px 8px;">Rs. {grand_total:.2f}</td>
                </tr>
            </table>

            <div style="font-size: 9px; margin-top: 25px; color: #555;">
                <strong style="color: #333;">TERMS & CONDITIONS :</strong><br>
                1. Check out Time 12:00 Noon. Extra hours will be subject to availability and charges.<br>
                2. Subject to Muzaffarnagar Jurisdiction Only.<br>
                E. & O.E.
            </div>

            <table style="width: 100%; margin-top: 50px; font-size: 11px;">
                <tr>
                    <td style="width: 50%; vertical-align: bottom;">____________________<br><br>Guest Signature</td>
                    <td style="width: 50%; text-align: right;">
                        For <strong>Hotel Royale Paradise</strong><br><br><br><br>
                        ____________________<br><br>Auth. Signatory
                    </td>
                </tr>
            </table>
            """
            
            # Show live preview
            preview_wrapper = f"<div style='background-color: white; padding: 30px; border: 1px solid #ccc; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); max-width: 800px; margin: auto;'>{core_html}</div>"
            components.html(preview_wrapper, height=750, scrolling=True)
            
            # PDF Download
            pdf_bytes = generate_pdf(core_html)
            if pdf_bytes:
                col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                with col_d2:
                    st.download_button(
                        label="📥 Download & Print Final PDF",
                        data=pdf_bytes,
                        file_name=f"Invoice_{bill_no}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

with tab2:
    st.subheader("Database Overview")
    conn = sqlite3.connect("royal_paradise_hotel.db")
    df = pd.read_sql_query("SELECT * FROM invoices", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download CA Report (Excel format)",
            data=csv,
            file_name=f"GST_Report_Hotel_{datetime.now().strftime('%b_%Y')}.csv",
            mime='text/csv',
            type="primary"
        )
    else:
        st.info("Your database is currently empty. Generated invoices will appear here.")
