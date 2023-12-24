import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import os
import logging

# 日志配置
logging.basicConfig(level=logging.DEBUG)

# 在載入資料檔案之前新增日誌
logging.debug('Début du chargement du fichier de données.')

try:
# 載入元素指標
    element_indicators = pd.read_csv('gen_element_imputed.csv', sep=',')
    element_indicators = element_indicators.set_index('elements')
    element_indicators = element_indicators[['Mass price (USD/kg)',
                                         'Supply risk',
                                         'Normalized vulnerability to supply restriction',
                                         'Embodied energy (MJ/kg)',
                                         'Rock to metal ratio (kg/kg)',
                                         'Water usage (l/kg)',
                                         'Human health damage',
                                         'Human rights violation',
                                         'Labor rights disregard']]
    element_indicators.rename(columns={'Human rights violation': 'Human rights pressure'}, inplace=True)
    element_indicators.rename(columns={'Labor rights disregard': 'Labor rights pressure'}, inplace=True)

except Exception as e:
    logging.error('Erreur lors du chargement du fichier de données : %s', e)

# 在載入資料檔案之後新增日誌
logging.debug('Fin du chargement du fichier de données.')

# 使用Bootstrap樣式初始化應用程式。
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# 在此處新增以下行
print(type(app))  # 以檢查 'app' 的類型
print(app.server)  # 以檢查 'app.server' 是否存在

server = app.server

# 定義元素名稱和預設輸入。
element_names = ['Al',  'C', 'Co', 'Cr', 'Cu', 
                 'Fe', 'Hf', 'Mg', 'Mn', 'Mo', 
                 'Nb', 'Ni', 'Re', 'Ru', 'Si', 
                 'Ta', 'Ti', 'V', 'W', 'Zr']
default_compositions = [0] * len(element_names)

# 設定影響的中位數值。
median_values = {
    'Mass price (USD/kg)': 19.3,
    'Supply risk': 0.316,
    'Normalized vulnerability to supply restriction': 0.115,
    'Embodied energy (MJ/kg)': 333,
    'Water usage (l/kg)': 355,
    'Rock to metal ratio (kg/kg)': 603,
    'Human health damage': 23,
    'Human rights pressure': 31,
    'Labor rights pressure': 41,
}

# 定義使用者介面 (UI)。
app.layout = html.Div([
    html.H1('Alloy Societal Impact Calculator'),  # 應用程式標題

    html.Div([
        html.P(
            '''
            The Alloy Societal Impact Calculator, 
            crafted by Professors Stephane Gorsse from the University of Bordeaux and Matthew 
            Barnett from Deakin University, provides a user-friendly tool for assessing the 
            societal impacts of various alloys. By entering the composition of your alloy, 
            you can instantly calculate its societal implications and benchmark these against 
            the median values established from over 300 published high-entropy alloys (HEAs). 
            This intuitive platform is designed to streamline the complex evaluation of alloy 
            impacts for both professionals and enthusiasts alike.
            '''
        )
    ], style={"margin": 20, "margin-top": 50}),
    
    # 新的入口部門分區
    html.Div([
        html.H2('Input - Alloy composition'),  # 入口部門標題
        html.P('Enter element concentration in wt.%'),  # 使用者指南

        # 您的輸入部分程式碼的其餘部分在此處...
        dbc.Row([  # 輸入組1的行
            dbc.Col([  # 每個輸入的欄位
                dbc.Label(name, html_for=name),  # 輸入的標籤
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),  # 輸入內容
                dbc.Tooltip(  # 每個輸入的說明提示
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[:5], default_compositions[:5])
        ], align="start"),
        dbc.Row([  # 輸入組2的列
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[5:10], default_compositions[5:10])
        ], align="start"),
        dbc.Row([  # 輸入組3的列
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[10:15], default_compositions[10:15])
        ], align="start"),
        dbc.Row([  # 輸入組4的列
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[15:], default_compositions[15:])
        ], align="start"),

        html.Button('Réinitialiser', id='reset', n_clicks=0),  # 重設按鈕
        dbc.Progress(id="progress", value=100, color="success", style={'margin-top': '20px'}),  # 進度條
        html.Button('Compute impacts', id='compute', n_clicks=0, style={'margin-top': '20px'}),  # 計算影響的按鈕
    ], className='input-section'),  # 如果需要，我們已添加了一個CSS類來單獨設計此部分
    
    html.Div([
        html.P("The calculated results include : "),
        html.P(
            '''
            1. Raw Material Price (MP): A proxy for the cost of materials, critical in determining an alloy's production cost.
            '''
        ),
        html.P(
            '''
            2. Supply Risk (SR): Evaluates the reliability of a metal's supply and potential constraints due to geopolitical and other factors.
            '''
        ),
        html.P(
            '''
            3. Normalized Vulnerability to Supply Restriction (NVSR): Measures an element's economic significance and its normalized risk of supply interruption.
            '''
        ),
        html.P(
            '''
            4. Embodied Energy (EE): The total energy consumed in producing a metal, reflecting its environmental impact and resource demand.
            '''
        ),
        html.P(
            '''
            5. Water Use (WU): Indicates the amount of water used in mining, affecting resource sustainability and ecosystem health.
            '''
        ),
        html.P(
            '''
            6. Rock-to-Metal Ratio (RMR): Represents the land use intensity of mining, with higher ratios indicating more environmental disruption.
            '''
        ),
        html.P(
            '''
            7. Human Health Damage (HHD): Aggregates the impact of metal production on human health across various environmental factors.
            '''
        ),
        html.P(
            '''
            8. Human Rights Pressure (HRP): Assesses the respect for human rights in extraction regions, impacting workers' well-being.
            '''
        ),
        html.P(
            '''
            9. Labor Rights Pressure (LRP): Gauges the adherence to labor rights in extraction regions, affecting workers' conditions and equity.
            '''
        )
    ], style={"margin": 20, "margin-top": 50, "margin-buttom": 50}),

    # 結果部分的新分區
    html.Div([
        html.H2('Societal impact of your alloy compared to median values calculated for 340 published HEAs'),
        # 結果部分的標題
        dash_table.DataTable(
            id='results', 
            data=[], 
            columns=[{"name": i, "id": i} for i in ['Impact Category', 'Value', 'Unit']],
            style_cell_conditional=[
                {'if': {'column_id': 'Impact Category'},
                'textAlign': 'left'}],
            style_data_conditional=[
                {'if': {'column_id': 'Impact Category'},
                'width': '50%'}]
        )
    ], className='results-section'),  # 如果需要，我們已添加一個CSS類別，以便可以單獨設計此部分。
], className='app-container', style={'width': '80%', 'height': '80%', 'margin': '0 auto'})
    # 如果需要，我們已添加一個CSS類別，以便可以單獨設計主容器。"

