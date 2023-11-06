import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import os
import logging

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)

# Ajout d'un log avant le chargement du fichier de données
logging.debug('Début du chargement du fichier de données.')

try:
# Chargez les indicateurs d'éléments
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

# Ajout d'un log après le chargement du fichier de données
logging.debug('Fin du chargement du fichier de données.')

# Initialisez l'application avec le style Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Ajoutez les lignes ici
print(type(app))  # pour vérifier le type de 'app'
print(app.server)  # pour vérifier que 'app.server' existe

server = app.server

# Définissez les noms d'éléments et les entrées par défaut
element_names = ['Al',  'C', 'Co', 'Cr', 'Cu', 
                 'Fe', 'Hf', 'Mg', 'Mn', 'Mo', 
                 'Nb', 'Ni', 'Re', 'Ru', 'Si', 
                 'Ta', 'Ti', 'V', 'W', 'Zr']
default_compositions = [0] * len(element_names)

# Définissez les valeurs médianes des impacts
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

# Définir l'interface utilisateur
app.layout = html.Div([
    html.H1('Alloy Societal Impact Calculator'),  # Titre de l'application
    
    # Nouvelle division pour la section des entrées
    html.Div([
        html.H2('Input - Alloy composition'),  # Titre pour la section d'entrée
        html.P('Enter element concentration in wt.%'),  # Instruction pour l'utilisateur

        # Le reste de votre code pour les entrées va ici...
        dbc.Row([  # Ligne pour le groupe d'entrées 1
            dbc.Col([  # Colonne pour chaque entrée
                dbc.Label(name, html_for=name),  # Étiquette pour l'entrée
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),  # Entrée elle-même
                dbc.Tooltip(  # Infobulle d'aide pour chaque entrée
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[:5], default_compositions[:5])
        ], align="start"),
        dbc.Row([  # Ligne pour le groupe d'entrées 2
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[5:10], default_compositions[5:10])
        ], align="start"),
        dbc.Row([  # Ligne pour le groupe d'entrées 3
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[10:15], default_compositions[10:15])
        ], align="start"),
        dbc.Row([  # Ligne pour le groupe d'entrées 4
            dbc.Col([
                dbc.Label(name, html_for=name),
                dbc.Input(type='number', id=name, value=default, min=0, max=100, step=0.01),
                dbc.Tooltip(
                    'Must range between 0 and 100',
                    target=name
                )
            ]) for name, default in zip(element_names[15:], default_compositions[15:])
        ], align="start"),

        html.Button('Réinitialiser', id='reset', n_clicks=0),  # Bouton de réinitialisation
        dbc.Progress(id="progress", value=100, color="success", style={'margin-top': '20px'}),  # Barre de progression
        html.Button('Compute impacts', id='compute', n_clicks=0, style={'margin-top': '20px'}),  # Bouton pour calculer les impacts
    ], className='input-section'),  # Nous avons ajouté une classe CSS pour pouvoir styliser cette section séparément si nécessaire
    
    # Nouvelle division pour la section des résultats
    html.Div([
        html.H2('Societal impact of your alloy compared to median values calculated for 340 published HEAs'),  # Titre pour la section des résultats
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
    ], className='results-section')  # Nous avons ajouté une classe CSS pour pouvoir styliser cette section séparément si nécessaire
], className='app-container', style={'width': '80%', 'height': '80%', 'margin': '0 auto'})  # Nous avons ajouté une classe CSS pour pouvoir styliser le conteneur principal si nécessaire

# Gestionnaire de rappel pour réinitialiser les entrées
@app.callback(
    [Output(name, 'value') for name in element_names],
    [Input('reset', 'n_clicks')]
)
def reset_inputs(n):
    return default_compositions

# Gestionnaire de rappel pour mettre à jour les résultats
@app.callback(
    Output('results', 'data'),
    Output('results', 'columns'),
    [Input('compute', 'n_clicks')],
    [State(name, 'value') for name in element_names]
)
def update_impacts(n, *compositions):
    compositions = [comp / 100 for comp in compositions]  # Convert percentages to fractions
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
    debug = False if os.environ.get('PORT') else True  # Définissez debug sur False si PORT est défini (c'est-à-dire sur Heroku)
    port = int(os.environ.get('PORT', 8050))  # Utilisez le port défini par Heroku ou 8050 par défaut
    app.run_server(debug=debug, host='0.0.0.0', port=port)

