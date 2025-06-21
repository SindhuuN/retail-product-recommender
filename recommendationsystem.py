
import streamlit as st
import pandas as pd
import pickle

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

st.header("Get Product Recommendations")
item_input = st.selectbox("Choose a product ID:", content_sim_df.index[:50])

if item_input:
    st.subheader("Content-Based Recommendations")
    st.write(get_content_recommendations(item_input))

    st.subheader("Collaborative Recommendations")
    st.write(get_collab_recommendations(item_input))

    st.subheader("Hybrid Recommendations")
    st.write(get_hybrid_recommendations(item_input))
