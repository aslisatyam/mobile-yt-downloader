import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="Python YT Pro Downloader", page_icon="🚀", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FF0000;'>YouTube Pro Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bhai, link dalo aur video/audio download karo!</p>", unsafe_allow_html=True)

url = st.text_input("Paste Video Link Here:", placeholder="https://youtube.com/watch?v=...")
is_mp3 = st.checkbox("🎵 Download as MP3 (Audio Only)")

if 'file_path' not in st.session_state:
    st.session_state.file_path = None
    st.session_state.file_name = None

if st.button("🚀 Prepare Download", use_container_width=True):
    if not url.strip():
        st.error("Bhai, pehle URL toh daalo!")
    else:
        st.session_state.file_path = None
        with st.spinner("⏳ Video process ho raha hai, thoda wait karo..."):
            try:
                tmp_dir = tempfile.mkdtemp()
                outtmpl = os.path.join(tmp_dir, "%(title).80s.%(ext)s")

                if is_mp3:
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": outtmpl,
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                        "noplaylist": True,
                        "quiet": True,
                    }
                else:
                    ydl_opts = {
                        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
                        "outtmpl": outtmpl,
                        "merge_output_format": "mp4",
                        "noplaylist": True,
                        "quiet": True,
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url.strip(), download=True)
                    downloaded_path = ydl.prepare_filename(info)
                    if is_mp3:
                        downloaded_path = os.path.splitext(downloaded_path)[0] + ".mp3"

                st.session_state.file_path = downloaded_path
                st.session_state.file_name = os.path.basename(downloaded_path)
                st.success("✅ Ready hai! Niche button se download karo.")

            except yt_dlp.utils.DownloadError as e:
                st.error(f"❌ Video download nahi ho paayi: {str(e)}")
            except Exception as e:
                st.error(f"❌ Kuch gadbad ho gayi: {str(e)}")

if st.session_state.file_path and os.path.exists(st.session_state.file_path):
    with open(st.session_state.file_path, "rb") as f:
        st.download_button(
            label="📥 Click Here to Save to Device",
            data=f,
            file_name=st.session_state.file_name,
            mime="audio/mp3" if is_mp3 else "video/mp4",
            use_container_width=True,
        )
    st.balloons()
