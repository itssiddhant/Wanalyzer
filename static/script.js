document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('upload-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('chat-file');
        const formData = new FormData();
        formData.append('chat_file', fileInput.files[0]);
        
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || 'An unknown error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred: ' + error.message);
            // You might want to display the error message on the page instead of an alert
            // document.getElementById('error-message').textContent = error.message;
            // document.getElementById('error-message').classList.remove('hidden');
        });
    });
});

function displayResults(data) {
    document.getElementById('results').classList.remove('hidden');
    
    // Update basic statistics
    document.getElementById('total-messages').textContent = data.total_messages;
    document.getElementById('total-users').textContent = data.total_users;
    document.getElementById('media-count').textContent = data.media_count;
    document.getElementById('total-emojis').textContent = data.total_emojis;
    document.getElementById('avg-response-time').textContent = data.avg_response_time.toFixed(2);
    
    document.getElementById('avg-sentiment').textContent = data.avg_sentiment.toFixed(2);
    document.getElementById('longest-streak-user').textContent = data.longest_streak_user;
    document.getElementById('longest-streak-count').textContent = data.longest_streak_count;
   
    // Create messages per user chart
    const messagesPerUserCtx = document.getElementById('messages-per-user-chart').getContext('2d');
    new Chart(messagesPerUserCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.messages_per_user),
            datasets: [{
                label: 'Messages',
                data: Object.values(data.messages_per_user),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Create time of day chart
    const timeOfDayCtx = document.getElementById('time-of-day-chart').getContext('2d');
    new Chart(timeOfDayCtx, {
        type: 'line',
        data: {
            labels: Object.keys(data.time_of_day_counts),
            datasets: [{
                label: 'Messages',
                data: Object.values(data.time_of_day_counts),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Create top words chart
    const topWordsCtx = document.getElementById('top-words-chart').getContext('2d');
    new Chart(topWordsCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.top_words),
            datasets: [{
                label: 'Occurrences',
                data: Object.values(data.top_words),
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                borderColor: 'rgba(153, 102, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });

    // Display word cloud
    document.getElementById('wordcloud').src = 'data:image/png;base64,' + data.wordcloud;

    // Display top emojis
    const topEmojisContainer = document.getElementById('top-emojis-container');
    topEmojisContainer.innerHTML = '';
    Object.entries(data.top_emojis).forEach(([emoji, count]) => {
        topEmojisContainer.innerHTML += `<span>${emoji}: ${count}</span><br>`;
    });
    
    // Display conversation starters and closers
    const startersContainer = document.getElementById('conversation-starters');
    const closersContainer = document.getElementById('conversation-closers');
    startersContainer.innerHTML = '';
    closersContainer.innerHTML = '';
    Object.entries(data.conversation_starters).forEach(([user, count]) => {
        startersContainer.innerHTML += `<span>${user}: ${count}</span><br>`;
    });
    Object.entries(data.conversation_closers).forEach(([user, count]) => {
        closersContainer.innerHTML += `<span>${user}: ${count}</span><br>`;
    });
}