from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import re
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import emoji
from wordcloud import WordCloud
import base64
import io
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import json

app = Flask(__name__)

def parse_line(line):
    pattern = r'(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.*?): (.*)'
    match = re.match(pattern, line)
    if match:
        date_str, time_str, user, message = match.groups()
        return {'date': date_str, 'time': time_str, 'user': user, 'message': message}
    return None

def analyze_chat(chat_data):
    messages = [parse_line(line) for line in chat_data if parse_line(line)]
    df = pd.DataFrame(messages)
    
    # Convert date and time to datetime object
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='%d/%m/%Y %H:%M')
    
    # Basic statistics
    total_messages = len(df)
    total_users = df['user'].nunique()
    
    # Messages per user
    messages_per_user = df['user'].value_counts().to_dict()
    
    # User Contributions Percentage
    user_contribution = (df['user'].value_counts() / len(df) * 100).to_dict()
    
    # Media message count
    media_keywords = ['image', 'video', 'document']
    df['is_media'] = df['message'].apply(lambda x: any(keyword in x.lower() for keyword in media_keywords))
    media_count = df['is_media'].sum()
    
    # Emoji usage
    def count_emojis(message):
        return sum(1 for char in message if char in emoji.EMOJI_DATA)
    
    df['emoji_count'] = df['message'].apply(count_emojis)
    total_emojis = df['emoji_count'].sum()
    
    # Most Used Emojis
    def extract_emojis(message):
        return [char for char in message if char in emoji.EMOJI_DATA]
    
    all_emojis = df['message'].apply(extract_emojis).sum()
    top_emojis = dict(Counter(all_emojis).most_common(10))
    
    # Time of day analysis
    df['hour'] = df['datetime'].dt.hour
    time_of_day_counts = df.groupby(df['hour']).size().to_dict()
    time_of_day_counts = {int(k): int(v) for k, v in time_of_day_counts.items()}
    
    # Top words analysis
    stop_words = set(['the', 'and', 'to', 'is', 'in', 'it', 'that', 'of', 'for', 'on', 'with', 'a', 'this'])
    all_words = ' '.join(df['message']).lower().split()
    filtered_words = [word for word in all_words if word not in stop_words]
    top_words = dict(Counter(filtered_words).most_common(10))
    
    # Sentiment analysis
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df['message'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    avg_sentiment = df['sentiment'].mean()
    user_sentiment = df.groupby('user')['sentiment'].mean().to_dict()
    
    # Response Time Analysis
    df['next_datetime'] = df['datetime'].shift(-1)
    df['time_diff'] = (df['next_datetime'] - df['datetime']).dt.total_seconds() / 60.0  # in minutes
    avg_response_time = df['time_diff'].mean()
    
    # Longest Streak Analysis
    def longest_streak(messages):
        max_streak = 0
        current_streak = 1
        current_user = messages['user'].iloc[0]
        user_streaks = {current_user: 1}

        for i in range(1, len(messages)):
            if messages['user'].iloc[i] == current_user:
                current_streak += 1
            else:
                if current_user in user_streaks:
                    user_streaks[current_user] = max(user_streaks[current_user], current_streak)
                else:
                    user_streaks[current_user] = current_streak
                current_user = messages['user'].iloc[i]
                current_streak = 1

        if current_user in user_streaks:
            user_streaks[current_user] = max(user_streaks[current_user], current_streak)
        else:
            user_streaks[current_user] = current_streak

        longest_streak_user = max(user_streaks, key=user_streaks.get)
        longest_streak_count = user_streaks[longest_streak_user]

        return longest_streak_user, longest_streak_count

    longest_streak_user, longest_streak_count = longest_streak(df)
    
    # Conversation Starters and Closers
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    first_message_by_day = df.groupby(df['date']).first()
    last_message_by_day = df.groupby(df['date']).last()
    conversation_starters = first_message_by_day['user'].value_counts().to_dict()
    conversation_closers = last_message_by_day['user'].value_counts().to_dict()
    
    # Word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_words))
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img, format='png')
    img.seek(0)
    wordcloud_b64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return {
        'total_messages': int(total_messages),
        'total_users': int(total_users),
        'messages_per_user': {k: int(v) for k, v in messages_per_user.items()},
        'user_contribution': {k: float(v) for k, v in user_contribution.items()},
        'media_count': int(media_count),
        'total_emojis': int(total_emojis),
        'top_emojis': {k: int(v) for k, v in top_emojis.items()},
        'time_of_day_counts': time_of_day_counts,
        'top_words': {k: int(v) for k, v in top_words.items()},
        'avg_sentiment': float(avg_sentiment),
        'user_sentiment': {k: float(v) for k, v in user_sentiment.items()},
        'avg_response_time': float(avg_response_time),
        'longest_streak_user': longest_streak_user,
        'longest_streak_count': int(longest_streak_count),
        'conversation_starters': {k: int(v) for k, v in conversation_starters.items()},
        'conversation_closers': {k: int(v) for k, v in conversation_closers.items()},
        'wordcloud': wordcloud_b64
    }

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'chat_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        chat_file = request.files['chat_file']
        if chat_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if chat_file:
            try:
                chat_data = chat_file.read().decode('utf-8').splitlines()
                analysis_results = analyze_chat(chat_data)
                return app.response_class(
                    response=json.dumps(analysis_results, cls=NumpyEncoder),
                    status=200,
                    mimetype='application/json'
                )
            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return jsonify({'error': str(e)}), 500
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.2',port=5501,debug=True)