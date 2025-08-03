# app.py
import streamlit as st
import pdfplumber
import pandas as pd
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
import logging

from utils.parsers import parse_chase, parse_bofa, parse_wells
from utils.decision_engine import make_decision

# Configuration
MAX_FILE_SIZE_MB = 10
SUPPORTED_BANKS = {
    "Chase": ["Chase", "JPMorgan Chase", "JPMORGAN CHASE"],
    "Bank of America": ["Bank of America", "BofA", "BANK OF AMERICA"],
    "Wells Fargo": ["Wells Fargo", "Wells", "WELLS FARGO"]
}

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(page_title="MCA Deal Analyzer", layout="wide")

def validate_file(uploaded_file) -> Tuple[bool, str]:
    """Validate uploaded file size and type."""
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
    
    if not uploaded_file.name.lower().endswith('.pdf'):
        return False, "Only PDF files are supported"
    
    return True, ""

@st.cache_data
def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF with error handling."""
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                return ""
            
            text_parts = []
            for page in pdf.pages:
                if text := page.extract_text():
                    text_parts.append(text)
            
            return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""

def detect_bank(text: str) -> Optional[str]:
    """Detect bank from PDF text content."""
    text_upper = text.upper()
    
    for bank_name, identifiers in SUPPORTED_BANKS.items():
        if any(identifier.upper() in text_upper for identifier in identifiers):
            return bank_name
    
    return None

def parse_transactions(uploaded_file, bank: str) -> Optional[pd.DataFrame]:
    """Parse transactions based on detected bank."""
    parsers = {
        "Chase": parse_chase,
        "Bank of America": parse_bofa,
        "Wells Fargo": parse_wells
    }
    
    try:
        parser = parsers.get(bank)
        if not parser:
            return None
        
        df = parser(uploaded_file)
        
        # Validate parsed data
        if df is None or df.empty:
            return None
        
        # Basic data validation
        required_columns = ['date', 'amount']  # Adjust based on your parser outputs
        if not all(col in df.columns for col in required_columns):
            logger.warning(f"Missing required columns in parsed data: {df.columns.tolist()}")
        
        return df
    
    except Exception as e:
        logger.error(f"Transaction parsing failed for {bank}: {e}")
        return None

def display_results(results: Dict[str, Any]):
    """Display analysis results in organized format."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Financial Analysis")
        st.metric("Average Monthly Revenue", f"${results['avg_revenue']:,}")
        st.metric("NSF Incidents", results['nsfs'])
        st.metric("Negative Balance Days", results['neg_days'])
    
    with col2:
        st.subheader("🎯 Deal Decision")
        if results['approved']:
            st.success("✅ APPROVED")
            st.metric("Recommended Amount", f"${results['amount']:,}")
            st.info(f"**Term**: {results['term']} | **Factor**: {results['factor']}")
        else:
            st.error("❌ DECLINED")
            st.subheader("Decline Reasons:")
            for reason in results['reasons']:
                st.write(f"• {reason}")

def main():
    """Main application logic."""
    st.title("📄 MCA Instant Deal Analyzer")
    st.markdown("Upload a PDF bank statement and instantly receive a deal recommendation.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Bank Statement PDF", 
        type=["pdf"],
        help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB. Supported banks: {', '.join(SUPPORTED_BANKS.keys())}"
    )
    
    if not uploaded_file:
        return
    
    # File validation
    is_valid, error_message = validate_file(uploaded_file)
    if not is_valid:
        st.error(f"❌ {error_message}")
        return
    
    # Processing with progress indicators
    with st.spinner("Processing PDF..."):
        # Extract text
        file_bytes = uploaded_file.read()
        full_text = extract_pdf_text(file_bytes)
        
        if not full_text:
            st.error("❌ Unable to extract text from PDF. Please ensure the file is not corrupted or password-protected.")
            return
    
    # Bank detection
    detected_bank = detect_bank(full_text)
    if not detected_bank:
        st.error("❌ Unsupported bank format detected.")
        st.info(f"**Supported banks**: {', '.join(SUPPORTED_BANKS.keys())}")
        
        # Show first 500 chars for debugging
        with st.expander("🔍 Debug: PDF Content Preview"):
            st.text(full_text[:500] + "..." if len(full_text) > 500 else full_text)
        return
    
    st.success(f"✅ Detected bank: **{detected_bank}**")
    
    # Parse transactions
    with st.spinner("Parsing transactions..."):
        # Reset file pointer
        uploaded_file.seek(0)
        transactions_df = parse_transactions(uploaded_file, detected_bank)
        
        if transactions_df is None:
            st.error("❌ Failed to parse transaction data. The PDF format may not be supported.")
            return
        
        if transactions_df.empty:
            st.warning("⚠️ No transactions found in the statement.")
            return
    
    st.success(f"✅ Parsed {len(transactions_df)} transactions")
    
    # Display transaction data
    with st.expander(f"📋 View Transactions ({len(transactions_df)} records)"):
        st.dataframe(transactions_df, use_container_width=True)
    
    # Run analysis
    with st.spinner("Analyzing deal..."):
        try:
            analysis_results = make_decision(transactions_df)
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            logger.error(f"Decision engine error: {e}")
            return
    
    # Display results
    display_results(analysis_results)
    
    # Download option
    st.divider()
    csv_data = transactions_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Transactions CSV",
        data=csv_data,
        file_name=f"{detected_bank.lower().replace(' ', '_')}_transactions.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()