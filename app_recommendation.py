# Re-run after reset to generate the final app file with login and filters
login_code = """
import streamlit as st
import pandas as pd
import pickle

users = {"admin": "admin123", "user": "pass123"}
login_successful = False

username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    if username in users and users[username] == password:
        login_successful = True
    else:
        st.error("Invalid username or password")

if login_successful:
    with open('user_item_matrix.pkl', 'rb') as f:
        user_item_matrix = pickle.load(f)
    with open('item_similarity_df.pkl', 'rb') as f:
        item_similarity_df = pickle.load(f)
    with open('content_sim_df.pkl', 'rb') as f:
        content_sim_df = pickle.load(f)

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

    st.title("Product Recommendation System")

    search_query = st.text_input("Search for a product")
    filtered_items = [item for item in content_sim_df.index if search_query.lower() in str(item).lower()]
    category_filter = st.multiselect("Filter by category keyword", ['electronics', 'books', 'fashion', 'home', 'toys'])

    if category_filter:
        filtered_items = [item for item in filtered_items if any(cat in str(item).lower() for cat in category_filter)]

    selected_item = st.selectbox("Choose a product ID:", filtered_items[:50] if filtered_items else content_sim_df.index[:50])

    if selected_item:
        st.subheader("Content-Based Recommendations")
        content_recs = get_content_recommendations(selected_item)
        st.write(content_recs)

        st.subheader("Collaborative Recommendations")
        collab_recs = get_collab_recommendations(selected_item)
        st.write(collab_recs)

        st.subheader("Hybrid Recommendations")
        hybrid_recs = get_hybrid_recommendations(selected_item)
        st.write(hybrid_recs)

        for rec in hybrid_recs:
            st.write(f"Recommended: {rec}")
            st.radio(f"Rate {rec}", ['👍', '👎'], key=f"rating_{rec}")

    st.subheader("Trending Products")
    trending = user_item_matrix.sum(axis=0).sort_values(ascending=False).head(5)
    st.table(trending)
else:
    st.warning("Enter credentials and click Login")
"""

login_output_path = "/mnt/data/app_with_login_and_filters.py"
with open(login_output_path, "w", encoding="utf-8") as f:
    f.write(login_code)

login_output_path
