from flask import Flask, render_template, request
import requests
import logging
import os

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/")

def hello_world():
 prefix_google = """
 <!-- Google tag (gtag.js) -->
<script async
src="https://www.googletagmanager.com/gtag/js?id=G-67RV40YVNY"></script>
<script>
 window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
 gtag('config', 'G-67RV40YVNY');
</script>
 """
 return prefix_google + "Hello World"


@app.route("/logger", methods=['GET', 'POST'])
def log():
    log_msg = "log(obi sur le dance floor)"
    app.logger.info(log_msg)

    if request.method == 'POST':
        text_from_textbox = request.form['textbox']

        browser_log = f"""
        <script>
            console.log(' Vous êtes bien connectés à la page des logs');
            console.log('Box : {text_from_textbox}');
        </script>
        """
    else:
        browser_log = """
        <script>
            console.log('Vous êtes bien connectés à la page des logs');
        </script>
        """
    textbox_form = """
    <form method="POST">
        <label for="textbox">Text Box :</label><br>
        <input type="text" id="textbox" name="textbox"><br><br>
        <input type="submit" value="Soumettre">
        <button type="button" onclick="makeGoogleRequest()">Faire une requête Google</button>
    </form>
    """

    return log_msg + browser_log + textbox_form

GOOGLE_URL = "https://www.google.com/"
GOOGLE_ANALYTICS_URL = "https://analytics.google.com/analytics/web/?pli=1#/p407460020/reports/intelligenthome"

@app.route('/google-request', methods=['GET'])
def google_request():
    # Render a form with buttons
    return """
    <form method="GET" action="/perform-google-analytics-request">
        <input type="submit" value="Display Google Analytics Dashboard of this App">
    </form>
    <form method="GET" action="/check-google-analytics-cookies">
        <input type="submit" value="Check Google Analytics Request Cookies">
    </form>
    """

@app.route('/perform-google-analytics-request', methods=['GET'])
def perform_google_analytics_request():
    try:
        response = requests.get(GOOGLE_ANALYTICS_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error with GAnalytics request: {str(e)}"


@app.route('/fetch-google-analytics-data', methods=['GET'])

def fetch_google_analytics_data():

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ga4-project-402022-9247fce49a1f.json'
    PROPERTY_GA4_ID = '407460020'
    starting_date = "28daysAgo"
    ending_date = "yesterday"
    client = BetaAnalyticsDataClient()
    
    def get_visitor_count(client, property_id):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[{"start_date": starting_date, "end_date": ending_date}],
            metrics=[{"name": "activeUsers"}]
        )
        response = client.run_report(request)
        return response

    response = get_visitor_count(client, PROPERTY_GA4_ID)
    if response and response.row_count > 0:
        metric_value = response.rows[0].metric_values[0].value
    else:
        metric_value = "No data" 

    return f'active visitors : {metric_value}'