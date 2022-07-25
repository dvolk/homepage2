"""homepage2 - Static site generator."""

import pathlib
import datetime
import re
import argparse
import subprocess
import shutil
import sys
import logging

import jinja2
import pygments
import pygments.lexers
import pygments.formatters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")


def create_href(*args):
    """Concat args and remove characters to create appropriate href tag."""
    return re.sub(r"[\W+]", "_", "_".join(args))


def icon(name):
    """Fontawesome icon helper."""
    return f'<i class="fa fa-{name} fa-fw"></i>'


def check_prereqs(prereqs):
    """Check if given binaries exist."""
    for prereq in prereqs:
        if not shutil.which(prereq):
            logging.critical("You need {prereq} to run this.")
            sys.exit(1)


def set_blog_entry_data(blog_title, blog_date):
    global glob_blog_title
    glob_blog_title = blog_title
    global glob_blog_date
    glob_blog_date = blog_date


def get_blog_entry_data():
    return glob_blog_title, glob_blog_date


pygments_html_formatter = pygments.formatters.HtmlFormatter(style="colorful")
pygments_html_formatter_css = pygments_html_formatter.get_style_defs()


def pygments_code_block(code_text, language_name):
    """Issue html formatting code."""
    if language_name.lower() == "python":
        lexer = pygments.lexers.PythonLexer()
    elif language_name.lower() == "nim":
        lexer = pygments.lexers.NimrodLexer()
    elif language_name.lower() == "c":
        lexer = pygments.lexers.CLexer()
    return pygments.highlight(code_text, lexer, pygments_html_formatter)


def save_blog_entry(blog_title, blog_date, blog_content):
    """Save blog entry html in a separate file."""
    href = create_href(blog_date, blog_title)
    out_filename = content_dir / pathlib.Path(href).with_suffix(".html")
    in_text = (
        """{% """
        f'set title = "{ blog_title }"'  # ?
        """ %}"""
        """
{% extends 'static/base.j2' %}

{% block content %}
{{ blog_content }}
{% endblock %}
"""
    )
    logging.info(f"BLOG ENTRY {blog_title} -> {out_filename}")
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(content_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    ).from_string(
        in_text,
    )
    out_text = template.render(
        now=datetime.datetime.now(),
        icon=icon,
        create_href=create_href,
        blog_title=blog_title,
        blog_date=blog_date,
        blog_content=blog_content,
        pygments_code_block=pygments_code_block,
        pygments_html_formatter_css=pygments_html_formatter_css,
        set_blog_entry_data=set_blog_entry_data,
        get_blog_entry_data=get_blog_entry_data,
        is_blog_page=True,
    )
    open(out_filename, "w").write(out_text)
    return ""


def main(content_dir2):
    """Parse a content directory and write out files to content-out dir."""
    global content_dir
    content_dir = pathlib.Path(content_dir2)
    check_prereqs(["rsync"])

    for p in content_dir.glob("*.j2"):
        in_text = open(p).read()
        template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(content_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        ).from_string(
            in_text,
        )
        out_text = template.render(
            now=datetime.datetime.now(),
            icon=icon,
            create_href=create_href,
            save_blog_entry=save_blog_entry,
            pygments_code_block=pygments_code_block,
            pygments_html_formatter_css=pygments_html_formatter_css,
            set_blog_entry_data=set_blog_entry_data,
            get_blog_entry_data=get_blog_entry_data,
            is_blog_page=False,
        )
        out_filename = p.with_suffix(".html")
        logging.info(f"{p} -> {out_filename}")
        open(out_filename, "w").write(out_text)

    subprocess.check_output(["rsync", "-aXxv", f"{content_dir}/", f"{content_dir}-out"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("content_dir")
    args = parser.parse_args()
    main(args.content_dir)
