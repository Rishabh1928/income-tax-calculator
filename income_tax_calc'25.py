import streamlit as st
import pandas as pd

# ------------------------------
# Custom CSS Styling
# ------------------------------
st.markdown(
    """
    <style>
        /* Main container and block styling */
        .main { background-color: #f8f9fa; }
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }
        /* Header styles */
        .header-style { color: #2c3e50; text-align: center; font-size: 2.5rem; }
        .subheader-style { color: #34495e; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        /* Metric card styling */
        .metric-box { 
            background: white; 
            border-radius: 15px; 
            padding: 1.5rem; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin: 1rem 0;
        }
        .positive { color: #27ae60; font-weight: 600; }
        .negative { color: #e74c3c; font-weight: 600; }
        /* Footer styling */
        .footer { 
            text-align: center; 
            padding: 1.5rem;
            background-color: #2c3e50;
            color: white;
            margin-top: 3rem;
            border-radius: 10px;
        }
        /* Input header styling */
        .input-header { color: #3498db; font-weight: 600; margin-bottom: 0.5rem; }
    </style>
    """, 
    unsafe_allow_html=True
)

# ------------------------------
# Tax Slabs for New Regime (Comparison)
# ------------------------------
NEW_REGIME_SLABS = {
    "FY24-25": [
        (0, 300000, 0),
        (300000, 600000, 5),
        (600000, 900000, 10),
        (900000, 1200000, 15),
        (1200000, 1500000, 20),
        (1500000, float('inf'), 30)
    ],
    "FY25-26": [
        (0, 400000, 0),
        (400000, 800000, 5),
        (800000, 1200000, 10),
        (1200000, 1600000, 15),
        (1600000, 2000000, 20),
        (2000000, 2400000, 25),
        (2400000, float('inf'), 30)
    ]
}

def calculate_tax(taxable_income, slabs):
    """
    Calculate base tax based on taxable income and the given tax slabs.
    Each slab is a tuple: (lower_bound, upper_bound, tax_rate_in_percent).
    """
    tax = 0
    for lower, upper, rate in slabs:
        if taxable_income > lower:
            income_in_slab = min(taxable_income, upper) - lower
            tax += income_in_slab * rate / 100
    return tax

def compute_total_tax(given_total_income, taxable_income, slabs):
    """
    Compute the final tax liability after applying:
      - Tax computed as per slabs on the final taxable income (after deductions).
      - Rebate under Section 87A: if given total income is ≤ ₹12,75,000, then no tax is payable.
      - Health & Education Cess: 4% on the computed tax.
    Returns a tuple: (total_tax, base_tax, cess)
    """
    # Check based on the given total income, not the taxable income after deductions.
    if given_total_income <= 1275000:
        base_tax = 0
    else:
        base_tax = calculate_tax(taxable_income, slabs)
    cess = base_tax * 0.04
    return base_tax + cess, base_tax, cess

def generate_report(report_data):
    """
    Generate a text report from the provided report_data dictionary.
    """
    lines = []
    lines.append("INCOME TAX REPORT")
    lines.append("=" * 50)
    lines.append("\n--- Income Details ---")
    for key, value in report_data['Income Details'].items():
        lines.append(f"{key}: ₹{value:,.2f}")
    lines.append("\n--- Tax Calculation ---")
    for key, value in report_data['Tax Calculation'].items():
        lines.append(f"{key}: ₹{value:,.2f}")
    lines.append("\n--- Additional Info ---")
    lines.append("Monthly Tax: ₹{0:,.2f}".format(report_data['Tax Calculation']['Total Tax'] / 12))
    lines.append("=" * 50)
    return "\n".join(lines)

