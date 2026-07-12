import streamlit as st
import yt_dlp

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab bina kisi proxy ya API issue ke directly videos fetch karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details directly via optimized yt-dlp
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video formats extract ho rahe hain..."):
            try:
                # Advanced configuration to bypass 403 blocks and get distinct formats
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    # Extractor arguments to simulate a real official client
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'skip': ['hls', 'dash']
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-us,en;q=0.5'
                    }
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    unique_formats = {}
                    
                    # Web formats extract karein jisme pre-merged formats (jaise 720p/360p) download ke liye ready ho
                    for f in formats:
                        height = f.get('height')
                        # Check dynamic combinations
                        if height and f.get('vcodec') != 'none' and f.get('url'):
                            # Filter standard resolutions
                            if height in:
                                label = f"{height}p (High Quality)" if height >= 720 else f"{height}p (Standard Quality)"
                                unique_formats[label] = f.get('url')
                    
                    # Fallback single download link
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Auto Quality (With Sound)"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(x.split('p')[0]) if 'p' in x else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Video stream fetch nahi ho payi. Details: {e}")

# Step 2: Show Quality Selector & Direct Browser Download
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Streamlit direct action button
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.caption("💡 **Tip:** Button par click karne par agar video play hone lage, toh desktop/mobile screen par niche **3 dots (...)** par click karke **'Download'** select kar lein.")
    else:
        st.error("Is video ke liye koi public download format nahi mil paya.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
