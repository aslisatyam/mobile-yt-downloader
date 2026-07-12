import streamlit as st
import yt_dlp
import io
import re
import requests

st.set_page_config(page_title="Mobile YT Downloader", page_icon="📱", layout="centered")

# Custom Title and Branding (Made by Satyam)
st.title("📱 Mobile YT Downloader")
st.caption("⚡ Made by Satyam")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

# Clean Input Box without old instruction text
url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Extract best available high qualities dynamically
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Scanning for highest quality formats..."):
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
                    
                    # Scanning for maximum possible resolution streams containing pre-merged sound
                    for f in formats:
                        height = f.get('height')
                        if height and f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                            if height >= 720:
                                label = f"{height}p (High Quality HD - Sound Included)"
                            else:
                                label = f"{height}p (Standard Quality - Sound Included)"
                            unique_formats[label] = f.get('url')
                    
                    # Direct fallback backup if stream array cuts down
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Quality Available (With Sound)"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error("Error: Server responds slow. Kripya ek baar dobara try karein!")

# Step 2: Live In-App Progress Bar Downloading Block (No Redirection)
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_stream_url = data['formats_dict'][selected_label]
        
        # Real-time process initiation trigger inside the same page layout
        if st.button(f"🚀 Prepare & Download {selected_label}", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Connecting to secure stream node...")
                progress_bar.progress(15)
                
                response = requests.get(final_stream_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
                total_length = response.headers.get('content-length')
                
                buffer = io.BytesIO()
                progress_bar.progress(35)
                
                if total_length is None:
                    buffer.write(response.content)
                    progress_bar.progress(100)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for chunk in response.iter_content(chunk_size=65536):  # Large size chunks for faster fetch
                        if chunk:
                            dl += len(chunk)
                            buffer.write(chunk)
                            # Custom visual animation progression calculation
                            done = int(35 + (dl / total_length) * 65)
                            progress_bar.progress(min(done, 100))
                            status_text.text(f"Downloading stream parts... {int((dl/total_length)*100)}%")
                
                status_text.text("🎉 Video Ready! Below button par click karke save karein.")
                
                # Direct in-browser local save activation layout
                st.download_button(
                    label="💾 Click Here to Save to Device / Gallery",
                    data=buffer.getvalue(),
                    file_name=f"{data['title']}.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as dl_err:
                st.error(f"Download break error: {dl_err}")
    else:
        st.error("No valid quality layers could be loaded.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
