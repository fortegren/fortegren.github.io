from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import Flask, request, redirect, render_template
import pandas as pd
import pygsheets
import numpy as np
import codecs, json


app = Flask(__name__)
app.config['DEBUG'] = True



SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#identify spreadsheet and range of data - this is just downloaded census ACS data
SPREADSHEET_ID = '1lCboC5mhWZLhYiFqNM_Cw-ABpO3FlK5rVCQg0Y5Y968'
RANGE_NAME = 'acs!A3:LN'


def get_data():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])
    return values


# update a spreadsheet for infogram with appropriate data based
# on user input
def create_update_spreadhseet(df):
    SPREADSHEET_ID = '19DkKtsyD3YzNZg65qjQQtCH52M57RxGDe3E-M8aywmE'
    RANGE_NAME = 'Sheet1!A1:LN'

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    values = [df.columns.values.tolist()] + df.values.tolist()
    body = {'values':values}

    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, 
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


@app.route('/', methods=['GET', 'POST'])
def select_place():
    vals = get_data()
    df = pd.DataFrame(vals)

    #this is where we do things with the data
    acs_data = pd.DataFrame(columns = ['place',	'unitsho', 'unitstotal',	'age35to44',	'age45to54',	
    'age55to64',	'age65to74',	'age75to84',	'ageover85',	'ageunder35',	'edbach',	
    'edhs',	'edlessthanhs',	'edcollege',	'racehispanic',	'racenative',	'raceasian',	'raceblack',	
    'racehawaii',	'raceother',	'racewhite',	'moved1989',	'moved1990to1999',	'moved2000to2009',	
    'moved2010to2014',	'moved2015to2016',	'moved2017'])


    place_names = []

    cols = {1:'place', 38:'unitsho', 34:'unitstotal',	170:'age35to44',
    182:'age45to54',	194:'age55to64',
    206:'age65to74',	218:'age75to84',
    230:'ageover85',	158:'ageunder35',
    278:'edbach',	254:'edhs',	
    242:'edlessthanhs',	266:'edcollege',
    134:'racehispanic',	74:'racenative',
    86:'raceasian',	62:'raceblack',	
    98:'racehawaii',	110:'raceother',
    50:'racewhite',	26:'moved1989',	14:'moved1990to1999',
    2:'moved2000to2009',	314:'moved2010to2014',	
    302:'moved2015to2016',	290:'moved2017'}

    for k,v in cols.items():
        acs_data[v] = df[k]

    acs_data['units'] = (acs_data['unitsho'].astype('float') / acs_data['unitstotal'].astype('float'))*100
    cols[38] = 'units'

    if request.method == 'POST':
        metro = request.form['option']

        national_units = acs_data['units'].astype('float').mean()
        #units = acs_data['units'].loc[acs_data['place'] == metro].iloc[0]
        #units = units.iloc[0]
        
        d = {}
        
        for k,v in cols.items():
            d[v] = acs_data[v].loc[acs_data['place'] == metro].iloc[0]

        #age3544 = acs_data['age35to44'].loc[acs_data['place'] == metro].iloc[0]
        create_update_spreadhseet(acs_data.loc[acs_data['place'] == metro])

        return render_template('data.html', 
        units = d['units'], age3544 = d['age35to44'],
        age4554 = d['age45to54'], age5564 = d['age55to64'], 
        age6574 = d['age65to74'], age7584 = d['age75to84'], 
        age85 = d['ageover85'], age35 = d['ageunder35'], place = metro, option_lst=acs_data['place'],
        nation = national_units)
        
    return render_template('index.html', option_lst=acs_data['place'])






'''    
    blog_id = request.args.get('id')


    if blog_id:
        blogs = Blog.query.filter_by(id=blog_id).all()
        page_title = blogs[0].title
    else:
        page_title = "Build a Blog"
        blogs = Blog.query.order_by(Blog.date.desc()).all()

    return render_template('blog.html', blogs=blogs, page_title=page_title)
@app.route('/page', methods=["GET", "POST"])
@login_required
def chooser():
    # Option list returns a list of JSON objects 
    option_list = get_options(g.user)
    # {u'_id': ObjectId('52a347343be0b32a070e5f4f'), u'optid': u'52a347343be0b32a070e5f4e'}

    # for debugging, checks out ok
    print option_list

    # Get selected id & return it
    if request.form['submit'] == 'Select':
            optid = o.optid
            resp = 'You chose: ', optid
            return Response(resp)

    return render_template('chooser.html')

@app.route('/newpost')
def add_blog():
    page_title = "Add a New Post"
    return render_template('newpost.html', page_title=page_title)

@app.route('/validate', methods=['POST', 'GET'])
def validate_blog_form():

    blog_title = request.form['title']
    blog_body = request.form['new-blog']

    title_error=''
    blog_error = ''

    if not blog_title:
        title_error = "You need a blog title!"
    if not blog_body:
        blog_error += "You need a blog body!"

    if title_error or blog_error:
        return render_template('newpost.html', title=blog_title, body=blog_body, 
            title_error=title_error, blog_error=blog_error)
    else:
        new_blog = Blog(blog_title, blog_body) 
        db.session.add(new_blog) 
        db.session.commit()

        blog_id = str(new_blog.id)

        return redirect('/blog?id='+blog_id)

@app.route('/blogz')
def individual_blog():
    blog_id = request.args.get('id')

    blog = Blog.query.filter_by(id=blog_id).all()
    

    return render_template('blogz.html', blog=blog)

'''


if __name__ == '__main__':
    app.run(port = 8080)