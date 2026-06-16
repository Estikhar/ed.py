import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import base64

# Page Configuration & Theme Styling
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

# --- APP INTERFACE ---
st.title("🏨 Hotel Royale Paradise")
st.subheader("Cloud-Based GST Billing Engine")

tab1, tab2 = st.tabs(["🆕 New Invoice", "📊 GST Reports & History"])

with tab1:
    st.info("Fill guest details below to generate a print-ready pink format invoice.")
    
    # Form Inputs
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

    # Calculation logic
    total_taxable = rate * days
    cgst = total_taxable * 0.025
    sgst = total_taxable * 0.025
    grand_total = total_taxable + cgst + sgst

    if st.button("Generate & Print Bill"):
        if not customer_name or not room_no:
            st.error("Please fill required fields (Guest Name & Room No.)")
        else:
            bill_no = get_next_bill_no()
            bill_date = datetime.now().strftime("%d-%m-%Y")
            
            # Save to Cloud DB
            db_data = (bill_no, bill_date, customer_name, customer_gstin, room_no, 
                       no_of_person, check_in, check_out, days, rate, total_taxable, cgst, sgst, grand_total)
            save_invoice(db_data)
            
            st.success(f"Invoice {bill_no} successfully stored in database!")

            # Raw HTML layout replicating your exact Pink Invoice Slip ('image.png')
            html_invoice = f"""
            <div style="background-color: #fff0f5; padding: 25px; border: 2px solid #d6336c; font-family: 'Arial', sans-serif; color: #2d3748; border-radius: 5px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="font-size: 11px;"><strong>CIN :</strong> U54132UP1999PTC024452</td>
                        <td style="text-align: right; font-size: 11px;"><strong>GSTIN :</strong> 09AADCA6394B2ZP</td>
                    </tr>
                </table>
                <div style="text-align: center; margin-top: 5px;">
                    <span style="font-size: 14px; letter-spacing: 2px; font-weight: bold; border-bottom: 1px solid black;">BILL</span>
                    <h1 style="color: #d6336c; font-style: italic; margin: 5px 0 2px 0; font-size: 26px;">Hotel Royale Paradise</h1>
                    <p style="font-size: 11px; margin: 0; font-weight: bold;">(A Unit of Akhand Enterprises (P) Ltd.)</p>
                    <p style="font-size: 10px; margin: 2px 0;">Regd. Off. : Kishori Kunj, 105-B, Gaushala Road, New Mandi, Muzaffarnagar (U.P.)</p>
                    <p style="font-size: 11px; margin: 0; font-weight: bold; background-color: rgba(214,51,108,0.1); padding: 3px;">Y-349 C, Sector-12, NOIDA-201301 (U.P.) Ph. : 91-120-2536460, 2533391, 9818675476</p>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #d6336c; margin: 15px 0;">

                <table style="width: 100%; font-size: 12px; margin-bottom: 15px;">
                    <tr>
                        <td style="width: 55%; line-height: 1.6;">
                            <strong>GUEST DETAILS:</strong><br>
                            Name: {customer_name}<br>
                            GSTIN: {customer_gstin if customer_gstin else 'N/A'}
                        </td>
                        <td style="width: 45%; line-height: 1.6; border-left: 1px dashed #d6336c; padding-left: 15px;">
                            <strong>BILL NO. : {bill_no}</strong><br>
                            BILL DATE : {bill_date}<br>
                            ROOM NO. : {room_no}<br>
                            NO. OF PERSON : {no_of_person}
                        </td>
                    </tr>
                </table>

                <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px;">
                    <thead>
                        <tr style="background-color: #d6336c; color: white;">
                            <th style="border: 1px solid #d6336c; padding: 8px; text-align: left;">PARTICULARS</th>
                            <th style="border: 1px solid #d6336c; padding: 8px; text-align: center; width: 20%;">RATE (₹)</th>
                            <th style="border: 1px solid #d6336c; padding: 8px; text-align: right; width: 20%;">AMOUNT (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="height: 120px;">
                            <td style="border: 1px solid #d6336c; padding: 8px;">
                                <strong>Lodging Charges for {days} days</strong><br>
                                <span style="font-size: 11px; color: #555;">From: {check_in}<br>To: {check_out}</span>
                            </td>
                            <td style="border: 1px solid #d6336c; padding: 8px; text-align: center;">{rate:.2f}</td>
                            <td style="border: 1px solid #d6336c; padding: 8px; text-align: right;">{total_taxable:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="border: 1px solid #d6336c; padding: 6px; text-align: right; font-weight: bold;">TOTAL</td>
                            <td style="border: 1px solid #d6336c; padding: 6px; text-align: right; font-weight: bold;">{total_taxable:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="border: 1px solid #d6336c; padding: 4px; text-align: right;">CGST (2.5%)</td>
                            <td style="border: 1px solid #d6336c; padding: 4px; text-align: right;">{cgst:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="border: 1px solid #d6336c; padding: 4px; text-align: right;">SGST (2.5%)</td>
                            <td style="border: 1px solid #d6336c; padding: 4px; text-align: right;">{sgst:.2f}</td>
                        </tr>
                        <tr style="background-color: rgba(214,51,108,0.1);">
                            <td colspan="2" style="border: 1px solid #d6336c; padding: 8px; text-align: right; font-weight: bold; font-size: 13px;">GRAND TOTAL</td>
                            <td style="border: 1px solid #d6336c; padding: 8px; text-align: right; font-weight: bold; font-size: 13px; color: #d6336c;">₹ {grand_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>

                <div style="font-size: 11px; margin-top: 15px; border-left: 2px solid #d6336c; padding-left: 10px;">
                    <strong>TERMS & CONDITIONS :</strong><br>
                    1. Check out Time 12:00 Noon<br>
                    2. Subject to Muzaffarnagar Jurisdiction Only<br>
                    E. & O.E.
                </div>

                <table style="width: 100%; margin-top: 40px; font-size: 12px;">
                    <tr>
                        <td style="width: 50%; vertical-align: bottom;">Guest Signature</td>
                        <td style="width: 50%; text-align: right; line-height: 1.5;">
                            For <strong>Hotel Royale Paradise</strong><br><br><br>
                            Auth. Signatory
                        </td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(html_invoice, unsafe_allow_html=True)
            
            # Simple Window Print trigger
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

with tab2:
    st.subheader("Database History")
    conn = sqlite3.connect("royal_paradise_hotel.db")
    df = pd.read_sql_query("SELECT * FROM invoices", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df)
        
        # GSTR Excel Generation for CA
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Monthly GST Ledger (CSV/Excel)",
            data=csv,
            file_name=f"GST_Report_{datetime.now().strftime('%m_%Y')}.csv",
            mime='text/csv',
        )
    else:
        st.warning("No invoices generated yet.")
