import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import io
import base64
import datetime
import dash_bootstrap_components as dbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN])#, suppress_callback_exceptions=True)

server = app.server

# Define the layout of the app
app.layout = html.Div(children = 
[
    #html.Div([dbc.Label("Clevered Dashboard", className="text-center fw-bold text-decoration-underline", style={'color': 'black'})]),
    html.H1("Clevered Dashboard", className="text-center fw-bold text-decoration-underline", style={'color': 'black'}),

    html.A(dbc.Button('Refresh', color="warning"),href='/', className="d-md-flex justify-content-md-end"),

    html.Div(id='upload-container', className='centered-container', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select .csv / .xlsx File')], style={'color': 'black'}),
                style={
                    'width': '50%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px auto',  # Center horizontally
                },
                multiple=False,
            ),
        ]),
    
    html.Div([dbc.Select(id='month-dropdown',options=[
                {'label': 'January', 'value': '01'},
                {'label': 'February', 'value': '02'},
                {'label': 'March', 'value': '03'},
                {'label': 'April', 'value': '04'},
                {'label': 'May', 'value': '05'},
                {'label': 'June', 'value': '06'},
                {'label': 'July', 'value': '07'},
                {'label': 'August', 'value': '08'},
                {'label': 'September', 'value': '09'},
                {'label': 'October', 'value': '10'},
                {'label': 'November', 'value': '11'},
                {'label': 'December', 'value': '12'},
            ],
            placeholder='Select a month...',
            style={'width': '90%', 'margin': '15px'},
            className="px-2 border"# bg-white rounded-pill"
        ),
        
        dbc.Select(id='name-dropdown',placeholder='Select a person...',style={'width': '90%', 'margin': '15px'},
            className="px-2 bg-white border"# rounded-pill"
        ),
    ], style={'display': 'flex'}), 

    html.Div([html.Div([dbc.Input(id='manual-search-input', type='text', placeholder='Enter a name to get details...', style={'width': '33vw'}), #30% of viewport width
                         dbc.ButtonGroup([dbc.Button('Search', id='manual-search-button', n_clicks=0, className = "text-center", color = "success"),
                                          dbc.Button('Clear', id = 'clear-button', n_clicks = 0, className = "text-center", color = "danger")], style = {'margin-right': '30px'})],
                         style = {'display':'flex'}),
              html.Div([dbc.Input(id='sender_password_input', type='password', placeholder='Enter your password...', style={'width': '36vw'}), 
                        dbc.Button('Send Mail', id = 'send_info_mail', n_clicks = 0, color="warning", className = 'text-center')],
                        style = {'display':'flex'}),#, 'margin': '15px'}),
             ],style = {'display':'flex', 'margin': '15px'}),
             
    # html.Div([dbc.Input(id='manual-search-input', type='text', placeholder='Enter a name to get details...', style={'width': '30vw' }), #30% of viewport width
    #                      dbc.ButtonGroup([dbc.Button('Search', id='manual-search-button', n_clicks=0, className = "text-center", color = "success"),
    #                                       dbc.Button('Clear', id = 'clear-button', n_clicks = 0, className = "text-center", color = "danger")])],
    #                      style = {'display':'flex'}),

    html.Div(id='output-columns'),
    
    html.Div(id='output-person-info', style={'color': 'black'}),
    
    html.Div(id='current-month-info', style={'color': 'black'}),#, className = 'text-dark'),  

    # html.Div([
    #     html.H2("Current Month Analysis", className="text-center fw-bold"),# fst-italic text-decoration-line-through"),

    #     html.Div([html.P('Birthdays in this month', className = "fst-italic fw-bold", style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'}),
    #               html.P('Anniversaries in this month', className = "fst-italic fw-bold", style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'})], 
    #               style={'display': 'flex', 'justify-content': 'center'}),
        
    #     html.Div(id='current-month-info', className = 'text-dark')  
    # ]),
  
    # html.Div([dbc.Input(id='sender_password_input', type='password', placeholder='Enter your password...', style={'width': '30vw'}), 
    #           dbc.Button('Send Mail', id = 'send_info_mail', n_clicks = 0, color="warning", className = 'text-center')],
    #          style = {'display':'flex'}),#, 'margin': '15px'}),
    
    html.Div(id='current-month-bday-anni-info', className = 'text-wrap'), #to send bday anni info
 
],style={
        'background': 'linear-gradient(360deg, #FF5733, #FFC300)',  
        'height': '200vh',  
        'color': 'white',  
        'padding': '30px',
    })


# Function to get current month
def get_current_month():
    now = datetime.datetime.now()
    return now.strftime('%m')

