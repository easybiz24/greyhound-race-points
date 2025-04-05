import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Greyhound Race Points Calculator")
st.title("Greyhound Race Points Calculator")

st.write("""
Upload a CSV file with the following columns:
- Dog Name
- PLC (Placement)
- DATE

The app will calculate cumulative points from the last 3 races per dog based on placement:
- **Race 1 (most recent)**: 1st = 18 pts, 2nd = 12 pts, 3rd = 6 pts
- **Race 2**: 1st = 12 pts, 2nd = 8 pts, 3rd = 4 pts
- **Race 3**: 1st = 6 pts, 2nd = 4 pts, 3rd = 2 pts
""")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Forward fill missing dog names
    df['Dog Name'] = df['Dog Name'].fillna(method='ffill')

    # Ensure DATE is datetime
    df['DATE'] = pd.to_datetime(df['DATE'])

    # Sort for ranking
    df = df.sort_values(by=['Dog Name', 'DATE'], ascending=[True, False])
    df['race_rank'] = df.groupby('Dog Name')['DATE'].rank(method='first', ascending=False)
    df = df[df['race_rank'] <= 3].copy()

    # Assign points
    def assign_points(row):
        plc = int(row['PLC'])
        if row['race_rank'] == 1:
            return {1: 18, 2: 12, 3: 6}.get(plc, 0)
        elif row['race_rank'] == 2:
            return {1: 12, 2: 8, 3: 4}.get(plc, 0)
        elif row['race_rank'] == 3:
            return {1: 6, 2: 4, 3: 2}.get(plc, 0)
        return 0

    df['Points'] = df.apply(assign_points, axis=1)

    # Filter dogs with exactly 3 races
    valid_dogs = df['Dog Name'].value_counts()
    valid_dogs = valid_dogs[valid_dogs == 3].index
    df = df[df['Dog Name'].isin(valid_dogs)]

    # Aggregate points
    summary = df.groupby('Dog Name')['Points'].sum().reset_index()
    summary.rename(columns={'Points': 'Cumulative Points'}, inplace=True)
    summary = summary.sort_values(by='Cumulative Points', ascending=False)

    st.subheader("Results")
    st.dataframe(summary)

    csv = summary.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "greyhound_points.csv", "text/csv")

