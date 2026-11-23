import pandas as pd

# Load your CSV file
df = pd.read_csv('responses.csv')

# Clean column names
df.columns = df.columns.str.strip()

# Print available columns for verification
print(df.columns.tolist())

# Example access to the column after cleaning
for index, row in df.iterrows():
    if 'When do you discard your clothes? select maximum 2 priority wise. Please be honest' in df.columns:
        print(f"I said: {row['When do you discard your clothes? select maximum 2 priority wise. Please be honest']}.")
    else:
        print("Column not found.")