#Function to get current date
def get_current_date():
    now = datetime.datetime.now()
    return now.strftime('%d')

def read_file(contents, filename):
    if contents is None:
        return ''
    content_type, content_string = contents.split(',')
    file_extension = filename.split('.')[-1].lower()

    #print(file_extension)
    if file_extension == 'csv':
        decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
        df = pd.read_csv(decoded, encoding = 'utf-8')

    elif file_extension == 'xlsx':
        decoded = io.BytesIO(base64.b64decode(content_string))
        df = pd.read_excel(decoded, engine='openpyxl')

    else:
        raise ValueError(f"Unsupported File Format: {file_extension}")

    
    df['date of birth'] = pd.to_datetime(df['date of birth'])
    df['date of joining'] = pd.to_datetime(df['date of joining'])

    return df                         

# Function to send an email
def send_email(sender_email, password, recv_email, subject, message):

    try:
        # Creating a message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recv_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server1 = smtplib.SMTP("smtp.gmail.com", 587)#("smtp.clevered.com", 587) #
        server1.starttls()
        server1.login(sender_email, password)
        print("login successful")

        server1.sendmail(sender_email, recv_email, msg.as_string())
        server1.quit()

        return "Email sent successfully"
    except Exception as e:
        return f"Error: Unable to send email! - {str(e)}"
    
def email_body(bdays_today, annis_today):   
    body = ''  
    if bdays_today is not None and not bdays_today.empty:   
        body += "The following employees have their Birthdays today: \n"  
        for _, row in bdays_today.iterrows():
            today_name_b = row['name']
            today_email_b = row['email ID']
            body += f"- {today_name_b} : {today_email_b}\n"

    if annis_today is not None and not annis_today.empty:  
        body += "\nThe following employees have their Work Anniversaries today: \n"
        for _, row in annis_today.iterrows():
            today_name_a = row['name']
            today_email_a = row['email ID']
            body += f"- {today_name_a} : {today_email_a}\n"
    return body

@app.callback(
    Output('current-month-bday-anni-info', 'children'), 
    Input('upload-data', 'contents'),
    Input('send_info_mail', 'n_clicks'),
    State('sender_password_input', 'value'),
    State('upload-data', 'filename')
)
def send_bday_anni_info(contents, n_clicks, password, filename):
    if n_clicks > 0 and contents is not None:

        df = read_file(contents, filename)
        
        sender_email = 'samreen@clevered.com' #'arya.verma.923@gmail.com'#
        recipient_email = 'samreen@clevered.com'#'arya.verma2021@vitstudent.ac.in'        

        current_month = get_current_month()
        current_date = get_current_date()
        birth_month_filter = (df['date of birth'].dt.strftime('%m') == current_month) & (df['date of birth'].dt.strftime('%d') == current_date)
        bdays_today = df[birth_month_filter][['name', 'email ID']] 

        anni_month_filter = (df['date of joining'].dt.strftime('%m') == current_month) & (df['date of joining'].dt.strftime('%d') == current_date)
        annis_today = df[anni_month_filter][['name', 'email ID']] 

        message = email_body(bdays_today, annis_today)

        try:
            send_email(sender_email, password, recipient_email, "Birthdays and Work Anniversaries today.", message)
            return dbc.Alert("Email sent successfully!", color = 'success', className = 'opacity-75')
        except Exception as e:
            return f'Email could not be sent: {str(e)}'
    else:
        return ''  # Initial state
        

#Define callback to display persons with DOB or DOJ in the current month
@app.callback(
    Output('current-month-info', 'children'), 
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
) 
   
