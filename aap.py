import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, time
from io import BytesIO
from xhtml2pdf import pisa
import streamlit.components.v1 as components

# --- PAGE CONFIGURATION (Professional Look) ---
st.set_page_config(page_title="Hotel Royale Paradise | PMS Dashboard", page_icon="🏨", layout="wide")

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
        body {{ font-family: Helvetica, sans-serif; font-size: 11px; color: #333333; }}
        th {{ font-weight: bold; }}
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
st.markdown("<h2 style='text-align: center; color: #800020; font-family: serif;'>Hotel Royale Paradise | <span style='font-size: 20px; color: #555;'>Property Management System</span></h2>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🧾 Generate Invoice (2026 Format)", "📊 Monthly GST Records"])

with tab1:
    with st.container():
        # --- SECTION 1: GUEST DETAILS ---
        st.markdown("<h5 style='color: #800020; margin-bottom: 15px;'>👤 Guest & Room Details</h5>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            customer_name = st.text_input("Guest Name *", placeholder="e.g. Rahul Sharma")
        with col2:
            customer_gstin = st.text_input("Guest GSTIN", placeholder="Optional for B2B")
        with col3:
            room_no = st.text_input("Room No. *", placeholder="e.g. 302")
        with col4:
            no_of_person = st.number_input("No. Of Persons", min_value=1, value=1)

        st.markdown("<hr style='border-top: 1px dashed #ccc; margin: 15px 0;'>", unsafe_allow_html=True)

        # --- SECTION 2: STAY DETAILS (WITH CALENDAR & TIME PICKER) ---
        st.markdown("<h5 style='color: #800020; margin-bottom: 15px;'>🗓️ Stay & Billing Details</h5>", unsafe_allow_html=True)
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            ci_date = st.date_input("Check-In Date", value=datetime.today())
            ci_time = st.time_input("Check-In Time", value=time(12, 0)) # Default 12:00 PM
        with col6:
            co_date = st.date_input("Check-Out Date", value=datetime.today())
            co_time = st.time_input("Check-Out Time", value=time(11, 0)) # Default 11:00 AM
        with col7:
            rate = st.number_input("Room Rate per Day (Rs.) *", min_value=0.0, value=2500.0)
            st.markdown("<br>", unsafe_allow_html=True) # Spacing adjustment
        with col8:
            days = st.number_input("Total Days *", min_value=1, value=1)

    # Combining selected Date and Time into a single string for DB & PDF
    check_in = f"{ci_date.strftime('%d-%m-%Y')} {ci_time.strftime('%I:%M %p')}"
    check_out = f"{co_date.strftime('%d-%m-%Y')} {co_time.strftime('%I:%M %p')}"

    st.markdown("<br>", unsafe_allow_html=True)
    
    total_taxable = rate * days
    cgst = total_taxable * 0.025
    sgst = total_taxable * 0.025
    grand_total = total_taxable + cgst + sgst

    # Generate Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_btn = st.button("🚀 Generate Final Tax Invoice", type="primary", use_container_width=True)

    if generate_btn:
        if not customer_name or not room_no:
            st.error("⚠️ Guest Name and Room Number are mandatory.")
        else:
            bill_no = get_next_bill_no()
            bill_date = datetime.now().strftime("%d-%m-%Y")
            
            db_data = (bill_no, bill_date, customer_name, customer_gstin, room_no, 
                       no_of_person, check_in, check_out, days, rate, total_taxable, cgst, sgst, grand_total)
            save_invoice(db_data)
            
            st.success(f"✅ Invoice {bill_no} successfully generated in HD Format.")

            # --- MODERN 2026 CORPORATE INVOICE TEMPLATE ---
            core_html = f"""
            <!-- HEADER SECTION -->
            <table style="width: 100%; border-bottom: 2px solid #800020; padding-bottom: 15px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <div style="font-family: Times-Roman, serif; font-size: 26px; color: #800020; font-weight: bold; letter-spacing: 1px;">HOTEL ROYALE PARADISE</div>
                        <div style="font-size: 10px; color: #555555; margin-top: 4px;">(A Unit of Akhand Enterprises (P) Ltd.)</div>
                        <div style="font-size: 10px; color: #555555; margin-top: 4px;">Y-349 C, Sector-12, NOIDA-201301 (U.P.)</div>
                        <div style="font-size: 10px; color: #555555; margin-top: 2px;">Phone: +91-120-2536460, 2533391, 9818675476</div>
                    </td>
                    <td style="width: 40%; text-align: right; vertical-align: top;">
                        <div style="font-size: 22px; color: #333333; font-weight: bold; letter-spacing: 2px;">TAX INVOICE</div>
                        <div style="font-size: 11px; color: #333; margin-top: 8px;"><strong>Invoice No:</strong> {bill_no}</div>
                        <div style="font-size: 11px; color: #333; margin-top: 3px;"><strong>Date:</strong> {bill_date}</div>
                    </td>
                </tr>
            </table>

            <!-- DETAILS GRID SECTION -->
            <table style="width: 100%; margin-top: 15px; margin-bottom: 20px;">
                <tr>
                    <!-- Guest Details -->
                    <td style="width: 48%; padding: 12px; border: 1px solid #e0e0e0; background-color: #fafafa; vertical-align: top;">
                        <div style="font-size: 10px; color: #800020; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; letter-spacing: 1px;">BILLED TO</div>
                        <div style="font-size: 12px; font-weight: bold; color: #111;">{customer_name.upper()}</div>
                        <div style="font-size: 10px; color: #555; margin-top: 5px;"><strong>GSTIN:</strong> {customer_gstin if customer_gstin else 'N/A'}</div>
                    </td>
                    <td style="width: 4%;"></td>
                    <!-- Stay Details -->
                    <td style="width: 48%; padding: 12px; border: 1px solid #e0e0e0; background-color: #fafafa; vertical-align: top;">
                        <div style="font-size: 10px; color: #800020; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; letter-spacing: 1px;">STAY DETAILS</div>
                        <table style="width: 100%; font-size: 10px; color: #333;">
                            <tr><td style="padding-bottom: 3px;"><strong>Room No:</strong></td><td style="text-align: right; padding-bottom: 3px;">{room_no}</td></tr>
                            <tr><td style="padding-bottom: 3px;"><strong>Guests:</strong></td><td style="text-align: right; padding-bottom: 3px;">{no_of_person}</td></tr>
                            <tr><td style="padding-bottom: 3px;"><strong>Check-In:</strong></td><td style="text-align: right; padding-bottom: 3px;">{check_in}</td></tr>
                            <tr><td style="padding-bottom: 3px;"><strong>Check-Out:</strong></td><td style="text-align: right; padding-bottom: 3px;">{check_out}</td></tr>
                        </table>
                    </td>
                </tr>
            </table>

            <!-- MAIN BILLING TABLE -->
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="background-color: #800020; color: white; padding: 10px; text-align: left; font-size: 10px; border: 1px solid #800020;">DESCRIPTION OF SERVICES</th>
                        <th style="background-color: #800020; color: white; padding: 10px; text-align: center; font-size: 10px; border: 1px solid #800020; width: 15%;">RATE (Rs.)</th>
                        <th style="background-color: #800020; color: white; padding: 10px; text-align: center; font-size: 10px; border: 1px solid #800020; width: 15%;">QTY/DAYS</th>
                        <th style="background-color: #800020; color: white; padding: 10px; text-align: right; font-size: 10px; border: 1px solid #800020; width: 20%;">AMOUNT (Rs.)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #e0e0e0; border-bottom: none; font-size: 11px; height: 120px; vertical-align: top;">
                            <strong>Room Rent / Lodging Charges</strong>
                        </td>
                        <td style="text-align: center; padding: 12px; border: 1px solid #e0e0e0; border-bottom: none; font-size: 11px; vertical-align: top;">{rate:.2f}</td>
                        <td style="text-align: center; padding: 12px; border: 1px solid #e0e0e0; border-bottom: none; font-size: 11px; vertical-align: top;">{days}</td>
                        <td style="text-align: right; padding: 12px; border: 1px solid #e0e0e0; border-bottom: none; font-size: 11px; vertical-align: top;">{total_taxable:.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="4" style="border-left: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #800020; height: 10px;"></td>
                    </tr>
                </tbody>
            </table>

            <!-- TAXES & TOTALS -->
            <table style="width: 100%; border-collapse: collapse; margin-top: 0;">
                <tr>
                    <td style="width: 55%; border: 1px solid #e0e0e0; border-top: none; padding: 12px; vertical-align: top; background-color: #fafafa;">
                        <div style="font-size: 9px; color: #555; line-height: 1.6;">
                            <strong style="color: #333;">Statutory & Company Details:</strong><br>
                            <strong>CIN:</strong> U54132UP1999PTC024452<br>
                            <strong>GSTIN:</strong> 09AADCA6394B2ZP<br>
                            <strong>Registered Office:</strong><br>
                            Kishori Kunj, 105-B, Gaushala Road,<br>New Mandi, Muzaffarnagar (U.P.)
                        </div>
                    </td>
                    <td style="width: 45%; border: 1px solid #e0e0e0; border-top: none; padding: 0;">
                        <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 12px; color: #555; border-bottom: 1px solid #eee;">Taxable Amount</td>
                                <td style="text-align: right; padding: 8px 12px; border-bottom: 1px solid #eee;">{total_taxable:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 12px; color: #555; border-bottom: 1px solid #eee;">CGST (2.5%)</td>
                                <td style="text-align: right; padding: 8px 12px; border-bottom: 1px solid #eee;">{cgst:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 12px; color: #555;">SGST (2.5%)</td>
                                <td style="text-align: right; padding: 8px 12px;">{sgst:.2f}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px; background-color: #800020; color: white; font-weight: bold; font-size: 13px; letter-spacing: 1px;">GRAND TOTAL</td>
                                <td style="text-align: right; padding: 12px; background-color: #800020; color: white; font-weight: bold; font-size: 14px;">Rs. {grand_total:.2f}</td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <!-- FOOTER & SIGNATURE -->
            <table style="width: 100%; margin-top: 50px;">
                <tr>
                    <td style="width: 60%; font-size: 9px; color: #666; vertical-align: bottom; line-height: 1.5;">
                        <strong style="color: #333; font-size: 10px;">Terms & Conditions:</strong><br>
                        1. Standard Check-out time is 12:00 Noon.<br>
                        2. All disputes are subject to Muzaffarnagar Jurisdiction.<br>
                        3. This is a computer-generated invoice.<br>
                        E. & O.E.
                    </td>
                    <td style="width: 40%; text-align: center; vertical-align: bottom;">
                        <div style="font-size: 10px; color: #333; margin-bottom: 45px;">For <strong>Hotel Royale Paradise</strong></div>
                        <div style="border-top: 1px solid #333; width: 80%; margin: 0 auto; padding-top: 5px; font-size: 10px; font-weight: bold;">Authorized Signatory</div>
                    </td>
                </tr>
            </table>
            """
            
            # Live Preview rendering
            preview_wrapper = f"<div style='background-color: white; padding: 40px; border: 1px solid #eaeaea; box-shadow: 0px 10px 30px rgba(0,0,0,0.05); max-width: 800px; margin: 20px auto;'>{core_html}</div>"
            components.html(preview_wrapper, height=750, scrolling=True)
            
            # PDF Generation
            pdf_bytes = generate_pdf(core_html)
            if pdf_bytes:
                col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                with col_d2:
                    st.download_button(
                        label="📥 Download Professional PDF",
                        data=pdf_bytes,
                        file_name=f"Tax_Invoice_HRP_{bill_no}.pdf",
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