# 重設輸入的回調管理器
@app.callback(
    [Output(name, 'value') for name in element_names],
    [Input('reset', 'n_clicks')]
)
def reset_inputs(n):
    return default_compositions

# 更新結果的回調管理器
@app.callback(
    Output('results', 'data'),
    Output('results', 'columns'),
    [Input('compute', 'n_clicks')],
    [State(name, 'value') for name in element_names]
)
def update_impacts(n, *compositions):
    compositions = [comp / 100 for comp in compositions]  # 將百分比轉換為分數
    if n == 0:
        return [], [{"name": i, "id": i} for i in ['Impact Category', 'Value', 'Unit']]
    if round(sum(compositions), 2) != 1:
        return [{'Impact Category': 'Erreur', 'Value': 'La somme des pourcentages doit être 100', 'Unit': ''}], \
               [{"name": i, "id": i} for i in ['Impact Category', 'Value', 'Unit']]
    alloy_compo_mass = pd.DataFrame([compositions], columns=element_names)
    impacts = pd.DataFrame(columns=element_indicators.columns)
    impacts['Mass price (USD/kg)'] = alloy_compo_mass.dot(element_indicators['Mass price (USD/kg)'])
    result = (1-alloy_compo_mass*element_indicators[['Supply risk']].T.values)
    impacts['Supply risk'] = 1-result.prod(axis=1)
    impacts['Normalized vulnerability to supply restriction'] = alloy_compo_mass.dot(element_indicators['Normalized vulnerability to supply restriction'])
    impacts['Embodied energy (MJ/kg)'] = alloy_compo_mass.dot(element_indicators['Embodied energy (MJ/kg)'])
    impacts['Water usage (l/kg)'] = alloy_compo_mass.dot(element_indicators['Water usage (l/kg)'])
    impacts['Rock to metal ratio (kg/kg)'] = alloy_compo_mass.dot(element_indicators['Rock to metal ratio (kg/kg)'])
    impacts['Human health damage'] = alloy_compo_mass.dot(element_indicators['Human health damage'])
    impacts['Human rights pressure'] = alloy_compo_mass.dot(element_indicators['Human rights pressure'])
    impacts['Labor rights pressure'] = alloy_compo_mass.dot(element_indicators['Labor rights pressure'])

    precision = {'Mass price (USD/kg)': 1, 'Supply risk': 3, 'Normalized vulnerability to supply restriction': 3,
                 'Embodied energy (MJ/kg)': 0, 'Water usage (l/kg)': 0, 'Rock to metal ratio (kg/kg)': 0, 
                 'Human health damage': 0, 'Human rights pressure': 0, 'Labor rights pressure': 0}

    impacts_dict = impacts.transpose().reset_index().rename(columns={'index': 'Impact Category', 0: 'Value'}).to_dict('records')
    for record in impacts_dict:
        record['Median value'] = median_values[record['Impact Category']]
        record['Value'] = "{:.{}f}".format(record['Value'], precision[record['Impact Category']])

    return impacts_dict, [{"name": i, "id": i} for i in ['Impact Category', 'Value', 'Median value']]


@app.callback(
    Output('progress', 'value'),
    Output('progress', 'color'),
    [Input(name, 'value') for name in element_names]
)
def update_progress(*compositions):
    total = round(sum(compositions), 2)
    if total == 100:
        color = "success"
    elif total < 100:
        color = "warning"
    else:
        color = "danger"
    return total, color  

if __name__ == '__main__':
    debug = False if os.environ.get('PORT') else True  # 如果PORT已定義（即在Heroku上），請將debug設置為False。
    port = int(os.environ.get('PORT', 8050))  # 使用Heroku定義的端口或默認的8050端口。
    app.run_server(debug=debug, host='0.0.0.0', port=port)

