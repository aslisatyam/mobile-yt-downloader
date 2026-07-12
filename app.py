import streamlit as st
import requests

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab har quality me video download karein bina kisi error ke!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Details using Free External API (Bypasses YouTube 403 block)
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("High-quality formats scan ho rahe hain..."):
            try:
                # Pubic open API to fetch pre-merged high quality links
                api_url = f"https://cobalt.tools"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                # Cobalt API parameters for high quality
                payload = {
                    "url": url,
                    "vQuality": "1080", # Request max 1080p
                    "isAudioOnly": False
                }
                
                response = requests.post(api_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    res_data = response.json()
                    
                    if res_data.get("status") == "stream" or res_data.get("status") == "picker":
                        download_url = res_data.get("url")
                        picker_links = res_data.get("picker", [])
                        
                        unique_formats = {}
                        
                        # Agar multiple qualities milti hain (Picker format)
                        if picker_links:
                            for item in picker_links:
                                quality_label = item.get("type", "Video") + "p"
                                if "audio" not in quality_label.lower():
                                    unique_formats[f"{quality_label} (High Quality)"] = item.get("url")
                        
                        # Agar single best link milta hai
                        if download_url:
                            unique_formats["Best Quality Available (Up to 1080p)"] = download_url
                            
                        sorted_labels = list(unique_formats.keys())
                        
                        st.session_state.video_data = {
                            'title': "YouTube Video",
                            'formats_dict': unique_formats,
                            'sorted_labels': sorted_labels
                        }
                        st.rerun()
                    else:
                        st.error("Video processing fail ho gayi. Kripya doobara koshish karein.")
                else:
                    st.error(f"API Error: Server respond nahi kar raha hai. Status: {response.status_code}")
            except Exception as e:
                st.error(f"Error: Connection fail ho gaya. Details: {e}")

# Step 2: Show Quality Selector & Download Button
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success("✅ Video Found!")
    
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # Premium design green button
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.caption("💡 **Tip:** Button par click karte hi aapki premium quality video download hona shuru ho jayegi!")
    else:
        st.error("Koi high-quality format nahi mil paya.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
