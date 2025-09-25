import requests
import streamlit as st

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Property Listing Form")

# Use a form so that all fields submit together
with st.form("listing_form"):
    st.subheader("Basic Information")
    title = st.text_input("Title", "")

    listing_type = st.selectbox("Listing Type", ["sale", "rent"])
    language = st.selectbox("Language", ["en", "pt"])
    price = st.number_input("Price", min_value=0, step=100)

    st.subheader("Location Details")
    city = st.text_input("City", "")
    neighborhood = st.text_input("Neighborhood", "")

    st.subheader("Property Features (optional)")
    bedrooms = st.number_input("Bedrooms", min_value=0, step=1, value=0)
    bathrooms = st.number_input("Bathrooms", min_value=0, step=1, value=0)
    area_sqm = st.number_input("Area (sqm)", min_value=0, step=10, value=0)
    balcony = st.checkbox("Balcony")
    parking = st.checkbox("Parking")
    elevator = st.checkbox("Elevator")
    floor = st.number_input("Floor", min_value=0, step=1, value=0)
    year_built = st.number_input("Year Built", min_value=0, step=1, value=0)

    submitted = st.form_submit_button("Generate HTML")

# -----------------------------
# Handle form submission
# -----------------------------
if submitted:
    # Build data in the same shape as your Pydantic models
    data = {
        "title": title,
        "location_details": {
            "city": city,
            "neighborhood": neighborhood,
        },
        "property_features": {
            "bedrooms": bedrooms or None,
            "bathrooms": bathrooms or None,
            "area_sqm": area_sqm or None,
            "balcony": balcony,
            "parking": parking,
            "elevator": elevator,
            "floor": floor or None,
            "year_built": year_built or None,
        },
        "price": price,
        "listing_type": listing_type,
        "language": language,
    }

    try:
        # Call your backend endpoint
        # Replace with your actual endpoint URL
        endpoint_url = "http://localhost:8000/generate_property_listing"
        response = requests.post(endpoint_url, json=data)

        if response.status_code == 200:
            html_content = response.text
            st.subheader("Generated HTML")
            st.code(html_content, language="html")
        else:
            st.error(f"Request failed with status {response.status_code}")
    except Exception as e:
        st.error(f"Error calling endpoint: {e}")
