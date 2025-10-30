#Importing the required libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

#Connecting python to Mysql database
engine = create_engine("mysql+mysqlconnector://root:root@localhost/health_data")

# PAGE CONFIG

st.set_page_config(
    page_title="Healthcare Data Insights",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Data Insights Dashboard")
st.markdown("Analyze patient admissions, doctor performance, and hospital financials interactively.")
# --------------------------
# 📊 GLOBAL SIDEBAR FILTERS
# --------------------------
st.sidebar.header("🔍 Global Filters")

# Load the entire table once (used for filtering)
main_df = pd.read_sql("SELECT * FROM patients_data;", engine)

# Convert Admit_Date to datetime
main_df["Admit_Date"] = pd.to_datetime(main_df["Admit_Date"])

# 1️⃣ Date Range Filter
min_date = main_df["Admit_Date"].min()
max_date = main_df["Admit_Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# 2️⃣ Doctor Filter
doctor_options = sorted(main_df["Doctor"].dropna().unique().tolist())
selected_doctors = st.sidebar.multiselect("Select Doctor(s)", doctor_options, default=doctor_options)

# 3️⃣ Diagnosis Filter
diagnosis_options = sorted(main_df["Diagnosis"].dropna().unique().tolist())
selected_diagnosis = st.sidebar.multiselect("Select Diagnosis", diagnosis_options, default=diagnosis_options)

# 4️⃣ Bed Type Filter
bed_options = sorted(main_df["Bed_Occupancy"].dropna().unique().tolist())
selected_beds = st.sidebar.multiselect("Select Bed Type(s)", bed_options, default=bed_options)

# ✅ Apply filters
filtered_df = main_df[
    (main_df["Admit_Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))) &
    (main_df["Doctor"].isin(selected_doctors)) &
    (main_df["Diagnosis"].isin(selected_diagnosis)) &
    (main_df["Bed_Occupancy"].isin(selected_beds))
]






# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Patient & Admission Trends",
    "💰 Financial Insights",
    "👨‍⚕️ Doctor & Performance Insights",
    "🧪 Diagnostics & Feedback",
    "🏥 Hospital Overview"
])

with tab1:
    st.markdown("### 📊 Patient & Admission Trends")
    # st.dataframe(filtered_df.head())

    # -----------------------------
    # Q1: Trends in Admission Over Time
    # -----------------------------
    df1 = (
        filtered_df.groupby("Admit_Date")["Patient_ID"]
        .count()
        .reset_index(name="Admissions")
        .sort_values("Admit_Date")
    )
    fig1 = px.line(df1, x='Admit_Date', y='Admissions', markers=True,
                title='🩺 Daily Admission Trends')
    fig1.update_traces(line_color="#2E86DE")
    st.plotly_chart(fig1, use_container_width=True)


    # -----------------------------
    # KPIs Summary
    # -----------------------------
    total_admissions = df1["Admissions"].sum()
    avg_admissions = df1["Admissions"].mean()

    col1, col2 = st.columns(2)
    col1.metric("📅 Total Admissions", f"{total_admissions:,}")
    col2.metric("📈 Avg Daily Admissions", f"{avg_admissions:.1f}")

    # -----------------------------
    # Q4: Bed Occupancy Utilization Over Time
    # -----------------------------
    filtered_df["Month"] = filtered_df["Admit_Date"].dt.to_period("M").astype(str)

    df4 = (
        filtered_df.groupby(["Month", "Bed_Occupancy"])["Patient_ID"]
        .count()
        .reset_index(name="Admissions")
    )
    fig4 = px.area(df4, x='Month', y='Admissions', color='Bed_Occupancy',
                title='🛏️ Bed Occupancy Utilization Over Time')
    st.plotly_chart(fig4, use_container_width=True)

    

    # -----------------------------
    # Q9: Bed Type vs Average Stay Duration
    # -----------------------------
    filtered_df["Admit_Date"] = pd.to_datetime(filtered_df["Admit_Date"], errors="coerce")
    filtered_df["Discharge_Date"] = pd.to_datetime(filtered_df["Discharge_Date"], errors="coerce")

    filtered_df["Stay_Length"] = (filtered_df["Discharge_Date"] - filtered_df["Admit_Date"]).dt.days


    filtered_df["Stay_Length"] = (filtered_df["Discharge_Date"] - filtered_df["Admit_Date"]).dt.days

    df9 = (
        filtered_df.groupby("Bed_Occupancy")["Stay_Length"]
        .mean()
        .reset_index(name="Avg_Stay")
    )
    fig9 = px.bar(df9, x='Bed_Occupancy', y='Avg_Stay', color='Bed_Occupancy',
                text='Avg_Stay', title='🛏️ Average Stay Duration by Bed Type')
    st.plotly_chart(fig9, use_container_width=True)


    # -----------------------------
    # Q14: Relationship Between Length of Stay and Billing Amount
    # -----------------------------
    fig14 = px.scatter(filtered_df, x='Stay_Length', y='Billing Amount', trendline='ols',
                    title='💵 Length of Stay vs Billing Amount',
                    color_discrete_sequence=['#9b59b6'])
    st.plotly_chart(fig14, use_container_width=True)

    



# ---------------------------
# TAB 2
# ---------------------------

with tab2:
    st.subheader("💰 Financial Insights Dashboard")
    st.markdown("Analyze hospital revenue, billing trends, and insurance distribution based on your filters.")

    # --- Q2: Average Billing Amount by Diagnosis ---
    df2 = (
        filtered_df.groupby("Diagnosis")["Billing Amount"]
        .mean()
        .reset_index(name="Avg_Billing")
        .sort_values("Avg_Billing", ascending=False)
    )
    fig2 = px.bar(
        df2, x='Diagnosis', y='Avg_Billing', color='Diagnosis', text='Avg_Billing',
        title='💵 Average Billing Amount by Diagnosis'
    )
    fig2.update_layout(xaxis_title="Diagnosis", yaxis_title="Average Billing Amount")
    st.plotly_chart(fig2, use_container_width=True)

    # --- Q5: Total Billing vs Insurance Coverage ---
    total_billing = filtered_df["Billing Amount"].sum()
    total_insurance = filtered_df["Health Insurance Amount"].sum()

    df5_viz = pd.DataFrame({
        'Category': ['Total Billing', 'Insurance Coverage'],
        'Amount': [total_billing, total_insurance]
    })

    fig5 = px.pie(
        df5_viz, names='Category', values='Amount', hole=0.5,
        color_discrete_sequence=['#3498db', '#2ecc71'],
        title='🏦 Total Billing vs Insurance Coverage'
    )
    st.plotly_chart(fig5, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("💰 Total Billing", f"₹{total_billing:,.0f}")
    col2.metric("🏥 Insurance Coverage", f"₹{total_insurance:,.0f}")

    # --- Q6: Diagnosis by Patient Count and Revenue ---
    df6 = (
        filtered_df.groupby("Diagnosis")
        .agg(Patient_Count=("Patient_ID", "count"),
             Total_Revenue=("Billing Amount", "sum"),
             Avg_Revenue_Per_Patient=("Billing Amount", "mean"))
        .reset_index()
        .sort_values("Total_Revenue", ascending=False)
    )
    fig6 = px.bar(
        df6, x='Diagnosis', y='Total_Revenue', color='Diagnosis',
        text='Avg_Revenue_Per_Patient', title='💵 Revenue and Patient Count by Diagnosis'
    )
    fig6.update_traces(texttemplate='Avg ₹%{text:.0f}', textposition='outside')
    st.plotly_chart(fig6, use_container_width=True)

    top_diag = df6.iloc[0]['Diagnosis'] if not df6.empty else "N/A"
    top_rev = df6.iloc[0]['Total_Revenue'] if not df6.empty else 0
    col1, col2 = st.columns(2)
    col1.metric("🏆 Top Revenue Diagnosis", top_diag)
    col2.metric("💰 Revenue Generated", f"₹{top_rev:,.0f}")

    # --- Q10: Month-wise Revenue Trend ---
    filtered_df["Month"] = filtered_df["Admit_Date"].dt.to_period("M").astype(str)
    df10 = (
        filtered_df.groupby("Month")["Billing Amount"]
        .sum()
        .reset_index(name="Total_Revenue")
    )
    fig10 = px.line(
        df10, x='Month', y='Total_Revenue', markers=True,
        title='📅 Month-wise Revenue Trend'
    )
    fig10.update_traces(line_color="#27AE60", marker_size=7)
    st.plotly_chart(fig10, use_container_width=True)

    total_revenue = df10["Total_Revenue"].sum()
    avg_monthly_revenue = df10["Total_Revenue"].mean() if not df10.empty else 0

    col1, col2 = st.columns(2)
    col1.metric("💵 Total Revenue", f"₹{total_revenue:,.0f}")
    col2.metric("📈 Avg Monthly Revenue", f"₹{avg_monthly_revenue:,.0f}")





# ---------------------------
# TAB 3
# ---------------------------

with tab3:
    st.subheader("👨‍⚕️ Doctor & Performance Insights")
    st.markdown("Evaluate doctor performance, patient load, and feedback ratings interactively.")

    # --- Q3: Doctor-wise Patient Load ---
    df3 = (
        filtered_df.groupby("Doctor")["Patient_ID"]
        .count()
        .reset_index(name="Patient_Count")
        .sort_values("Patient_Count", ascending=False)
    )
    fig3 = px.bar(
        df3, x='Doctor', y='Patient_Count', color='Doctor',
        title='👨‍⚕️ Doctor-wise Patient Load', text='Patient_Count'
    )
    st.plotly_chart(fig3, use_container_width=True)

    # KPIs
    if not df3.empty:
        top_doc = df3.iloc[0]['Doctor']
        top_load = df3.iloc[0]['Patient_Count']
        st.metric("🏆 Most Consulted Doctor", f"{top_doc} ({top_load} patients)")
    else:
        st.info("No data available for selected filters.")

    # --- Q7: Top Doctors by Revenue Generated ---
    df7 = (
        filtered_df.groupby("Doctor")["Billing Amount"]
        .sum()
        .reset_index(name="Total_Revenue")
        .sort_values("Total_Revenue", ascending=False)
    )
    fig7 = px.bar(
        df7, x='Doctor', y='Total_Revenue', color='Doctor',
        title='💰 Top Doctors by Revenue Generated', text='Total_Revenue'
    )
    st.plotly_chart(fig7, use_container_width=True)

    # KPI for top revenue doctor
    if not df7.empty:
        top_rev_doc = df7.iloc[0]['Doctor']
        top_rev_amount = df7.iloc[0]['Total_Revenue']
        col1, col2 = st.columns(2)
        col1.metric("💵 Top Earning Doctor", top_rev_doc)
        col2.metric("🏥 Revenue Generated", f"₹{top_rev_amount:,.0f}")

    # --- Q8: Doctor-wise Average Feedback Rating ---
    df8 = (
        filtered_df.groupby("Doctor")["Feedback"]
        .mean()
        .reset_index(name="Avg_Rating")
        .sort_values("Avg_Rating", ascending=False)
    )
    fig8 = px.bar(
        df8, x='Doctor', y='Avg_Rating', color='Avg_Rating',
        title='⭐ Doctor-wise Average Feedback Rating', text='Avg_Rating'
    )
    st.plotly_chart(fig8, use_container_width=True)

    if not df8.empty:
        top_feedback_doc = df8.iloc[0]['Doctor']
        top_feedback = df8.iloc[0]['Avg_Rating']
        st.metric("🌟 Highest Rated Doctor", f"{top_feedback_doc} ({top_feedback:.2f}/5)")




# ---------------------------
# TAB 4
# ---------------------------

with tab4:
    st.subheader("🧪 Diagnostics & Feedback Insights")
    st.markdown("Understand diagnostic test trends and patient satisfaction based on selected filters.")

    # --- Q4: Diagnostic Tests Frequency ---
    df4 = (
        filtered_df.groupby("Test")["Patient_ID"]
        .count()
        .reset_index(name="Test_Count")
        .sort_values("Test_Count", ascending=False)
    )
    fig4 = px.bar(
        df4.head(10),
        x='Test', y='Test_Count', color='Test_Count',
        title='🔬 Top 10 Diagnostic Tests Conducted',
        text='Test_Count'
    )
    st.plotly_chart(fig4, use_container_width=True)

    if not df4.empty:
        top_test = df4.iloc[0]['Test']
        top_count = df4.iloc[0]['Test_Count']
        st.metric("🩺 Most Frequent Test", f"{top_test} ({top_count} patients)")
    else:
        st.info("No test data available for the selected filters.")

    # --- Q5: Average Billing Amount per Test ---
    df5 = (
        filtered_df.groupby("Test")["Billing Amount"]
        .mean()
        .reset_index(name="Avg_Billing")
        .sort_values("Avg_Billing", ascending=False)
    )
    fig5 = px.bar(
        df5.head(10),
        x='Test', y='Avg_Billing', color='Avg_Billing',
        title='💰 Average Billing Amount per Test',
        text='Avg_Billing'
    )
    st.plotly_chart(fig5, use_container_width=True)

    if not df5.empty:
        top_bill_test = df5.iloc[0]['Test']
        top_avg_bill = df5.iloc[0]['Avg_Billing']
        st.metric("🏷️ Costliest Test (Avg)", f"{top_bill_test} (₹{top_avg_bill:,.0f})")

    # --- Q9: Feedback Distribution ---
    fig9 = px.histogram(
        filtered_df,
        x='Feedback',
        nbins=10,
        title='⭐ Distribution of Patient Feedback Ratings',
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig9, use_container_width=True)

    if not filtered_df.empty:
        avg_feedback = filtered_df['Feedback'].mean()
        st.metric("🌟 Overall Average Feedback", f"{avg_feedback:.2f}/5")

with tab5:
    st.subheader("🏥 Hospital Overview")
    st.markdown("A comprehensive summary of hospital performance, revenue, and patient experience.")

    # --- 1️⃣ Key KPIs ---
    total_patients = len(filtered_df["Patient_ID"].unique())
    total_revenue = filtered_df["Billing Amount"].sum()
    avg_stay = filtered_df["Length_of_Stay"].mean()
    avg_feedback = filtered_df["Feedback"].mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("👥 Total Patients", f"{total_patients}")
    kpi2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    kpi3.metric("🛌 Avg Stay Duration", f"{avg_stay:.1f} days")
    kpi4.metric("⭐ Avg Feedback", f"{avg_feedback:.2f}/5")

    st.markdown("---")

    # --- 2️⃣ Revenue by Diagnosis ---
    df_rev = (
        filtered_df.groupby("Diagnosis")["Billing Amount"]
        .sum()
        .reset_index()
        .sort_values("Billing Amount", ascending=False)
    )

    fig_rev = px.bar(
        df_rev,
        x="Diagnosis", y="Billing Amount", color="Billing Amount",
        title="🩺 Diagnosis-wise Revenue",
        text_auto=".2s"
    )
    st.plotly_chart(fig_rev, use_container_width=True)

    # --- 3️⃣ Correlation: Length of Stay vs Billing ---
    fig_corr = px.scatter(
        filtered_df,
        x="Length_of_Stay", y="Billing Amount",
        color="Diagnosis",
        trendline="ols",
        title="📈 Relationship Between Stay Duration and Billing Amount"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # --- 4️⃣ Insurance Coverage Overview ---
    df_ins = (
        filtered_df.groupby("Health Insurance Amount")["Billing Amount"]
        .sum()
        .reset_index()
    )

    fig_ins = px.pie(
        df_ins, names="Health Insurance Amount", values="Billing Amount",
        title="🧾 Insurance vs Non-Insurance Revenue Share",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_ins, use_container_width=True)

    # --- 5️⃣ Summary Insight ---
    st.markdown("### 📊 Summary Insights")
    if not filtered_df.empty:
        top_diagnosis = df_rev.iloc[0]["Diagnosis"]
        top_revenue = df_rev.iloc[0]["Billing Amount"]
        insurance_share = (
            df_ins.loc[df_ins["Health Insurance Amount"] == "Yes", "Billing Amount"].sum()
            / total_revenue * 100
            if total_revenue > 0 else 0
        )

        st.success(f"""
        - The hospital has served **{total_patients} patients** generating total revenue of **₹{total_revenue:,.0f}**.
        - The **average stay duration** is **{avg_stay:.1f} days**, with **average feedback** of **{avg_feedback:.2f}/5**.
        - {top_diagnosis}  cases contribute the highest revenue (**₹{top_revenue:,.0f}**).
        - Insurance patients account for **{insurance_share:.1f}%** of the total billing.
        """)
    else:
        st.info("No data available for selected filters.")


