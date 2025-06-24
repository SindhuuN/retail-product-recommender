import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import os

# --- Load data ---
with open('user_item_matrix.pkl', 'rb') as f:
    user_item_matrix = pickle.load(f)

with open('item_similarity_df.pkl', 'rb') as f:
    item_similarity_df = pickle.load(f)

with open('content_sim_df.pkl', 'rb') as f:
    content_sim_df = pickle.load(f)

# Sample product metadata (if available)
try:
    product_meta = pd.read_csv("product_metadata.csv")  # itemid, categoryid, available, title (optional)
    product_meta.set_index('itemid', inplace=True)
except:
    product_meta = pd.DataFrame(columns=["categoryid", "available"])

# --- Recommendation Functions ---
def get_collaborative_recommendations(user_id, num_recommendations=5):
    if user_id not in user_item_matrix.index:
        return []
    user_ratings = user_item_matrix.loc[user_id]
    rated_items = user_ratings[user_ratings > 0].index
    scores = item_similarity_df[rated_items].sum(axis=1)
    scores = scores.drop(labels=rated_items)
    return scores.sort_values(ascending=False).head(num_recommendations).index.tolist()

def get_content_recommendations(item_id, num_recommendations=5):
    if item_id not in content_sim_df.index:
        return []
    similar_items = content_sim_df[item_id].sort_values(ascending=False).drop(item_id)
    return similar_items.head(num_recommendations).index.tolist()

def get_hybrid_recommendations(user_id, alpha=0.5, num_recommendations=5):
    if user_id not in user_item_matrix.index:
        return []
    user_ratings = user_item_matrix.loc[user_id]
    rated_items = user_ratings[user_ratings > 0].index
    collab_scores = item_similarity_df[rated_items].sum(axis=1)
    content_scores = content_sim_df[rated_items].sum(axis=1)
    hybrid_scores = alpha * collab_scores + (1 - alpha) * content_scores
    hybrid_scores = hybrid_scores.drop(labels=rated_items, errors='ignore')
    return hybrid_scores.sort_values(ascending=False).head(num_recommendations).index.tolist()

# --- Product Details + Image ---
def get_product_info(item_id):
    info = product_meta.loc[item_id] if item_id in product_meta.index else {}
    cat = info.get('categoryid', 'Unknown')
    avail = info.get('available', 'Unknown')
    return f"Category: {cat} | Available: {avail}"

def get_product_image(item_id):
    img_path = f"images/{item_id}.jpg"
    if os.path.exists(img_path):
        return Image.open(img_path)
    return Image.open("images/default.jpg")

# --- Streamlit UI ---
st.set_page_config(page_title="🛍️ Retail Recommender", layout="wide")
st.title("🛍️ Retail Product Recommendation System")

# Sidebar Inputs
st.sidebar.header("🔎 User Input")
visitor_id = st.sidebar.text_input("Enter Visitor ID", value="")
rec_type = st.sidebar.selectbox("Recommendation Type", ["Hybrid", "Collaborative", "Content-Based"])
num_recs = st.sidebar.slider("Number of Recommendations", 1, 10, 5)

st.sidebar.markdown("---")
search_item = st.sidebar.text_input("🔍 Search by Item ID")
if search_item:
    try:
        item_id = int(search_item)
        st.sidebar.image(get_product_image(item_id), caption=f"Item {item_id}", use_column_width=True)
        st.sidebar.write(get_product_info(item_id))
    except:
        st.sidebar.warning("Item not found.")

# Main Recommendations
if visitor_id:
    try:
        visitor_id = int(visitor_id)
        st.subheader(f"Recommended Products for Visitor ID: {visitor_id}")

        if rec_type == "Hybrid":
            recommended = get_hybrid_recommendations(visitor_id, num_recommendations=num_recs)
        elif rec_type == "Collaborative":
            recommended = get_collaborative_recommendations(visitor_id, num_recommendations=num_recs)
        else:
            rated = user_item_matrix.loc[visitor_id]
            if rated[rated > 0].empty:
                st.warning("No past interactions to generate content-based recommendations.")
                recommended = []
            else:
                item_id = rated[rated > 0].index[0]
                recommended = get_content_recommendations(item_id, num_recommendations=num_recs)

        if recommended:
            cols = st.columns(len(recommended))
            for i, item_id in enumerate(recommended):
                with cols[i]:
                    st.image(get_product_image(item_id), use_column_width=True)
                    st.caption(f"Item {item_id}")
                    st.markdown(get_product_info(item_id))
        else:
            st.warning("No recommendations available.")
    except:
        st.error("Visitor ID must be numeric.")

# Trending Products Section
st.markdown("---")
st.subheader("🔥 Top Trending Products")

top_trending = user_item_matrix.sum(axis=0).sort_values(ascending=False).head(5).index.tolist()
cols = st.columns(len(top_trending))
for i, item_id in enumerate(top_trending):
    with cols[i]:
        st.image(get_product_image(item_id), use_column_width=True)
        st.caption(f"Item {item_id}")
        st.markdown(get_product_info(item_id))
