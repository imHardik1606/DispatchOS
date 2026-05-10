from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DispatchOS API Documentation</title>
    <style>
        :root {
            --bg-color: #0f0f0f;
            --card-bg: #1a1a1a;
            --text-color: #e0e0e0;
            --get-color: #22c55e;
            --post-color: #3b82f6;
            --border-color: #333;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
        }
        header {
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 3rem;
            padding-bottom: 1rem;
        }
        h1 { margin: 0; color: #fff; }
        .subtitle { color: #888; font-size: 1.1rem; }
        .author { margin-top: 0.5rem; font-size: 0.9rem; }
        .author a { color: var(--post-color); text-decoration: none; }
        .author a:hover { text-decoration: underline; }

        .endpoint-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 2.5rem;
            padding: 1.5rem;
        }
        .endpoint-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .badge {
            border-radius: 4px;
            color: #fff;
            font-family: monospace;
            font-weight: bold;
            padding: 0.2rem 0.6rem;
            text-transform: uppercase;
        }
        .badge-get { background-color: var(--get-color); }
        .badge-post { background-color: var(--post-color); }
        .path {
            font-family: monospace;
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .section-title {
            color: #fff;
            font-size: 0.9rem;
            font-weight: bold;
            margin-top: 1.2rem;
            margin-bottom: 0.4rem;
            text-transform: uppercase;
        }
        .code-block {
            background-color: #000;
            border-radius: 4px;
            font-family: monospace;
            padding: 0.8rem;
            white-space: pre-wrap;
        }
        
        table {
            border-collapse: collapse;
            margin-top: 0.5rem;
            width: 100%;
        }
        th, td {
            border-bottom: 1px solid var(--border-color);
            padding: 0.8rem;
            text-align: left;
        }
        th {
            color: #888;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        .status-code { font-family: monospace; font-weight: bold; }
        
        .diagram {
            background-color: #222;
            border-left: 4px solid var(--post-color);
            color: #fff;
            font-family: monospace;
            margin: 1rem 0;
            padding: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <header>
        <h1>DispatchOS</h1>
        <div class="subtitle">AI-native inbound voice dispatcher agent</div>
        <div class="author">Hardik Gayner | <a href="https://github.com/imHardik1606" target="_blank">github.com/imHardik1606</a></div>
    </header>

    <main>
        <!-- Endpoint 1: Health -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="badge badge-get">GET</span>
                <span class="path">/api/v1/health</span>
            </div>
            <p>Verify the API is responsive and check the status of required environment variables like GROQ_API_KEY.</p>
            
            <div class="section-title">Request</div>
            <p>None</p>

            <div class="section-title">Responses</div>
            <table>
                <thead>
                    <tr>
                        <th>Status Code</th>
                        <th>Condition</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="status-code">200</td>
                        <td>Service is healthy and dependencies are configured.</td>
                        <td>JSON object with service status.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Endpoint 2: Transcribe -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="badge badge-post">POST</span>
                <span class="path">/api/v1/transcribe</span>
            </div>
            <p>Converts uploaded driver audio files into text using Groq's Whisper-1 model.</p>
            
            <div class="section-title">Request</div>
            <p>Multipart/form-data with a <code>file</code> field containing audio (WAV, MP3, M4A).</p>

            <div class="section-title">Responses</div>
            <table>
                <thead>
                    <tr>
                        <th>Status Code</th>
                        <th>Condition</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="status-code">200</td>
                        <td>Transcription successful.</td>
                        <td>JSON containing transcript and character count.</td>
                    </tr>
                    <tr>
                        <td class="status-code">200</td>
                        <td>No speech detected in audio.</td>
                        <td>JSON with <code>status: empty_transcript</code>.</td>
                    </tr>
                    <tr>
                        <td class="status-code">422</td>
                        <td>Unsupported audio file type or invalid MIME type.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">503</td>
                        <td>Groq Whisper API service unavailable.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">500</td>
                        <td>Internal server error during audio processing.</td>
                        <td>JSON error detail.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Endpoint 3: Reason -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="badge badge-post">POST</span>
                <span class="path">/api/v1/reason</span>
            </div>
            <p>Processes the driver transcript using LLaMA-3 to generate a professional dispatcher response.</p>
            
            <div class="section-title">Request</div>
            <div class="code-block">{ "transcript": "string" }</div>

            <div class="section-title">Responses</div>
            <table>
                <thead>
                    <tr>
                        <th>Status Code</th>
                        <th>Condition</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="status-code">200</td>
                        <td>Reasoning successful and response generated.</td>
                        <td>JSON containing response text and word count.</td>
                    </tr>
                    <tr>
                        <td class="status-code">400</td>
                        <td>Transcript required or content too short to process.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">502</td>
                        <td>Reasoning engine returned an invalid response.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">503</td>
                        <td>Groq LLaMA API service unavailable.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">500</td>
                        <td>Internal server error during LLM inference.</td>
                        <td>JSON error detail.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Endpoint 4: Synthesize -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="badge badge-post">POST</span>
                <span class="path">/api/v1/synthesize</span>
            </div>
            <p>Converts dispatcher text responses into audio bytes using gTTS.</p>
            
            <div class="section-title">Request</div>
            <div class="code-block">{ "text": "string" }</div>

            <div class="section-title">Response Headers</div>
            <div class="code-block">X-Audio-Length-Bytes, X-TTS-Engine</div>

            <div class="section-title">Responses</div>
            <table>
                <thead>
                    <tr>
                        <th>Status Code</th>
                        <th>Condition</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="status-code">200</td>
                        <td>Synthesis successful and audio stream returned.</td>
                        <td>Audio stream (MPEG).</td>
                    </tr>
                    <tr>
                        <td class="status-code">400</td>
                        <td>Text required or content exceeds character limits (500 chars).</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">502</td>
                        <td>Upstream voice engine returned empty audio data.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">503</td>
                        <td>gTTS voice synthesis service unavailable.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">500</td>
                        <td>Internal server error during audio synthesis.</td>
                        <td>JSON error detail.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Endpoint 5: Dispatch Call -->
        <div class="endpoint-card">
            <div class="endpoint-header">
                <span class="badge badge-post">POST</span>
                <span class="path">/api/v1/dispatch-call</span>
            </div>
            <p>Executes the full voice agent workflow: transcription, reasoning, and synthesis.</p>
            
            <div class="diagram">
                Audio Input → Groq Whisper → LLaMA Reasoning → gTTS → MP3 Response
            </div>

            <div class="section-title">Request</div>
            <p>Multipart/form-data with a <code>file</code> field containing audio.</p>

            <div class="section-title">Response Headers</div>
            <div class="code-block">X-Pipeline-Latency-Ms, X-Transcription-Ms, X-Reasoning-Ms, X-Synthesis-Ms, X-Transcript-Preview, X-TTS-Engine</div>

            <div class="section-title">Responses</div>
            <table>
                <thead>
                    <tr>
                        <th>Status Code</th>
                        <th>Condition</th>
                        <th>Response</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="status-code">200</td>
                        <td>Pipeline executed successfully.</td>
                        <td>Audio stream (MPEG).</td>
                    </tr>
                    <tr>
                        <td class="status-code">200</td>
                        <td>No speech detected in audio.</td>
                        <td>JSON with <code>status: no_speech</code>.</td>
                    </tr>
                    <tr>
                        <td class="status-code">422</td>
                        <td>Unsupported audio file type.</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">502</td>
                        <td>Upstream stage error (transcription, reasoning, or synthesis failure).</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">503</td>
                        <td>External API service unavailable (Groq or gTTS connection issues).</td>
                        <td>JSON error detail.</td>
                    </tr>
                    <tr>
                        <td class="status-code">500</td>
                        <td>Internal server error during pipeline orchestration.</td>
                        <td>JSON error detail.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

@router.get("/apidocs", response_class=HTMLResponse)
async def get_apidocs():
    return HTML_CONTENT
