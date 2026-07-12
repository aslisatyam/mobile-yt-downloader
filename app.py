import streamlit as st
import yt_dlp

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Link paste karein aur mobile/PC browser me best quality me download karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details, Thumbnail & All Available Stream Links
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video details scan ho rahi hain..."):
            try:
                # Optimized configuration taaki YouTube server local IP block na kare
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
                    
                    # Saare formats check karke unhe extract karna
                    for f in formats:
                        height = f.get('height')
                        if height and f.get('vcodec') != 'none' and f.get('url'):
                            # 720p aur usse upar wale formats browser routing ke liye arrange karein
                            if height >= 720:
                                label = f"{height}p (High Quality HD - Sound Included)"
                            else:
                                label = f"{height}p (Standard Quality - Sound Included)"
                            unique_formats[label] = f.get('url')
                    
                    # Fallback option agar progressive selection skip ho jaye
                    if not unique_formats and info.get('url'):
                        unique_formats["Best Quality Stream (With Sound)"] = info.get('url')
                        
                    sorted_labels = sorted(list(unique_formats.keys()), key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0, reverse=True)
                    
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Details extract nahi ho payin. Kripya ek baar dobara try karein!")

# Step 2: Display UI & Handover Direct Stream Link via Green Button
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Premium green link layout button (Yeh direct naye tab me open karega mobile chrome par)
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" download="{data["title"]}.mp4" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.caption("💡 **Mobile Chrome User Tip:** Agar button par click karne ke baad video naye tab me play hone lage, toh niche kone me **3 dots (...)** par click karke **'Download'** select kar lein, video gallery me save ho jayegi!")
    else:
        st.error("Is video ke liye formats load nahi ho paaye.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
