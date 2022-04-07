from re import A
import pandas as pd

#data = pd.read_csv("dataset.csv").head(1)

df = pd.DataFrame({"A": [1],"B":[5]})
print(df)
df['A'][0] = 2
print(df)

a = [1,2,3]


