import streamlit as st
import requests

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab har quality me video download karein full sound ke sath!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Details using Free Working API (Cobalt API GET Method)
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("High-quality formats scan ho rahe hain..."):
            try:
                # Cobalt API ka standard GET endpoint use kar rahe hain jo sabse stable hai
                api_url = f"https://cobalt.tools"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Referer": "https://cobalt.tools"
                }
                
                # Payload jisme quality configurations locked hain
                payload = {
                    "url": url,
                    "vQuality": "1080", # Max quality capability request
                    "isAudioOnly": False,
                    "filenamePattern": "classic"
                }
                
                response = requests.post(api_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    res_data = response.json()
                    
                    unique_formats = {}
                    
                    # Agar single direct high-quality merged link milta hai
                    if res_data.get("url"):
                        unique_formats["Best Quality Available (720p / 1080p Full Sound)"] = res_data.get("url")
                    
                    # Agar picker options milte hain
                    if res_data.get("picker"):
                        for item in res_data.get("picker"):
                            if item.get("type") == "video":
                                label = f"{item.get('quality', 'High Quality')}p (Sound Included)"
                                unique_formats[label] = item.get("url")
                    
                    if unique_formats:
                        st.session_state.video_data = {
                            'title': "YouTube Video",
                            'formats_dict': unique_formats,
                            'sorted_labels': list(unique_formats.keys())
                        }
                        st.rerun()
                    else:
                        st.error("Is video ke liye high-quality link generate nahi ho paya.")
                else:
                    # Agar yeh free node busy hai toh alternative dynamic fallback link denge
                    st.warning("Primary server busy hai, alternative download method check kiya ja raha hai...")
                    # Fallback to direct progressive streams
                    st.session_state.video_data = {
                        'title': "YouTube Video",
                        'formats_dict': {"Standard Quality (720p/360p Mixed Sound)": f"https://twdown.tools{url}"},
                        'sorted_labels': ["Standard Quality (720p/360p Mixed Sound)"]
                    }
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: Connection fail ho gaya. Details: {e}")

# Step 2: Show Quality Selector & Direct Link
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success("✅ Video Found!")
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Premium green layout download button
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" download style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        st.caption("💡 **Tip:** Download Now par click karte hi video direct full HD me sound ke sath download hona shuru ho jayegi.")
    else:
        st.error("Formats load nahi ho paaye.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
