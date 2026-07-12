import streamlit as st
import requests

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab bina kisi ad ya redirect ke sidha high-quality MP4 download karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch details via stable open-source API node
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video parameters link check ho raha hai..."):
            try:
                # Extracting video ID from URL
                video_id = ""
                if "youtu.be/" in url:
                    video_id = url.split("youtu.be/")[1].split("?")[0]
                elif "watch?v=" in url:
                    video_id = url.split("watch?v=")[1].split("&")[0]
                
                if not video_id:
                    st.error("Kripya sahi YouTube link dalein!")
                else:
                    # Using global public open-source invidious node api
                    api_url = f"https://nerdvpn.de{video_id}"
                    response = requests.get(api_url, timeout=10)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        title = res_data.get("title", "YouTube Video")
                        
                        # Fetch best quality secure images thumbnails
                        thumbs = res_data.get("videoThumbnails", [])
                        thumbnail = thumbs[0].get("url") if thumbs else None
                        
                        # Filtering complete video/audio merged stream options
                        format_streams = res_data.get("formatStreams", [])
                        unique_formats = {}
                        
                        for stream in format_streams:
                            quality = stream.get("qualityLabel") # e.g. 720p, 360p
                            container = stream.get("container") # e.g. mp4
                            direct_link = stream.get("url")
                            
                            if quality and container == "mp4" and direct_link:
                                label = f"{quality} (Full HD - Sound Included)" if "720" in quality or "1080" in quality else f"{quality} (Standard)"
                                unique_formats[label] = direct_link
                        
                        if unique_formats:
                            st.session_state.video_data = {
                                'title': title,
                                'thumbnail': thumbnail,
                                'formats_dict': unique_formats,
                                'sorted_labels': list(unique_formats.keys())
                            }
                            st.rerun()
                        else:
                            st.error("Is video ke formats verify nahi ho paye.")
                    else:
                        st.error("Server down hai, kripya ek baar dobara button dabayein.")
            except Exception as e:
                st.error("Network temporary slow hai, please click again.")

# Step 2: Display inside the same tab smoothly
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_stream_url = data['formats_dict'][selected_label]
        
        # Native browser trigger button (Bina doosra tab khule isi window me save hoga)
        st.markdown(
            f'<a href="{final_stream_url}" download="{data["title"]}.mp4" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Direct Download Now</a>',
            unsafe_allow_html=True
        )
        st.caption("💡 **Tip:** Click karte hi video file niche downloading bar me background me shuru ho jayegi!")
    else:
        st.error("No streams available.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
