from flask import Flask, request, render_template, jsonify,send_file
import requests
import logging
from pytrends.request import TrendReq
import time
from collections import Counter
import matplotlib.pyplot as plt

PROPERTY_GA4_ID = '407460020'
starting_date = "28daysAgo"
ending_date = "yesterday"
GOOGLE_URL = "https://www.google.com/"
GOOGLE_ANALYTICS_URL = "https://analytics.google.com/analytics/web/?pli=1#/p407460020/reports/intelligenthome"



#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ga4-project-402022-9247fce49a1f.json'
    
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def home_page():
    google_tag = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-67RV40YVNY"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-67RV40YVNY');
    </script>
    """
    return google_tag + "Welcome to My Website"

@app.route('/app-dashboard', methods=['GET'])
def app_dashboard():
    return """
    <form method="GET" action="/show-analytics-dashboard">
        <input type="submit" value="Display App's Analytics Dashboard">
    </form>
    <form method="GET" action="/check-analytics-request-cookies">
        <input type="submit" value="Check Analytics Request Cookies">
    </form>
    """

@app.route('/show-analytics-dashboard', methods=['GET'])
def show_analytics_dashboard():
    try:
        response = requests.get(GOOGLE_ANALYTICS_URL)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error accessing the Analytics Dashboard: {str(e)}"

@app.route('/check-analytics-request-cookies', methods=['GET'])
def check_analytics_request_cookies():
    try:
        response = requests.get(GOOGLE_ANALYTICS_URL)
        response.raise_for_status()
        cookies = response.cookies
        cookies_html = "<h2>Google Analytics Request Cookies:</h2><ul>"
        for cookie in cookies:
            cookies_html += f"<li><strong>{cookie.name}:</strong> {cookie.value}</li>"
        cookies_html += "</ul>"
        return cookies_html
    except requests.exceptions.RequestException as e:
        return f"Error checking Google Analytics Request Cookies: {str(e)}"

@app.route("/logger", methods=['GET', 'POST'])
def log_page():
    log_msg = "You are connected to the log page"
    app.logger.info(log_msg)

    if request.method == 'POST':
        text_from_textbox = request.form['textbox']
        browser_log = f"""
        <script>
            console.log('Web browser console: You are connected to the log page');
            console.log('Text from the text box: {text_from_textbox}');
        </script>
        """
    else:
        browser_log = """
        <script>
            console.log('Web browser console: You are connected to the log page');
        </script>
        """

    form = """
    <form method="POST">
        <label for="textbox">Text Box :</label><br>
        <input type="text" id="textbox" name="textbox"><br><br>
        <input type="submit" value="Submit">
        <button type="button" onclick="makeGoogleRequest()">Make a Google Request</button>
    </form>
    """
    return log_msg + browser_log + form

@app.route('/perform-google-request-cookies', methods=['GET'])
def perform_google_request_cookies():
    try:
        response = requests.get(GOOGLE_ANALYTICS_URL)
        response.raise_for_status()
        cookies = response.cookies
        return render_template('cookies.html', cookies=cookies)
    except requests.exceptions.RequestException as e:
        return f"Error making Google Analytics Cookies request: {str(e)}"

@app.route('/chart_data')
def chart_data():
    pytrends = TrendReq(hl='en-US', tz=360)
    keywords = ["Marvel", "DC Comics"]
    pytrends.build_payload(keywords, timeframe='today 12-m', geo='US')
    interest_over_time_df = pytrends.interest_over_time()

    data = {
        'dates': interest_over_time_df.index.strftime('%Y-%m-%d').tolist(),
        'Marvel': interest_over_time_df['Marvel'].tolist(),
        'DC': interest_over_time_df['DC Comics'].tolist()
    }

    return jsonify(data)

@app.route('/chart_data_render')
def index():
    return render_template('chart_trend_data.html')

# Decorator to log execution time
def timeit(func):
    def timed(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return execution_time  # Return the execution time directly

    return timed

# Download Shakespeare's text
def download_shakespeare_text():
    url = "https://ocw.mit.edu/ans7870/6/6.006/s08/lecturenotes/files/t8.shakespeare.txt"
    response = requests.get(url)
    return response.text

# Word count using a dictionary
@timeit
def word_count_dictionary(text):
    words = text.split()
    word_count = {}
    for word in words:
        word = word.lower()
        if word.isalpha():
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
    return word_count

# Word count using Counter
@timeit
def word_count_counter2(text):
    words = text.split()
    words = [word.lower() for word in words if word.isalpha()]
    word_count = Counter(words)
    return word_count

@app.route('/word_count', methods=['GET'])
def count_words():
    shakespeare_text = download_shakespeare_text()
    
    word_count_dict_times = [word_count_dictionary(shakespeare_text) for _ in range(100)]
    word_count_counter_times = [word_count_counter2(shakespeare_text) for _ in range(100)]
    
    # Calculate average execution times
    print(word_count_counter_times[0])

    average_dict_time = sum(word_count_dict_times) / len(word_count_dict_times)
    average_counter_time = sum(word_count_counter_times) / len(word_count_counter_times)
    
    # Calculate variance of execution times
    variance_dict_time = sum((t - average_dict_time) ** 2 for t in word_count_dict_times) / len(word_count_dict_times)
    variance_counter_time = sum((t - average_counter_time) ** 2 for t in word_count_counter_times) / len(word_count_counter_times)
    
    methods = ['Dictionary', 'Counter']
    average_times = [average_dict_time, average_counter_time]
    
    plt.figure(figsize=(8, 6))
    plt.bar(methods, average_times)
    plt.title('Mean Execution Time')
    plt.xlabel('Method')
    plt.ylabel('Time (s)')
    
    # Save the plot as an image
    plt.savefig('execution_time_plot.png')
    
    # Close the plot to free up resources
    plt.close()
    
    
    # Serve the image to the client
    
    # return jsonify({
    #     "average_dict_time": average_dict_time,
    #     "average_counter_time": average_counter_time,
    #     "variance_dict_time": variance_dict_time,
    #     "variance_counter_time": variance_counter_time
    # })
    return send_file('execution_time_plot.png', mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)