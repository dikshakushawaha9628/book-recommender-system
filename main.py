from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
from fuzzywuzzy import process

pt = pickle.load(open("pt.pkl", "rb"))
books = pickle.load(open("books.pkl", "rb"))
similarity_scores = pickle.load(open("similarity_scores.pkl", "rb"))

app = FastAPI()


class BookRequest(BaseModel):
    book_name: str


@app.get("/")
def home():
    return {"message": "Book Recommender API is running"}


@app.post("/recommend")
def recommend(req: BookRequest):
    user_input = req.book_name

    match = process.extractOne(user_input, pt.index)

    if match is None:
        return {"error": "No similar book found"}

    matched_book = match[0]
    index = np.where(pt.index == matched_book)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommendations = []

    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        recommendations.append({
            "title": temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0],
            "author": temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
            "image": temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0]
        })

    return {
        "matched_book": matched_book,
        "recommendations": recommendations
    }