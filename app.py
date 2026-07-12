import streamlit as st
import yt_dlp
import re

st.set_page_config(page_title="Mobile YT Downloader", page_icon="📱", layout="centered")

# Satyam Branding Clean UI Layout
st.title("📱 Mobile YT Downloader")
st.caption("⚡ Made by Satyam")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

# Input box without old helper lines
url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Securely Fetch Video Details
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Extracting working download nodes..."):
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
                    
                    # Filtering valid mp4 progressive links with sound integration
                    for f in formats:
                        height = f.get('height')
                        if height and f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('url'):
                            if height >= 720:
                                label = f"{height}p (High Quality HD)"
                            else:
                                label = f"{height}p (Standard Quality)"
                            unique_formats[label] = f.get('url')
                    
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Quality Stream (Standard)"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error("YouTube Response Timeout. Please tap Fetch Details again.")

# Step 2: Show Metadata & Direct Clean Browser Stream Delivery
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Inbuilt dynamic custom button that acts straight into chrome system
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15); margin-bottom: 10px;">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.info("💡 **Mobile Phone Me Kaise Save Karein?**\n"
                "1. Upar diye gaye **Download Now** button par click karein.\n"
                "2. Video aapke browser me play hone lagegi.\n"
                "3. Video ke right-side niche corner me **3 dots (...)** dikhenge, uspe click karke **'Download'** select karein. Video poori sound ke saath aapki gallery me save ho jayegi!")
    else:
        st.error("No valid streams mapped for this target.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
