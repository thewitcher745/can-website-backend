import os
import glob
import yaml
from flask import Flask, jsonify, abort
from markdown import markdown

BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog_posts')

app = Flask(__name__)


def parse_markdown_file(filepath):
	# Read the file content and return the metadata and markdown content
	with open(filepath, 'r', encoding='utf-8') as f:
		content = f.read()
	if content.startswith('---'):
		parts = content.split('---', 2)
		if len(parts) >= 3:
			meta = yaml.safe_load(parts[1])
			md_content = parts[2].strip()
		else:
			meta = {}
			md_content = content
	else:
		meta = {}
		md_content = content
	return meta, md_content


def get_slug(filename):
	# Extract the slug from the filename
	return os.path.splitext(os.path.basename(filename))[0]


@app.route('/api/blog/', methods=['GET'])
def list_posts():
	# List all blog posts
	posts = []
	for filepath in glob.glob(os.path.join(BLOG_DIR, '*.md')):
		meta, _ = parse_markdown_file(filepath)
		slug = get_slug(filepath)
		post = {
			'slug': slug,
			'title': meta.get('title', slug),
			'date': meta.get('date', ''),
			'author': meta.get('author', ''),
			'tags': meta.get('tags', []),
		}
		posts.append(post)
	posts.sort(key=lambda x: x['date'], reverse=True)
	return jsonify(posts)


@app.route('/api/blog/<slug>', methods=['GET'])
def get_post(slug):
	# Get a specific blog post
	filepath = os.path.join(BLOG_DIR, f'{slug}.md')
	if not os.path.isfile(filepath):
		abort(404)
	meta, md_content = parse_markdown_file(filepath)
	html_content = markdown(md_content)
	post = {
		'slug': slug,
		'title': meta.get('title', slug),
		'date': meta.get('date', ''),
		'author': meta.get('author', ''),
		'tags': meta.get('tags', []),
		'content_html': html_content,
	}
	return jsonify(post)


if __name__ == '__main__':
	import os
	port = int(os.environ.get("PORT", 5000))
	app.run(debug=True, host='0.0.0.0', port=port)
