import pandas as pd

# Load the CSV file
df = pd.read_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/All.csv')

# Drop duplicate values based on the 'Provinica' column
df = df.drop_duplicates(subset=['provincia'])

df.to_csv('/Users/tomasmendietarios/Library/Mobile Documents/com~apple~CloudDocs/I.T.B.A/MRI/Data/Loc.csv', index=False)

