import streamlit as st
import pandas as pd
from surprise import Reader, Dataset, SVD

@st.cache(allow_output_mutation=True)
def load_model():
    df = pd.read_csv('data/ratings.csv')
    reader = Reader(rating_scale=(df.rating.min(), df.rating.max()))
    data = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)
    items = pd.read_csv('data/items.csv')
    return algo, items

def recommend_for_user(algo, items, user_id, k=10):
    preds = [(iid, algo.predict(user_id, iid).est) for iid in items.item_id.unique()]
    topk = sorted(preds, key=lambda x: x[1], reverse=True)[:k]
    return pd.DataFrame(topk, columns=['item_id','est_rating']).merge(items, on='item_id')

def main():
    st.title("📦 Retail Product Recommender")

    algo, items = load_model()
    user_id = st.sidebar.number_input("User ID", min_value=1, step=1, value=1)

    if st.sidebar.button("Show Top Recommendations"):
        recs = recommend_for_user(algo, items, user_id)
        st.dataframe(recs[['item_id','product_name','est_rating']])

    st.sidebar.write("## OR Predict specific item rating")
    item_id = st.sidebar.number_input("Item ID", min_value=1, step=1, value=1)
    if st.sidebar.button("Predict Rating"):
        est = algo.predict(user_id, item_id).est
        st.write(f"📌 Predicted rating for user {user_id} → item {item_id}: **{est:.2f}**")

if __name__ == "__main__":
    main()
