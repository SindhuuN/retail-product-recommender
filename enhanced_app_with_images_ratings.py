
import streamlit as st
import pandas as pd
import pickle
import os
import json

# -------------------------------
# Dummy Image URLs for Simulation
# -------------------------------
def get_image_url(item_id):
    return f"https://via.placeholder.com/150?text=Item+{item_id}"

# -------------------------------
# Rating Storage Utilities
# -------------------------------
def load_ratings():
    if os.path.exists("ratings.json"):
        with open("ratings.json", "r") as f:
            return json.load(f)
    return {}

def save_rating(user, item_id, rating):
    ratings = load_ratings()
    if user not in ratings:
        ratings[user] = {}
    ratings[user][item_id] = rating
    with open("ratings.json", "w") as f:
        json.dump(ratings, f)

# -------------------------------
# Session State for Login
# -------------------------------
if 'login_successful' not in st.session_state:
    st.session_state.login_successful = False
if 'username' not in st.session_state:
    st.session_state.username = None

# -------------------------------
# Hardcoded User Credentials
# -------------------------------
users = {"admin": "admin123", "user": "pass123"}

# -------------------------------
# Login Form
# -------------------------------
if not st.session_state.login_successful:
    st.title("Login to Access Recommendations")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.login_successful = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")
else:
    st.title("Product Recommendation System")

    # Load Data
    with open('user_item_matrix.pkl', 'rb') as f:
        user_item_matrix = pickle.load(f)
    with open('item_similarity_df.pkl', 'rb') as f:
        item_similarity_df = pickle.load(f)
    with open('content_sim_df.pkl', 'rb') as f:
        content_sim_df = pickle.load(f)

    # Recommendation Functions
    def get_content_recommendations(item_id, top_n=5):
        if item_id not in content_sim_df.index:
            return []
        scores = content_sim_df[item_id].sort_values(ascending=False).drop(item_id)
        return scores.head(top_n).index.tolist()

    def get_collab_recommendations(item_id, top_n=5):
        if item_id not in item_similarity_df.index:
            return []
        scores = item_similarity_df[item_id].sort_values(ascending=False).drop(item_id)
        return scores.head(top_n).index.tolist()

    def get_hybrid_recommendations(item_id, top_n=5):
        content_scores = content_sim_df.get(item_id, pd.Series())
        collab_scores = item_similarity_df.get(item_id, pd.Series())
        hybrid = (content_scores.add(collab_scores, fill_value=0)) / 2
        hybrid = hybrid.sort_values(ascending=False).drop(item_id)
        return hybrid.head(top_n).index.tolist()

    # Search & Filter UI
    search_query = st.text_input("Search for a product")
    filtered_items = [item for item in content_sim_df.index if search_query.lower() in str(item).lower()]
    category_filter = st.multiselect("Filter by category keyword", ['electronics', 'books', 'fashion', 'home', 'toys'])

    if category_filter:
        filtered_items = [item for item in filtered_items if any(cat in str(item).lower() for cat in category_filter)]

    selected_item = st.selectbox("Choose a product ID:", filtered_items[:50] if filtered_items else content_sim_df.index[:50])

    # Show Recommendations
    if selected_item:
        st.image(get_image_url(selected_item), caption=f"Selected Product: {selected_item}")
        st.subheader("Content-Based Recommendations")
        content_recs = get_content_recommendations(selected_item)
        for rec in content_recs:
            st.image(get_image_url(rec), width=100)
            st.write(f"Recommended: {rec}")

        st.subheader("Collaborative Recommendations")
        collab_recs = get_collab_recommendations(selected_item)
        for rec in collab_recs:
            st.image(get_image_url(rec), width=100)
            st.write(f"Recommended: {rec}")

        st.subheader("Hybrid Recommendations")
        hybrid_recs = get_hybrid_recommendations(selected_item)
        for rec in hybrid_recs:
            st.image(get_image_url(rec), width=100)
            st.write(f"Recommended: {rec}")
            rating = st.radio(f"Rate {rec}", ['👍', '👎'], key=f"rating_{rec}")
            if st.button(f"Submit Rating for {rec}", key=f"submit_{rec}"):
                save_rating(st.session_state.username, rec, rating)
                st.success(f"Rating saved for {rec}: {rating}")

    st.subheader("Trending Products")
    trending = user_item_matrix.sum(axis=0).sort_values(ascending=False).head(5)
    for item_id in trending.index:
        st.image(get_image_url(item_id), width=100)
        st.write(f"{item_id} — Interactions: {trending[item_id]}")

    # Logout
    if st.button("Logout"):
        st.session_state.login_successful = False
        st.session_state.username = None
        st.experimental_rerun()
