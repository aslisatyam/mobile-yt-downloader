import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="Python YT Pro Downloader", page_icon="🚀", layout="centered")

st.markdown("<h1 style='text-align: center; color: #FF0000;'>YouTube Pro Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bhai, link dalo aur bina kisi block ke mast video/audio download karo!</p>", unsafe_allow_html=True)

# State setup check karne ke liye ki link ready hai ya nahi
if 'download_url' not in st.session_state:
    st.session_state.download_url = None

url = st.text_input("Paste Video/Playlist Link Here:", placeholder="https://youtube.com...")
is_mp3 = st.checkbox("🎵 Download as MP3 (Audio Only)")

if st.button("🚀 Prepare Download Link", use_container_width=True):
    if not url.strip():
        st.error("Bhai, pehle URL toh daalo!")
    else:
        with st.spinner("⏳ Cloud bypass active ho raha hai... Link taiyar ho rahi hai..."):
            # 🌟 Custom public network server infrastructure rules implementation
            api_url = "https://wuk.sh"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "url": url.strip(),
                "vQuality": "720", 
                "isAudioOnly": is_mp3
            }
            
            try:
                response = requests.post(api_url, json=data, headers=headers)
                res_data = response.json()
                
                if response.status_code == 200 or res_data.get("status") == "redirect" or "url" in res_data:
                    st.session_state.download_url = res_data.get("url")
                    st.success("✅ Download link ekdum taiyar hai! Niche diye button par click karein.")
                else:
                    st.error(f"❌ Server side error: {res_data.get('text', 'Please try again later')}")
            except Exception as e:
                st.error(f"❌ Network response issue, firse try karein: {str(e)}")

# Green rang ka button browser download trigger karne ke liye
if st.session_state.download_url:
    st.markdown(
        f'<a href="{st.session_state.download_url}" target="_blank" style="text-decoration: none;">'
        f'<button style="width:100%; padding:14px; background-color:#4CAF50; color:white; '
        f'border:none; border-radius:5px; font-weight:bold; cursor:pointer; font-size:16px;">'
        f'📥 Click Here to Save to Device</button></a>',
        unsafe_allow_html=True
    )
    st.balloons()
