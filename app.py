
import streamlit as st
import pandas as pd
import math
from io import BytesIO

# ------------------------- Ρυθμίσεις -------------------------
APP_ENABLED = True
APP_PASSWORD = "2025_KATANOMI_MATHITON"
COPYRIGHT_NOTICE = "© 2025 - Σύστημα Κατανομής Μαθητών Α’ Δημοτικού – Πνευματικά Δικαιώματα Διατηρούνται – Παναγιώτα Γιαννίτσαρου"

if not APP_ENABLED:
    st.error("⛔ Η εφαρμογή είναι προσωρινά απενεργοποιημένη από τον διαχειριστή.")
    st.stop()

st.set_page_config(page_title="Κατανομή Μαθητών", layout="centered")
st.title("🔐 Σύστημα Κατανομής Μαθητών")

password = st.text_input("Εισάγετε τον κωδικό πρόσβασης:", type="password")
if password != APP_PASSWORD:
    st.warning("Παρακαλώ εισάγετε τον σωστό κωδικό για να συνεχίσετε.")
    st.stop()

# ------------------------- Εφαρμογή -------------------------
st.subheader("1️⃣ Εισαγωγή Δεδομένων Μαθητών")
uploaded_file = st.file_uploader("📥 Επιλέξτε αρχείο Excel (.xlsx)", type="xlsx")
df = None
sections = []

def calculate_sections_and_initialize(df, max_students_per_class=25):
    total_students = len(df)
    num_sections = math.ceil(total_students / max_students_per_class)
    return [f"Τμήμα {i + 1}" for i in range(num_sections)]

def generate_statistics_table(df):
    relevant_columns = {
        'ΦΥΛΟ': lambda x: (x == 'Α').sum(),
        'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ': lambda x: (x == 'Ν').sum(),
        'ΖΩΗΡΟΣ': lambda x: (x == 'Ν').sum(),
        'ΙΔΙΑΙΤΕΡΟΤΗΤΑ': lambda x: (x == 'Ν').sum(),
        'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ': lambda x: (x == 'Ν').sum(),
        'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ': lambda x: (x == 'Ν').sum(),
        'ΟΝΟΜΑΤΕΠΩΝΥΜΟ': 'count'
    }

    stats = df.groupby('ΤΜΗΜΑ').agg(relevant_columns).rename(columns={
        'ΦΥΛΟ': 'Αγόρια (Α)',
        'ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ': 'Παιδιά Εκπαιδευτικών',
        'ΖΩΗΡΟΣ': 'Ζωηροί',
        'ΙΔΙΑΙΤΕΡΟΤΗΤΑ': 'Ιδιαιτερότητα',
        'ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ': 'Καλή Γν. Ελληνικών',
        'ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ': 'Μαθησιακά Ικανοί',
        'ΟΝΟΜΑΤΕΠΩΝΥΜΟ': 'Σύνολο'
    })

    stats['Κορίτσια (Κ)'] = stats['Σύνολο'] - stats['Αγόρια (Α)']
    stats = stats.reset_index()
    columns_order = [
        'ΤΜΗΜΑ',
        'Αγόρια (Α)',
        'Κορίτσια (Κ)',
        'Παιδιά Εκπαιδευτικών',
        'Ζωηροί',
        'Ιδιαιτερότητα',
        'Καλή Γν. Ελληνικών',
        'Μαθησιακά Ικανοί',
        'Σύνολο'
    ]
    stats = stats[columns_order]
    return stats

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Το αρχείο φορτώθηκε επιτυχώς!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"❌ Σφάλμα κατά τη φόρτωση: {e}")

if st.button("2️⃣ Εκτέλεση Κατανομής Μαθητών"):
    if df is not None:
        sections = calculate_sections_and_initialize(df)
        df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = [sections[i % len(sections)] for i in range(len(df))]
        st.success("✅ Ολοκληρώθηκε η προσωρινή κατανομή.")
        st.dataframe(df[['ΟΝΟΜΑΤΕΠΩΝΥΜΟ', 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']])
    else:
        st.warning("⚠️ Πρώτα πρέπει να ανεβάσετε αρχείο Excel.")

if st.button("3️⃣ Εξαγωγή Αποτελέσματος σε Excel"):
    if df is not None and 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ' in df.columns:
        df['ΤΜΗΜΑ'] = df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ']
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        st.download_button(
            label="📤 Κατέβασμα Αποτελέσματος",
            data=output,
            file_name="katanomi_apotelesma.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ Δεν υπάρχουν δεδομένα για εξαγωγή.")

if st.button("4️⃣ Προβολή Στατιστικών Κατανομής"):
    if df is not None and 'ΤΜΗΜΑ' in df.columns:
        st.subheader("📊 Ενιαίος Πίνακας Στατιστικών Ανά Τμήμα")
        stats_df = generate_statistics_table(df)
        st.dataframe(stats_df)

        output_stats = BytesIO()
        stats_df.to_excel(output_stats, index=False)
        output_stats.seek(0)
        st.download_button(
            label="📥 Κατέβασμα Πίνακα Στατιστικών",
            data=output_stats,
            file_name="statistika_tmimaton.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ Δεν έχει πραγματοποιηθεί ακόμα η πλήρης κατανομή.")

st.markdown("---")
st.markdown(f"<div style='text-align:center; font-size: 12px; color: gray;'>{COPYRIGHT_NOTICE}</div>", unsafe_allow_html=True)
