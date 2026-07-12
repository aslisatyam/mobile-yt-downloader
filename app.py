import streamlit as st
import yt_dlp

st.set_page_config(page_title="Premium YT Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Premium YouTube Downloader")
st.write("Link paste karein, quality chunein aur best quality me download karein!")

# Initialize session states to store video info
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

# Input URL
url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

# If user changes URL in the input box, reset the previous fetched data
if url != st.session_state.current_url:
    st.session_state.video_data = None
    st.session_state.current_url = url

# Step 1: Fetch Video Details Button
if url and st.session_state.video_data is None:
    if st.button("🔍 Fetch Video Details", use_container_width=True):
        with st.spinner("Video ki information nikali ja rahi hai..."):
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Extract title, thumbnail and available formats
                    title = info.get('title', 'Video')
                    thumbnail = info.get('thumbnail')
                    formats = info.get('formats', [])
                    
                    # Filter out distinct video qualities that have both audio and video (progressive)
                    # or filter common resolutions for direct cloud download convenience
                    unique_formats = {}
                    for f in formats:
                        # Hum sirf un links ko le rahe hain jisme resolution (height) ho aur download url valid ho
                        if f.get('height') and f.get('url'):
                            res = f"{f.get('height')}p"
                            # 'ext' mp4 ho toh best hai browser compatible download ke liye
                            ext = f.get('ext', 'mp4')
                            label = f"{res} (Format: {ext})"
                            unique_formats[label] = f.get('url')
                    
                    # Sort formats from high resolution to low resolution
                    sorted_labels = sorted(unique_formats.keys(), key=lambda x: int(x.split('p')[0]), reverse=True)
                    
                    # Save into session state
                    st.session_state.video_data = {
                        'title': title,
                        'thumbnail': thumbnail,
                        'formats_dict': unique_formats,
                        'sorted_labels': sorted_labels
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Error: Link sahi nahi hai ya network issue hai. Details: {e}")

# Step 2: Show Thumbnail, Quality Selector, and Download Button
if st.session_state.video_data:
    data = st.session_state.video_data
    
    st.success(f"**🎬 Video Found:** {data['title']}")
    
    # Display Thumbnail
    if data['thumbnail']:
        st.image(data['thumbnail'], use_container_width=True)
        
    st.write("---")
    
    # Quality Dropdown Selection
    if data['sorted_labels']:
        selected_label = st.selectbox("⚡ Video Quality Select Karein (Best selected by default):", data['sorted_labels'])
        final_download_url = data['formats_dict'][selected_label]
        
        # HTML Download Button
        st.markdown(
            f'<a href="{final_download_url}" target="_blank" style="display: inline-block; padding: 14px 28px; background-color: #25D366; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; text-align: center; width: 100%; font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.15);">📥 Download Now ({selected_label})</a>',
            unsafe_allow_html=True
        )
        
        st.caption("💡 **Tip:** Agar button click karne par video download hone ke bajay naye tab me play hone lage, toh video screen par right side me niche **3 dots (...)** par click karke **'Download'** select kar lein.")
    else:
        st.error("Is video ke liye koi download format nahi mil paya.")
        
    # Reset Button to paste a new link
    if st.button("🔄 Clear & Paste New Link", type="secondary"):
        st.session_state.video_data = None
        st.session_state.current_url = ""
        st.rerun()
