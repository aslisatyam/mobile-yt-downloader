import streamlit as st
import yt_dlp
import re

st.set_page_config(page_title="Mobile YT Downloader", page_icon="📱", layout="centered")

# Satyam Branding Custom Header
st.title("📱 Mobile YT Downloader")
st.caption("⚡ Made by Satyam")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

# Clean input box
url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Info & Stream Links (Safe Meta Extraction)
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Scanning for best quality tracks..."):
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'skip': ['hls', 'dash']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    }
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'YouTube Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    unique_formats = {}
                    
                    # Filtering valid progressive MP4 streams
                    for f in formats:
                        height = f.get('height')
                        if height and f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                            if height >= 720:
                                label = f"{height}p (High Quality HD)"
                            else:
                                label = f"{height}p (Standard Quality)"
                            unique_formats[label] = f.get('url')
                    
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Quality Available"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error("Error: YouTube Server block code received. Please click fetch again!")

# Step 2: Show Metadata & Client-Side JavaScript Blob Downloader
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_stream_url = data['formats_dict'][selected_label]
        
        # Safe filename string logic
        safe_title = "".join([c for c in data['title'] if c.isalnum() or c in [' ', '-', '_']]).strip()
        
        # HTML5 + JS code for in-browser download with real progress bar
        js_downloader_html = f"""
        <div style="font-family: sans-serif; background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #eee;">
            <button id="dl-btn" onclick="downloadVideo()" style="width: 100%; padding: 14px 28px; background-color: #25D366; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 18px; cursor: pointer; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">
                📥 Click to Download Now ({selected_label})
            </button>
            
            <div id="progress-container" style="display: none; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; font-weight: bold; color: #333;">
                    <span id="status-text">Connecting to stream node...</span>
                    <span id="percent-text">0%</span>
                </div>
                <div style="width: 100%; background-color: #e0e0e0; border-radius: 6px; height: 12px; overflow: hidden;">
                    <div id="progress-bar" style="width: 0%; height: 100%; background-color: #25D366; transition: width 0.1s linear;"></div>
                </div>
            </div>
        </div>

        <script>
        async function downloadVideo() {{
            const btn = document.getElementById('dl-btn');
            const container = document.getElementById('progress-container');
            const bar = document.getElementById('progress-bar');
            const percentText = document.getElementById('percent-text');
            const statusText = document.getElementById('status-text');
            
            btn.disabled = true;
            btn.style.backgroundColor = '#cccccc';
            btn.innerText = 'Processing...';
            container.style.display = 'block';
            
            try {{
                statusText.innerText = "Fetching video chunks directly from YouTube...";
                const response = await fetch("{final_stream_url}");
                
                if (!response.ok) throw new Error('Network error or source expired.');
                
                const reader = response.body.getReader();
                const contentLength = +response.headers.get('Content-Length');
                
                let receivedLength = 0;
                let chunks = [];
                
                while(true) {{
                    const {{done, value}} = await reader.read();
                    
                    if (done) {{
                        break;
                    }}
                    
                    chunks.push(value);
                    receivedLength += value.length;
                    
                    if (contentLength) {{
                        let pct = Math.round((receivedLength / contentLength) * 100);
                        bar.style.width = pct + '%';
                        percentText.innerText = pct + '%';
                        statusText.innerText = "Downloading data stream directly inside Chrome... " + Math.round(receivedLength / (1024*1024)) + " MB";
                    }}
                }}
                
                statusText.innerText = "🎉 Finalizing and assembling MP4 file container...";
                bar.style.width = '100%';
                percentText.innerText = '100%';
                
                // Assemble chunks into a true playable local blob
                const blob = new Blob(chunks, {{ type: 'video/mp4' }});
                const downloadUrl = URL.createObjectURL(blob);
                
                // Native hidden anchor download trigger
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = "{safe_title}.mp4";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);
                
                statusText.innerText = "🎉 Video Saved Successfully to Gallery / Downloads!";
                btn.style.backgroundColor = '#25D366';
                btn.disabled = false;
                btn.innerText = '📥 Download Again';
                
            }} catch (error) {{
                statusText.innerText = "Error: Stream blocked or connection interrupted. Please try again.";
                statusText.style.color = 'red';
                btn.style.backgroundColor = '#ff4b4b';
                btn.disabled = false;
                btn.innerText = '🔄 Retry Download';
                console.error(error);
            }}
        }}
        </script>
        """
        
        # Inject Javascript safe frame component
        st.components.v1.html(js_downloader_html, height=140)
        st.caption("💡 **Note:** Bina koi naya tab khule isi website par live progress loading chalegi aur complete hote hi browser direct correct video file download folder me save kar dega.")
    else:
        st.error("No stream arrays mapped.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
