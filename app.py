import streamlit as st
import yt_dlp
import io
import re

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab bina kisi extra tab ke sidha high quality mp4 download karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details directly using optimized browser signatures
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video details scan ho rahi hain..."):
            try:
                # Direct safe configurations to fetch true quality layouts
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
                    
                    # Filtering formats that contain pre-merged audio and video tracks
                    for f in formats:
                        height = f.get('height')
                        if height and f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                            label = f"{height}p (Sound Included - .mp4)"
                            unique_formats[label] = f.get('url')
                    
                    # Fallback configuration
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Auto Quality (With Sound)"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Connection reset. Link check karke dobara koshish karein.")

# Step 2: In-app Progressive Download with Real-time Progress Bar
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_stream_url = data['formats_dict'][selected_label]
        
        # Inbuilt progressive extraction
        if st.button(f"🚀 Prepare & Download {selected_label}", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Connecting to secure video node...")
                progress_bar.progress(15)
                
                # Fetch data directly from stream URL via standard requests
                import requests
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
                    for chunk in response.iter_content(chunk_size=32768): # Optimized chunk processing block
                        if chunk:
                            dl += len(chunk)
                            buffer.write(chunk)
                            done = int(35 + (dl / total_length) * 65)
                            progress_bar.progress(min(done, 100))
                            status_text.text(f"Extracting high quality bytes... {int((dl/total_length)*100)}%")
                
                status_text.text("🎉 Video Ready! Niche diye gaye button par click karke save karein.")
                
                # Native local browser file save action
                st.download_button(
                    label="💾 Click Here to Save to Local Storage",
                    data=buffer.getvalue(),
                    file_name=f"{data['title']}.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as download_err:
                st.error(f"Download processing error: {download_err}")
    else:
        st.error("No valid quality layers mapped.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
