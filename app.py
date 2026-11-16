import streamlit as st
import pandas as pd
from datetime import date

# Import custom database functions from the database package
from database.db_handler import init_db, search_equipment, add_new_equipment

# Import PDF generator functions from the templates package
from templates.mmd_template import generate_mmd_pdf
from templates.rd_template import generate_rd_pdf

# Set page configuration for the Streamlit web app
st.set_page_config(
    page_title="Indent Form Generation System",
    page_icon="📋",
    layout="wide"
)

# Initialize the database and load default sample items if not already initialized
init_db()

# --- Session State Initialization ---
# Streamlit reruns scripts on every interaction. We use st.session_state 
# to persistently store the selected cart items and generated form state across runs.
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- Main Title Header ---
st.title("📋 Automated Indent Form Generation System")
st.markdown("Institutional Procurement and R&D Equipment Indent Management Portal")
st.markdown("---")

# --- Sidebar Configuration & Form Type Selection ---
st.sidebar.header("⚙️ Indent Configuration")

# Select Form Type: MMD (General/Office) or R&D (Research & Lab)
form_type = st.sidebar.selectbox(
    "Select Indent Form Type",
    ["MMD Indent Form (General/Office)", "R&D Indent Form (Research Lab)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("👤 Requester Details")
requester_name = st.sidebar.text_input("Requester Name / PI", value="Dr. A. Sharma")
department_name = st.sidebar.text_input("Department / Lab Name", value="Electrical Engineering / CSPML Lab")

# Conditional sidebar input based on form type
if "R&D" in form_type:
    grant_code = st.sidebar.text_input("Project / Grant Code", value="SERB-CRG-2026-XYZ")
else:
    grant_code = "N/A"

indent_id_input = st.sidebar.text_input("Indent Reference ID", value="IND-2026-001")
indent_date = st.sidebar.date_input("Indent Date", value=date.today())

st.sidebar.markdown("---")
st.sidebar.info("💡 **Workflow Tip:** Search & select items from the database, adjust quantities, preview, and export your official PDF form instantly!")

# --- Main Dashboard Layout ---
tab1, tab2, tab3 = st.tabs(["🔍 Search & Add Items", "🛒 Selected Items Cart", "📄 Preview & Export PDF"])

# ==========================================
# TAB 1: SEARCH & ADD ITEMS (OR MANUAL ENTRY)
# ==========================================
with tab1:
    st.subheader("Search Equipment Database")
    
    # Search input box supporting flexible keyword matching
    search_query = st.text_input("Type equipment name, category, manufacturer, or model keyword...", "")
    
    # Fetch filtered DataFrame results from database
    search_results_df = search_equipment(search_query)
    
    if not search_results_df.empty:
        st.success(f"Found {len(search_results_df)} matching item(s) in database.")
        
        # Display items in an interactive table view
        st.dataframe(search_results_df, use_container_width=True)
        
        st.markdown("### Add Item to Indent Cart")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Select item by name from search results
            item_options = search_results_df['item_name'].tolist()
            selected_item_name = st.selectbox("Select Equipment from Results", item_options)
        
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            
        with col3:
            st.markdown("<br>", unsafe_allow_html=True) # Spacer alignment
            add_to_cart_btn = st.button("➕ Add to Cart", type="primary")
            
        if add_to_cart_btn:
            # Fetch complete row details for the selected item
            selected_row = search_results_df[search_results_df['item_name'] == selected_item_name].iloc[0]
            
            cart_item = {
                "id": int(selected_row['id']),
                "item_name": selected_row['item_name'],
                "category": selected_row['category'],
                "manufacturer": selected_row['manufacturer'],
                "model": selected_row['model'],
                "part_number": selected_row['part_number'],
                "unit_price": float(selected_row['unit_price']),
                "description": selected_row['description'],
                "quantity": int(quantity)
            }
            
            # Append item to session cart state
            st.session_state.cart.append(cart_item)
            st.success(f"Added {quantity} x {selected_item_name} to cart successfully!")
    else:
        st.warning("No matching items found in the database.")

    st.markdown("---")
    st.subheader("➕ Manual Entry (If Item Not Found in Database)")
    with st.expander("Click here to enter a custom item manually"):
        with st.form("manual_entry_form"):
            m_name = st.text_input("Equipment Name *")
            m_cat = st.selectbox("Category", ["R&D Equipment", "General Lab", "MMD / Office", "Computers & IT"])
            m_mfg = st.text_input("Manufacturer / Make")
            m_model = st.text_input("Model Number")
            m_part = st.text_input("Part Number / SKU")
            m_price = st.number_input("Estimated Unit Price (₹)", min_value=0.0, value=1000.0, step=100.0)
            m_desc = st.text_area("Technical Description & Specifications")
            
            save_to_db_checkbox = st.checkbox("Save this new equipment to database for future use", value=True)
            submit_manual = st.form_submit_button("Add Manual Item to Cart")
            
            if submit_manual:
                if m_name.strip() == "":
                    st.error("Equipment Name is mandatory!")
                else:
                    # Save to database if requested
                    if save_to_db_checkbox:
                        add_new_equipment(m_name, m_cat, m_mfg, m_model, m_part, m_price, m_desc)
                        st.info("New item saved permanently to the equipment database.")
                    
                    # Add directly to session cart
                    manual_item = {
                        "id": 9999,
                        "item_name": m_name,
                        "category": m_cat,
                        "manufacturer": m_mfg,
                        "model": m_model,
                        "part_number": m_part,
                        "unit_price": float(m_price),
                        "description": m_desc,
                        "quantity": 1
                    }
                    st.session_state.cart.append(manual_item)
                    st.success(f"Manual item '{m_name}' added to cart successfully!")

# ==========================================
# TAB 2: SELECTED ITEMS CART
# ==========================================
with tab2:
    st.subheader("🛒 Current Indent Items Cart")
    
    if len(st.session_state.cart) > 0:
        cart_df = pd.DataFrame(st.session_state.cart)
        # Calculate total price per line item
        cart_df['Total Price (₹)'] = cart_df['quantity'] * cart_df['unit_price']
        
        st.dataframe(cart_df[['item_name', 'category', 'manufacturer', 'model', 'quantity', 'unit_price', 'Total Price (₹)']], use_container_width=True)
        
        # Display Grand Total calculation
        grand_total = cart_df['Total Price (₹)'].sum()
        st.markdown(f"### **Estimated Grand Total: ₹{grand_total:,.2f}**")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🗑️ Clear Cart"):
                st.session_state.cart = []
                st.rerun()
        with col_c2:
            st.info("Head over to the 'Preview & Export PDF' tab to generate your official form.")
    else:
        st.info("Your cart is currently empty. Search and add items from Tab 1.")

# ==========================================
# TAB 3: PREVIEW & EXPORT PDF
# ==========================================
with tab3:
    st.subheader("📄 Form Preview & PDF Export")
    
    purpose_justification = st.text_area("Purpose / Justification for Indent", value="Required urgently for ongoing research experiments and academic coursework requirements.")
    
    if len(st.session_state.cart) == 0:
        st.warning("Please add at least one item to your cart before generating the PDF form.")
    else:
        if st.button("🚀 Generate Official PDF Form", type="primary"):
            # Package all form data dictionary
            indent_payload = {
                "department": department_name,
                "requester": requester_name,
                "date": str(indent_date),
                "indent_id": indent_id_input,
                "grant_code": grant_code,
                "purpose": purpose_justification,
                "items": st.session_state.cart
            }
            
            try:
                # Generate PDF based on user selection in sidebar
                if "MMD" in form_type:
                    pdf_path = generate_mmd_pdf(indent_payload)
                    form_title = "MMD Indent Form"
                else:
                    pdf_path = generate_rd_pdf(indent_payload)
                    form_title = "R&D Indent Form"
                    
                st.success(f"🎉 {form_title} generated successfully!")
                
                # Provide direct download button for the generated PDF
                with open(pdf_path, "rb") as pdf_file:
                    bytes_data = pdf_file.read()
                    st.download_button(
                        label=f"📥 Download {form_title} (PDF)",
                        data=bytes_data,
                        file_name=pdf_path.split("/")[-1],
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error generating PDF: {e}")