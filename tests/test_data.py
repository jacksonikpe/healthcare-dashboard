"""Quick independent dataset check: python tests/test_data.py"""
from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parents[1]/'data'/'Patients_Data_Cleaned.csv'
df=pd.read_csv(p)
assert len(df)==237425, f'Unexpected record count: {len(df)}'
for col, expected in {'HadHeartAttack':13188,'HadSkinCancer':20240,'HadStroke':9920,'HadCOPD':18575}.items():
    actual=int((df[col]==1).sum())
    assert actual==expected, f'{col}: expected {expected}, got {actual}'
print('PASS: row count and all four condition counts match the supplied cleaned CSV')
