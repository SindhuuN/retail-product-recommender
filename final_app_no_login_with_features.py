
import streamlit as st
import pandas as pd
import pickle
import os
import json

# -------------------------------
# Dummy Utilities
# -------------------------------
def get_image_url(item_id):
    return f"https://via.placeholder.com/150?text=Item+{item_id}"

def get_description(item_id):
    return f"This is a description for product {item_id}. It belongs to one or more interesting categories."

# -------------------------------
# Rating Storage Utilities
# -------------------------------
def load_ratings():
    if os.path.exists("ratings.json"):
        with open("ratings.json", "r") as f:
            return json.load(f)
    return {}

def save_rating(item_id, rating):
    ratings = load_ratings()
    if item_id not in ratings:
        ratings[item_id] = []
    ratings[item_id].append(rating)
    with open("ratings.json", "w") as f:
        json.dump(ratings, f)

def average_rating(item_id):
    ratings = load_ratings()
    if item_id in ratings:
        values = [1 if r == "👍" else 0 for r in ratings[item_id]]
        return sum(values) / len(values)
    return None

# -------------------------------
# Load Data
# -------------------------------
st.title("🛍️ Product Recommendation System (No Login)")

with open('user_item_matrix.pkl', 'rb') as f:
    user_item_matrix = pickle.load(f)
with open('item_similarity_df.pkl', 'rb') as f:
    item_similarity_df = pickle.load(f)
with open('content_sim_df.pkl', 'rb') as f:
    content_sim_df = pickle.load(f)

# -------------------------------
# Recommendation Functions
# -------------------------------
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

# -------------------------------
# Filters and Sorting
# -------------------------------
search_query = st.text_input("🔍 Search for a product")
filtered_items = [item for item in content_sim_df.index if search_query.lower() in str(item).lower()]
category_filter = st.multiselect("Filter by category keyword", ['electronics', 'books', 'fashion', 'home', 'toys'])

if category_filter:
    filtered_items = [item for item in filtered_items if any(cat in str(item).lower() for cat in category_filter)]

selected_item = st.selectbox("Choose a product ID:", filtered_items[:50] if filtered_items else content_sim_df.index[:50])
sort_option = st.selectbox("Sort recommendations by", ['Default', 'Highest Avg Rating', 'Most Similar'])

# -------------------------------
# Display Recommendations
# -------------------------------
if selected_item:
    st.image(get_image_url(selected_item), caption=f"Selected Product: {selected_item}")
    st.write(get_description(selected_item))

    def display_items(item_list, title):
        st.subheader(title)
        for item in item_list:
            st.image(get_image_url(item), width=100)
            st.write(f"**Product:** {item}")
            st.write(get_description(item))
            avg = average_rating(item)
            if avg is not None:
                st.write(f"Average Rating: {'⭐' * round(avg * 5)} ({avg:.2f})")
            rate = st.radio(f"Rate {item}", ['👍', '👎'], key=f"rate_{item}")
            if st.button(f"Submit Rating for {item}", key=f"submit_{item}"):
                save_rating(item, rate)
                st.success(f"Rating saved: {rate}")

    # Generate and optionally sort recommendations
    hybrid_recs = get_hybrid_recommendations(selected_item)
    if sort_option == 'Highest Avg Rating':
        hybrid_recs = sorted(hybrid_recs, key=lambda x: average_rating(x) or 0, reverse=True)
    elif sort_option == 'Most Similar':
        hybrid_recs = get_content_recommendations(selected_item)

    display_items(hybrid_recs, "💡 Hybrid Recommendations")

# -------------------------------
# Trending Section
# -------------------------------
st.subheader("🔥 Trending Products")
trending = user_item_matrix.sum(axis=0).sort_values(ascending=False).head(5)
for item_id in trending.index:
    st.image(get_image_url(item_id), width=100)
    st.write(f"{item_id} — Interactions: {trending[item_id]}")
    st.write(get_description(item_id))
