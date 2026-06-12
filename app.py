from flask import Flask, render_template, request
from datetime import datetime
import pickle
import numpy as np
from fuzzywuzzy import process

popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))




app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author = list(popular_df['Book-Author'].values),
                           image = list(popular_df['Image-URL-L'].values),
                           votes = list(popular_df['num_ratings'].values),
                           rating = list(popular_df['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_request', methods=['POST'])
def submit_request():
    book = request.form.get('book_name')

    if book:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open('book_requests.csv', 'a', encoding='utf-8') as f:
            f.write(f'{book.strip()},{timestamp}\n')

        success = f'Thank you! Your request for "{book}" has been recorded.'
    else:
        success = 'Please enter a valid book name.'

    return render_template('contact.html', success=success)

@app.route('/requests')
def view_requests():
    books = []

    try:
        with open('book_requests.csv', 'r', encoding='utf-8') as f:
            books = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        pass

    return render_template('requests.html', books=books)

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    match = process.extractOne(user_input, pt.index)

    if match is None:
        return render_template(
            'recommend.html',
            error='No similar book found.'
        )

    book_name = match[0]
    score = match[1]

    if score < 60:
        return render_template(
            'recommend.html',
            error='No close match found.'
        )

    index = np.where(pt.index == book_name)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    data = []

    for i in similar_items:
        item = []

        temp_df = books[
            books['Book-Title'] == pt.index[i[0]]
        ]

        item.extend(
            list(temp_df.drop_duplicates('Book-Title')['Book-Title'])
        )

        item.extend(
            list(temp_df.drop_duplicates('Book-Title')['Book-Author'])
        )

        item.extend(
            list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'])
        )

        data.append(item)

    return render_template(
        'recommend.html',
        data=data,
        matched_book=book_name
    )
import pickle

popular_df = pickle.load(open('popular.pkl', 'rb'))

print(popular_df.columns)
if __name__ == '__main__':
    app.run(debug=True)
