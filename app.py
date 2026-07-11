import streamlit as st
import yt_dlp
import os

# Page Configuration
st.set_page_config(page_title="Python YT Pro Downloader", page_icon="🚀", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF0000;'>YouTube Pro Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bhai, link dalo aur mast video/audio download karo!</p>", unsafe_allow_html=True)

if 'available_formats' not in st.session_state:
    st.session_state.available_formats = {}
if 'qualities_list' not in st.session_state:
    st.session_state.qualities_list = ["Pehle Link Fetch Karein"]
if 'thumbnail_url' not in st.session_state:
    st.session_state.thumbnail_url = None
if 'status_msg' not in st.session_state:
    st.session_state.status_msg = "Ready to roll! 😎"
if 'status_color' not in st.session_state:
    st.session_state.status_color = "gray"

url = st.text_input("Paste Video/Playlist Link Here:", placeholder="https://youtube.com...")

# 🌟 403 Forbidden se bachne ke liye safe Android client parameters
SAFE_OPTS = {
    'nocheckcertificate': True,
    'quiet': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web_embedded'],
            'player_skip': ['webpage', 'configs']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
}

if st.button("🔍 Fetch Video Info", use_container_width=True):
    if not url.strip():
        st.error("Bhai, pehle URL toh daalo!")
    else:
        with st.spinner("🔍 Info fetch ho rahi hai... Please wait..."):
            try:
                with yt_dlp.YoutubeDL(SAFE_OPTS) as ydl:
                    info = ydl.extract_info(url.strip(), download=False)
                    is_playlist = 'entries' in info
                    
                    if is_playlist:
                        st.session_state.qualities_list = ["Best Quality (Auto)"]
                        st.session_state.status_msg = "✅ Playlist mil gayi! Direct download par click karein."
                        st.session_state.status_color = "green"
                        
                        entries = list(info.get('entries', []))
                        st.session_state.thumbnail_url = entries.get('thumbnail') if entries and entries else None
                    else:
                        formats = info.get('formats', [])
                        qualities = set()
                        st.session_state.available_formats.clear()
                        
                        for f in formats:
                            if f.get('height') and f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                                h = f.get('height')
                                quality_str = f"{h}p"
                                qualities.add(quality_str)
                                
                                if quality_str not in st.session_state.available_formats or f.get('tbr', 0) > st.session_state.available_formats[quality_str]['tbr']:
                                    st.session_state.available_formats[quality_str] = {
                                        'format_id': f.get('format_id'),
                                        'tbr': f.get('tbr', 0)
                                    }
                        
                        sorted_qualities = sorted(list(qualities), key=lambda x: int(x.replace('p', '')), reverse=True)
                        
                        if sorted_qualities:
                            st.session_state.qualities_list = sorted_qualities
                            st.session_state.status_msg = "✅ Qualities mil gayi! Format select karke download karein."
                            st.session_state.status_color = "green"
                        else:
                            st.session_state.qualities_list = ["Best Quality (Auto)"]
                            st.session_state.status_msg = "✅ Video mil gayi! Direct download par click karein."
                            st.session_state.status_color = "green"
                        
                        st.session_state.thumbnail_url = info.get('thumbnail')
            except Exception as e:
                st.session_state.status_msg = f"❌ Info fetch fail ho gayi! {str(e)}"
                st.session_state.status_color = "red"

st.markdown(f"<p style='color: {st.session_state.status_color}; font-style: italic;'>{st.session_state.status_msg}</p>", unsafe_allow_html=True)

selected_quality = st.selectbox("Select Video Quality:", st.session_state.qualities_list)

if st.session_state.thumbnail_url:
    st.image(st.session_state.thumbnail_url, caption="Video/Playlist Thumbnail", width=300)

is_mp3 = st.checkbox("🎵 Download as MP3 (Audio Only)")

if url.strip() and st.session_state.status_color == "green":
    if st.button("🚀 Prepare Download Link", use_container_width=True):
        with st.spinner("⏳ Server par file taiyar ho rahi hai..."):
            try:
                # 🌟 Download ke waqt bhi SAFE_OPTS use karenge taaki 403 error na aaye
                download_opts = SAFE_OPTS.copy()
                
                if is_mp3:
                    out_filename = "downloaded_audio.mp3"
                    download_opts.update({
                        'format': 'bestaudio',
                        'outtmpl': 'downloaded_audio.%(ext)s',
                    })
                else:
                    out_filename = "downloaded_video.mp4"
                    if selected_quality in st.session_state.available_formats:
                        v_id = st.session_state.available_formats[selected_quality]['format_id']
                        format_selector = v_id
                    else:
                        format_selector = 'best[ext=mp4]/best'
                        
                    download_opts.update({
                        'format': format_selector,
                        'outtmpl': 'downloaded_video.%(ext)s',
                    })
                
                with yt_dlp.YoutubeDL(download_opts) as ydl_dl:
                    file_info = ydl_dl.extract_info(url.strip(), download=True)
                    ext = file_info.get('ext', 'mp4') if not is_mp3 else file_info.get('ext', 'm4a')
                    real_filename = f"downloaded_audio.{ext}" if is_mp3 else f"downloaded_video.{ext}"
                
                if os.path.exists(real_filename):
                    with open(real_filename, "rb") as file:
                        st.download_button(
                            label="📥 Click Here to Save to Device",
                            data=file,
                            file_name=f"audio.{ext}" if is_mp3 else f"video.{ext}",
                            mime=f"audio/{ext}" if is_mp3 else f"video/{ext}",
                            use_container_width=True
                        )
                    os.remove(real_filename)
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Kuch error aaya: {str(e)}")
