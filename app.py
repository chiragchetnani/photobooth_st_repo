import streamlit as st
import requests
from datetime import datetime
from PIL import Image
import os
import io

# API Configuration
API_BASE_URL = "http://35.153.100.110:8000"

st.title("Event Management System")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Upload Photos", "Search Event", "Manage Events"])

if menu == "Upload Photos":
    st.header("Upload Photos")

    uploaded_files = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    event_name = st.text_input("Event Name")
    date = st.date_input("Event Date", value=datetime.now().date())
    
    if st.button("Upload"):
        if not event_name:
            st.error("Please provide an event name.")
        elif not uploaded_files:
            st.error("Please upload at least one image.")
        else:
            for file in uploaded_files:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/add_face/",
                        data={"event_name": event_name, "date": date.strftime("%Y-%m-%d")},
                        files={"file": (file.name, file.getvalue(), file.type)}
                    )
                    if response.status_code == 200:
                        st.success(f"Image {file.name} uploaded successfully.")
                    else:
                        st.error(f"Error uploading {file.name}: {response.json().get('error')}")
                except Exception as e:
                    st.error(f"Error: {e}")

elif menu == "Search Event":
    st.header("Search Events")

    search_option = st.radio("Search by", ["Date Range", "Event Name"])

    if search_option == "Date Range":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if st.button("Search"):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/filter_events_by_date/",
                    params={"start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")}
                )
                if response.status_code == 200:
                    events = response.json().get("events", [])
                    st.success("Events found:")
                    st.write(events)
                else:
                    st.error(response.json().get("error", "No events found."))
            except Exception as e:
                st.error(f"Error: {e}")

    elif search_option == "Event Name":
        event_name = st.text_input("Event Name")
        image_file = st.file_uploader("Upload an image to search", type=["jpg", "jpeg", "png"])
        captured_image = st.camera_input("Or capture an image")

        if st.button("Search"):
            if not event_name:
                st.error("Please provide an event name.")
            elif not image_file and not captured_image:
                st.error("Please upload or capture an image.")
            else:
                img_data = captured_image if captured_image else image_file
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/search_faces/",
                        data={"event_name": event_name},
                        files={"file": (img_data.name, img_data.getvalue(), img_data.type)}
                    )

                    if response.status_code == 200:
                        matched_images = response.json().get("matched_images", [])
                        if matched_images:
                            st.success("Matched Images Found!")
                            for img_path in matched_images:
                                if os.path.exists(img_path):
                                    st.image(img_path, caption=os.path.basename(img_path), use_column_width=True)
                                else:
                                    st.warning(f"Image not found: {img_path}")
                        else:
                            st.warning("No matching images found.")
                    else:
                        st.error(response.json().get("error", "Error searching for images."))
                except Exception as e:
                    st.error(f"Error: {e}")
