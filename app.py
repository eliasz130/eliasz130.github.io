from flask import Flask, render_template, abort, request
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Ensure the posts file exists
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'posts.json')
if not os.path.exists(POSTS_FILE):
    with open(POSTS_FILE, 'w') as f:
        json.dump([], f)


def load_posts():
    """Load posts from the JSON file."""
    try:
        with open(POSTS_FILE) as f:
            posts = json.load(f)
            # Validate posts
            for post in posts:
                if not all(key in post for key in ('id', 'title', 'content', 'date')):
                    raise ValueError("Invalid post structure")
            return posts
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return []


def save_posts(posts):
    """Save posts to the JSON file."""
    try:
        with open(POSTS_FILE, 'w') as f:
            json.dump(posts, f, indent=4)
    except IOError as e:
        print(f"Error saving posts: {e}")


@app.route('/blog')
def home():
    """Render the homepage with paginated posts."""
    posts = load_posts()
    posts.sort(key=lambda x: x['date'], reverse=True)
    page = int(request.args.get('page', 1))
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = posts[start:end]
    return render_template('blog/home.html', posts=paginated_posts, page=page, total_pages=(len(posts) + per_page - 1) // per_page)


@app.route('/blog/post/<int:post_id>')
def post_detail(post_id):
    """Render the details of a specific post."""
    posts = load_posts()
    post = next((post for post in posts if post['id'] == post_id), None)
    if post is None:
        abort(404)
    return render_template('blog/post_detail.html', post=post)


@app.route('/blog/about')
def about():
    """Render the About page."""
    return render_template('blog/about.html')


@app.context_processor
def inject_year():
    """Inject the current year into templates."""
    return {'year': datetime.now().year}


if __name__ == '__main__':
    app.run(debug=True)
