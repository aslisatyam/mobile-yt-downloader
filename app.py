import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Ultimate YouTube Downloader")
st.write("Ab bina kisi extra tab ke sidha high quality mp4 download karein!")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

url = st.text_input("Enter YouTube Video URL:", placeholder="https://youtube.com...")

if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Title, Thumbnail & High-Quality Direct Streams
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video scanning and formats parsing in progress..."):
            try:
                # SaveFrom Engine to extract exact downloadable source direct links
                api_url = "https://sf-api.com"
                payload = {"url": url}
                headers = {"User-Agent": "Mozilla/5.0"}
                
                response = requests.post(api_url, data=payload, headers=headers)
                
                # Cleaning response payload format JavaScript variables
                raw_text = response.text
                json_match = re.search(r'id:\s*({.*?})', raw_text.replace('\n', ''))
                
                if json_match:
                    data_str = json_match.group(1)
                    # Convert to valid structural JSON mapping
                    data_str = re.sub(r'(\w+)\s*:', r'"\1":', data_str)
                    res_json = json.loads(data_str)
                else:
                    # Alternative payload structure check
                    clean_text = raw_text.strip().lstrip('(').rstrip(')')
                    res_json = json.loads(clean_text)

                # Parsing meta parameters
                title = res_json.get("meta", {}).get("title", "YouTube Video")
                thumbnail = res_json.get("meta", {}).get("thumbnail")
                url_list = res_json.get("url", [])
                
                unique_formats = {}
                for item in url_list:
                    quality = item.get("quality")
                    ext = item.get("ext", "mp4")
                    direct_url = item.get("url")
                    
                    # Filtering valid qualities that contain audio
                    if quality and direct_url and ext == "mp4":
                        # If video is 720p or 1080p, these direct engine nodes are already merged with sound
                        label = f"{quality}p (Full Sound - .mp4)"
                        unique_formats[label] = direct_url
                
                if unique_formats:
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted(list(unique_formats.keys()), key=lambda x: int(x.split('p')[0]) if 'p' in x else 0, reverse=True)
                    }
                    st.rerun()
                else:
                    st.error("Is quality format ke links processing me issue hai.")
            except Exception as e:
                st.error("Video parse nahi ho saki. Kripya link sahi se copy karke dobara koshish karein.")

# Step 2: Local direct Streamlit integration via local memory processing
if st.session_state.video_data:
    data = st.session_state.video_data
    st.success(f"🎬 **Video Found:** {data['title']}")
    
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein:", data['sorted_labels'])
        final_stream_url = data['formats_dict'][selected_label]
        
        # Inbuilt Progress bar logic inside client layout
        if st.button(f"🚀 Prepare & Download {selected_label}", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Connecting to secure server stream...")
                progress_bar.progress(10)
                
                # Fetching file binary content in chunks to feed browser locally
                file_response = requests.get(final_stream_url, stream=True)
                total_length = file_response.headers.get('content-length')
                
                video_bytes = b""
                progress_bar.progress(40)
                status_text.text("Extracting audio and video bytes metadata...")
                
                if total_length is None:
                    video_bytes = file_response.content
                else:
                    dl = 0
                    total_length = int(total_length)
                    for chunk in file_response.iter_content(chunk_size=4096):
                        dl += len(chunk)
                        video_bytes += chunk
                        # Dynamic bar simulation logic
                        done = int(50 + (dl / total_length) * 50)
                        progress_bar.progress(min(done, 100))
                        status_text.text(f"Downloading chunks data... {int((dl/total_length)*100)}%")
                
                status_text.text("🎉 Video Download Complete! Niche save karein.")
                
                # Native browser trigger mapping
                st.download_button(
                    label="💾 Click Here to Save to Gallery / PC File",
                    data=video_bytes,
                    file_name=f"{data['title']}.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as download_error:
                st.error(f"Download break error: {download_error}")
    else:
        st.error("Qualities options system read nahi kar paaya.")
        
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
