import os
import glob
import yaml
from flask import Flask, jsonify, abort
from flask_cors import CORS
from markdown import markdown
from dateutil import parser
from datetime import datetime

BLOG_DIR = os.path.join(os.path.dirname(__file__), 'blog_posts')
ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), 'analysis_posts')

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes


def parse_blog_markdown_file(filepath):
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


def parse_datetime(time_str):
	if not time_str:
		return datetime.min
	try:
		return parser.parse(time_str)
	except (ValueError, TypeError):
		return datetime.min

def format_datetime(dt):
	"""Format datetime object to string in ISO format"""
	if dt == datetime.min:
		return ''
	return dt.isoformat()


@app.route('/api/blog/', methods=['GET'])
def list_posts():
	# List all blog posts
	posts = []
	for filepath in glob.glob(os.path.join(BLOG_DIR, '*.md')):
		meta, _ = parse_blog_markdown_file(filepath)
		slug = get_slug(filepath)
		post = {
			'slug': slug,
			'title': meta.get('title', slug),
			'time': parse_datetime(meta.get('time', '')),
			'author': meta.get('author', ''),
			'tags': meta.get('tags', []),
			'desc': meta.get('desc', ''),
		}
		posts.append(post)
	posts.sort(key=lambda x: x['time'], reverse=True)
	return jsonify(posts)


@app.route('/api/blog/<slug>', methods=['GET'])
def get_post(slug):
	# Get a specific blog post
	filepath = os.path.join(BLOG_DIR, f'{slug}.md')
	if not os.path.isfile(filepath):
		abort(404)
	meta, md_content = parse_blog_markdown_file(filepath)
	html_content = markdown(md_content)
	post = {
		'slug': slug,
		'title': meta.get('title', slug),
		'time': meta.get('time', ''),
		'author': meta.get('author', ''),
		'tags': meta.get('tags', []),
		'desc': meta.get('desc', ''),
		'content_html': html_content,
	}
	return jsonify(post)


@app.route('/')
def hello():
	return jsonify('The CAN platform backend API branches off here!')


@app.route('/api/analysis/', methods=['GET'])
def list_analysis_posts():
	# List all analysis posts, sorted by latest update time
	posts = []
	for filepath in glob.glob(os.path.join(ANALYSIS_DIR, '*.md')):
		sections = parse_multi_markdown_file(filepath)
		if not sections:
			continue
		# Use the last metadata section for the latest update
		latest_meta = sections[-1]['meta'] if 'meta' in sections[-1] else {}
		first_meta = sections[0]['meta'] if 'meta' in sections[0] else {}
		slug = get_slug(filepath)
		post = {
			'slug': slug,
			'title': first_meta.get('title', slug),
			'time': format_datetime(parse_datetime(latest_meta.get('time', ''))),  # Use latest update time
			'thumbnail_link': first_meta.get('thumbnail_link', ''),
			'author': first_meta.get('author', ''),
			'tags': first_meta.get('tags', []),
			'desc': first_meta.get('desc', ''),
		}
		posts.append(post)
	posts.sort(key=lambda x: x['time'], reverse=True)
	return jsonify(posts)


def parse_multi_markdown_file(filepath):
	"""
	Parse a markdown file with multiple YAML sections (---). Returns a list of dicts:
	[{meta: ..., body: ...}, ...]
	"""
	with open(filepath, 'r', encoding='utf-8') as f:
		content = f.read()
	sections = content.split('---')
	results = []
	idx = 1 if sections[0].strip() == '' else 0
	while idx < len(sections) - 1:
		meta = yaml.safe_load(sections[idx]) if sections[idx].strip() else {}
		body = sections[idx + 1].strip() if idx + 1 < len(sections) else ''
		results.append({'meta': meta, 'body': body})
		idx += 2
	return results


@app.route('/api/analysis/<slug>', methods=['GET'])
def get_analysis_post(slug):
	# Get a specific analysis post (main + updates)
	filepath = os.path.join(ANALYSIS_DIR, f'{slug}.md')
	if not os.path.isfile(filepath):
		abort(404)
	sections = parse_multi_markdown_file(filepath)
	results = []
	for i, section in enumerate(sections):
		meta = section.get('meta', {})
		body = section.get('body', '')
		item = {'content_html': markdown(body)}
		if i == 0:
			item.update(
				{
					'slug': slug,
					'title': meta.get('title', slug),
					'time': meta.get('time', ''),
					'author': meta.get('author', ''),
					'tags': meta.get('tags', []),
					'desc': meta.get('desc', ''),
				}
			)
		else:
			item['time'] = meta.get('time', '')
		results.append(item)
	return jsonify(results)


if __name__ == '__main__':
	import os

	port = int(os.environ.get('PORT', 5000))
	app.run(debug=True, host='0.0.0.0', port=port)
