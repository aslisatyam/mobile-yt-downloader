import streamlit as st
import requests
import time

# Page Configuration
st.set_page_config(page_title="Python YT Pro Downloader", page_icon="🚀", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF0000;'>YouTube Pro Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bhai, link dalo aur bina kisi block ke mast video/audio download karo!</p>", unsafe_allow_html=True)

# State setup
if 'download_url' not in st.session_state:
    st.session_state.download_url = None
if 'video_title' not in st.session_state:
    st.session_state.video_title = "download"

url = st.text_input("Paste Video/Playlist Link Here:", placeholder="https://youtube.com...")
is_mp3 = st.checkbox("🎵 Download as MP3 (Audio Only)")

if st.button("🚀 Prepare Download Link", use_container_width=True):
    if not url.strip():
        st.error("Bhai, pehle URL toh daalo!")
    else:
        with st.spinner("⏳ Network बाईपास हो रहा है... link taiyar ho rahi hai..."):
            # Cobalt API infrastructure usage for serverless platform bypass
            api_url = "https://cobalt.tools"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "url": url.strip(),
                "vQuality": "1080",  # Max quality allowed automatically
                "isAudioOnly": is_mp3
            }
            
            try:
                response = requests.post(api_url, json=data, headers=headers)
                res_data = response.json()
                
                if response.status_code == 200 or res_data.get("status") == "redirect":
                    st.session_state.download_url = res_data.get("url")
                    st.session_state.video_title = res_data.get("filename", "download")
                    st.success("✅ Download link taiyar ho gayi hai!")
                else:
                    st.error(f"❌ Server refuse kar raha hai: {res_data.get('text', 'Unknown Error')}")
            except Exception as e:
                st.error(f"❌ Connection fail ho gaya: {str(e)}")

# Safe browser data rendering interface
if st.session_state.download_url:
    st.markdown(
        f'<a href="{st.session_state.download_url}" target="_blank" style="text-decoration: none;">'
        f'<button style="width:100%; padding:12px; background-color:#4CAF50; color:white; '
        f'border:none; border-radius:5px; font-weight:bold; cursor:pointer; font-size:16px;">'
        f'📥 Click Here to Save to Device</button></a>',
        unsafe_allow_html=True
    )
    st.balloons()
