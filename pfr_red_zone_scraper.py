import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

def suffix_name_remove(full_name):
    return ' '.join(full_name.split()[0:2])

pd.set_option('display.max_columns', None)
# we will only be extracting red zone RECEIVING stats
redzone_url = 'https://www.pro-football-reference.com/years/{year}/redzone-receiving.htm'


start_year = 2013
end_year = 2021

redzone_df = pd.DataFrame()

for year in range(start_year, end_year+1):
    res = requests.get(redzone_url.format(year=year))
    soup = bs(res.content, 'html.parser')
    table = soup.find('table', {'id':'fantasy_rz'})
    df = pd.read_html(str(table))[0]
    df.columns = df.columns.droplevel(level=0)
    df = df.loc[df['Player'] != 'Player']
    df['Player'] = df['Player'].apply(lambda x: x.split('*')[0].strip())

    df['rz_targets'] = df['Tgt'].iloc[:,0]
    df['rz_receptions'] = df['Rec'].iloc[:,0]
    df['rz_catch_rate'] = df['Ctch%'].iloc[:,0]
    df['rz_rec_yards'] = df['Yds'].iloc[:,0]
    df['rz_rec_tds'] = df['TD'].iloc[:,0]
    df['rz_target_share'] = df['%Tgt'].iloc[:,0]

    df['rz10_targets'] = df['Tgt'].iloc[:,1]
    df['rz10_receptions'] = df['Rec'].iloc[:,1]
    df['rz10_catch_rate'] = df['Ctch%'].iloc[:,1]
    df['rz10_rec_yards'] = df['Yds'].iloc[:,1]
    df['rz10_rec_tds'] = df['TD'].iloc[:,1]
    df['rz10_target_share'] = df['%Tgt'].iloc[:,1]

    df = df.drop(['Tgt', 'Rec', 'Ctch%', 'Yds', 'TD', '%Tgt', 'Link'], axis=1)

    df['season'] = year
    col_name = df.columns.tolist()
    col_name.pop()
    col_name.insert(0,'season')
    df =df[col_name]

    col_arr = ['rz_catch_rate', 'rz_target_share', 'rz10_catch_rate', 'rz10_target_share']

    for each in col_arr:
        df[each] = df[each].str.rstrip('%')
        df[each] = pd.to_numeric(df[each], errors = 'coerce')

    df = df.rename({'Player':'player_name', 'Tm':'team'}, axis=1)
    df.loc[:,['player_name']] = df['player_name'].apply(suffix_name_remove)
    df['player_name'] = df['player_name'].str.lower()
    df['player_name'] = df['player_name'].str.replace('.','', regex=True)

    redzone_df = pd.concat([redzone_df, df])

redzone_df.to_csv('/Users/brandynklee/Python_Projects/fantasy_footballl_22/data/rz_receiving_compiled_2013_2021.csv', index=False)