# ------------------------------
# Sidebar Configuration & Info
# ------------------------------
st.sidebar.title("ℹ️ Calculator Info")
st.sidebar.markdown(
    """
    **Comparison Features:**
    - Compare New Regime FY24-25 vs FY25-26 tax slabs
    - Standard Deduction: ₹75,000
    - NPS Deduction (up to 14% of Basic Salary)
    - Section 87A Rebate: No tax if your **total income** is ≤ ₹12,75,000
    
    **Key Differences:**
    - Revised tax slabs and exemption limits for FY25-26
    - Additional tax brackets in the latest regime
    """
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 0.9em; color: #7f8c8d;">
        Data Source: Union Budget 2025<br>
    </div>
    """, 
    unsafe_allow_html=True
)

# ------------------------------
# Main Application Header
# ------------------------------
st.markdown("<h1 class='header-style'>Income Tax Calculator</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subheader-style'>New Regime: FY24-25 vs FY25-26 Comparison</h3>", unsafe_allow_html=True)

# ------------------------------
# Input Section
# ------------------------------
with st.container():
    st.markdown("<div class='input-header'>💰 Income Details</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        total_income = st.number_input(
            "Gross Annual Income (₹):", 
            min_value=0.0, 
            value=1800000.0, 
            step=10000.0, 
            format="%.0f",
            help="Enter your total annual income before any deductions."
        )
    with col2:
        basic_salary_pct = st.number_input(
            "Basic Salary Percentage (%):", 
            min_value=0.0, 
            max_value=100.0, 
            value=40.0, 
            step=1.0, 
            format="%.1f",
            help="Enter the percentage of your total income that is your basic salary."
        )

    st.markdown("<div class='input-header'>📉 Deductions</div>", unsafe_allow_html=True)
    nps_pct = st.slider(
        "NPS Contribution (% of Basic Salary):", 
        min_value=0, 
        max_value=14, 
        value=10, 
        help="Maximum allowed under Section 80CCD(1) is 14% of Basic Salary."
    )

# ------------------------------
# Calculations
# ------------------------------
basic_salary = total_income * (basic_salary_pct / 100)
nps_deduction = basic_salary * (nps_pct / 100)
standard_deduction = 75000
final_taxable_income = max(total_income - standard_deduction - nps_deduction, 0)

# ------------------------------
# Results Section
# ------------------------------
if st.button("🧮 Calculate Tax Liability", type="primary", use_container_width=True):
    # Compute tax for the two financial years using the respective slabs
    current_total_tax, current_base_tax, current_cess = compute_total_tax(total_income, final_taxable_income, NEW_REGIME_SLABS["FY25-26"])
    previous_total_tax, previous_base_tax, previous_cess = compute_total_tax(total_income, final_taxable_income, NEW_REGIME_SLABS["FY24-25"])
    tax_difference = current_total_tax - previous_total_tax

    # Detailed Deduction Breakdown
    with st.expander("📊 Detailed Breakdown", expanded=True):
        cols = st.columns(3)
        cols[0].metric("Basic Salary", f"₹{basic_salary:,.0f}")
        cols[1].metric("NPS Contribution", f"₹{nps_deduction:,.0f}", f"{nps_pct}% of Basic")
        cols[2].metric("Standard Deduction", "₹75,000", "Fixed")
        st.markdown(f"**Final Taxable Income:** ₹{final_taxable_income:,.0f}")

    # Tax Comparison Cards for the two FYs
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.subheader("📅 FY25-26 (Current)")
            st.metric("Base Tax", f"₹{current_base_tax:,.0f}")
            st.metric("Health & Education Cess", f"₹{current_cess:,.0f}")
            st.markdown(f"**Total Tax:** ₹{current_total_tax:,.0f}")
            # Display savings or extra liability
            if tax_difference < 0:
                st.markdown(f"<div class='positive'>▼ Saving ₹{abs(tax_difference):,.0f}</div>", unsafe_allow_html=True)
            elif tax_difference > 0:
                st.markdown(f"<div class='negative'>▲ Increase ₹{tax_difference:,.0f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div>No change</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    with col2:
        with st.container():
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.subheader("📅 FY24-25 (Previous)")
            st.metric("Base Tax", f"₹{previous_base_tax:,.0f}")
            st.metric("Health & Education Cess", f"₹{previous_cess:,.0f}")
            st.markdown(f"**Total Tax:** ₹{previous_total_tax:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Visual Comparison
    st.markdown("---")
    st.subheader("📈 Year-over-Year Comparison")
    tax_df = pd.DataFrame({
        "Financial Year": ["FY24-25", "FY25-26"],
        "Total Tax": [previous_total_tax, current_total_tax]
    }).set_index("Financial Year")
    st.bar_chart(tax_df, use_container_width=True)

    # ------------------------------
    # Generate Report Section
    # ------------------------------
    # Prepare report data using current regime values
    report_data = {
        'Income Details': {
            'Total Income': total_income,
            'Basic Salary': basic_salary,
            'NPS Deduction': nps_deduction,
            'Standard Deduction': standard_deduction,
            'Taxable Income': final_taxable_income
        },
        'Tax Calculation': {
            'Base Tax': current_base_tax,
            'Health & Education Cess': current_cess,
            'Total Tax': current_total_tax,
            'Monthly Tax': current_total_tax / 12
        }
    }
    report = generate_report(report_data)
    st.download_button(
        "Download Tax Report 📑",
        report,
        "tax_report.txt",
        "text/plain"
    )


# ------------------------------
# Footer Section
# ------------------------------
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        Made with ❤️ by Mukhiyaa<br>
        Version 1.0 • Updated Feb'25
    </div>
    """, 
    unsafe_allow_html=True
)
