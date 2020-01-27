import requests as req
import pandas as pd

url = 'http://www.astrobin.com/api/v1/userprofile/?user__contains=observatory&limit=10000&api_key=d73dc4194b889db7b47a649a329fb82c64e754f0&api_secret=ae57b5743a1aa9d04836e3353246dc56d57cc124'

res = req.get(url)

json_res = res.json()

json_res_final = json_res['objects']
type(json_res_final)
df = pd.DataFrame.from_records(json_res_final)

df[df.about.str.contains('observatory')]['about'].values[0]