def display_current_month_info(contents, filename):
    if contents is None:
        return ''

    df = read_file(contents, filename)
    
    current_month = get_current_month()
    birth_month_filter = df['date of birth'].dt.strftime('%m') == current_month  
    joining_month_filter = df['date of joining'].dt.strftime('%m') == current_month

   
    birth_persons = df[birth_month_filter]
    joining_persons = df[joining_month_filter]

    # Create Bootstrap columns for DOB and DOJ
    birth_person_info_divs = []
    joining_person_info_divs = []


    for _, row in birth_persons.iterrows():
        person_name = row['name']
        person_info_div = html.Div([
            html.H5(f'Details for {person_name}:')
        ])

        bday_person_email = row['email ID']
        bday_person_dob = row['date of birth']

        person_info_div.children.append(html.P(f'Email ID: {bday_person_email}'))
        person_info_div.children.append(html.P(f'Birth date: {bday_person_dob}'))

        birth_person_info_divs.append(person_info_div)
   
    for _, row in joining_persons.iterrows():
        person_name = row['name']
        person_info_div = html.Div([
            html.H5(f'Details for {person_name}:')
        ])

        anni_person_email = row['email ID']
        anni_person_doj = row['date of joining']

        person_info_div.children.append(html.P(f'Email ID: {anni_person_email}'))
        person_info_div.children.append(html.P(f'Work Anniversary: {anni_person_doj}'))


        joining_person_info_divs.append(person_info_div)
    
    # current_month_info_div = html.Div([
    #     html.Div(birth_person_info_divs, className='col-md-6'),
    #     html.Div(joining_person_info_divs, className='col-md-6')
    # ], className='row')
    current_month_info_div = html.Div([
        html.H2("Current Month Analysis", className="text-center fw-bold"),# fst-italic text-decoration-line-through"),

        html.Div([
            dbc.Row(
                    [
                        dbc.Col(html.Div([html.H4('Birthdays in this month', className = "fst-italic fw-bold"),#, style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'}), 
                                          html.P(birth_person_info_divs, style={'text-align': 'justify'})])), #, className='col-md-6')]),),
                        dbc.Col(html.Div([html.H4('Work Anniversaries in this month', className = "fst-italic fw-bold"),#, style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'}), 
                                          html.P(joining_person_info_divs, style={'text-align': 'justify'})])),
                    ]
                ),
            ])])
    #     html.Div([
    #         html.Div([html.H4('Birthdays in this month', className = "fst-italic fw-bold"),#, style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'}), 
    #                   html.P(birth_person_info_divs)]), #, className='col-md-6')]),
    #         html.Div([html.H4('Work Anniversaries in this month', className = "fst-italic fw-bold"),#, style={'width': '50%', 'margin': 'auto', 'text-align': 'center', 'font-size': '20px'}), 
    #                   html.P(joining_person_info_divs)])], #, className='col-md-6')])], 
    #         style={'display': 'flex'})#, 'justify-content': 'center'})
    # ])

    
    return current_month_info_div

# Define combined callback to handle person info display, name dropdown updates, and manual search
@app.callback(
    [
        Output('output-person-info', 'children'),
        Output('name-dropdown', 'options'),
        Output('manual-search-input', 'value'),
    ],
    [
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),        
        Input('name-dropdown', 'value'),
        Input('month-dropdown', 'value'),
        Input('manual-search-button', 'n_clicks'),
        Input('clear-button', 'n_clicks'), 
        State('manual-search-input', 'value'),
    ]
)
def update_person_info(contents, filename, selected_name, selected_month, search_clicks, clear_clicks, manual_search_name):
    if contents is None:
        return '', [], manual_search_name

    df = read_file(contents, filename)
    
    output_person_info = ''
    name_dropdown_options = []

    if selected_month:
        current_month = selected_month
        birth_month_filter = df['date of birth'].dt.strftime('%m') == current_month
        joining_month_filter = df['date of joining'].dt.strftime('%m') == current_month

        filtered_persons = df[birth_month_filter | joining_month_filter]

        person_info_divs = []

        for _, row in filtered_persons.iterrows():
            person_name = row['name']
            person_info_div = html.Div([
                html.H4(f'Details for {person_name}:')
            ])

            for column_name, value in row.items():
                person_info_div.children.append(html.P(f'{column_name}: {value}'))

            person_info_divs.append(person_info_div)
            name_dropdown_options.append({'label': person_name, 'value': person_name})
    
    if selected_name:
        for person_info_div in person_info_divs:
            if person_info_div.children[0].children == f'Details for {selected_name}:':
                output_person_info = person_info_div
                break
    person_info = pd.DataFrame() #

    if search_clicks is not None and search_clicks > 0 and manual_search_name:
        manual_search_name_components = manual_search_name.split(' ')
        manual_search_name_first = manual_search_name_components[0].lower()
        df['name_lower'] = df['name'].str.lower()

        person_info = df[df['name_lower'].str.startswith(manual_search_name_first)].copy() ## to create a copy of the original dataframe
        person_info.drop('name_lower', axis = 1, inplace = True) #inplace true for dropping col from the same data frame and not making a copy of the dataframe with a col dropped. axis = 1 to delete col and not row(axis=0)
        
    if not person_info.empty:
            person_info_dict = person_info.iloc[0].to_dict()
            output_person_info = html.Div([
                html.H4(f'Details for {manual_search_name}:')
            ])

            # Iterate over all columns in the row and add them to the div
            for column_name, value in person_info_dict.items():
                output_person_info.children.append(html.P(f'{column_name}: {value}'))

            name_dropdown_options.append({'label': manual_search_name, 'value': manual_search_name})

    if clear_clicks is not None and clear_clicks >0:
            manual_search_name = ''
    return output_person_info, name_dropdown_options, manual_search_name

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8067)