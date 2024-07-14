import os
import click

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'\
        + os.path.join(app.root_path, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

blog_data = {
    "Computer Science": {
        "OS": ["MIT 6.828", "Andoriod"],
        "Network": ["Protocols"],
        "Hack": ["Web Penetraion", "DoS"],
        "Quantum Computation": ["Algorithms", "Programming"],
    },
    "Chess": {
        "Opening": ["Sicilian", "Scotland", "English"],
        "Tactics": ["Decoy&Deflection", "Stalemate"],
        "Endgame": ["Pawn and King"],
        "Positional": ["Exchange", "Sacrifice"],
        "Books": ["Fischer: My 60 memorable games", "Nimzowitsch: My system"],
    },
}


class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)


class Subtheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    theme = db.Column(db.String(20))


class Subsubtheme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    theme = db.Column(db.String(20))
    subtheme = db.Column(db.String(20))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    theme = db.Column(db.String(20))
    subtheme = db.Column(db.String(20))
    subsubtheme = db.Column(db.String(20))
    time = db.Column(db.DateTime, default=db.func.current_timestamp())


@app.route('/')
def home():
    return render_template('index.html', themes=blog_data.keys())


@app.route('/<theme>.html')
def theme(theme):
    if theme in blog_data:
        subthemes = blog_data[theme]

        return render_template('theme.html',
                               theme=theme,
                               subthemes=subthemes.keys())

    return render_template('404.html')


@app.route('/<theme>/<subtheme>.html')
def subtheme(theme, subtheme):
    if theme in blog_data\
     and subtheme in blog_data[theme].keys():
        subsubthemes = blog_data[theme][subtheme]
        return render_template('subtheme.html',
                               theme=theme,
                               subtheme=subtheme,
                               subsubthemes=subsubthemes)


@app.route('/<theme>/<subtheme>/<subsubtheme>.html')
def subsubtheme(theme, subtheme, subsubtheme):
    if theme in blog_data\
     and subtheme in blog_data[theme].keys()\
     and subsubtheme in blog_data[theme][subtheme]:
        articles = Article.query.filter_by(
                    theme=theme,
                    subtheme=subtheme,
                    subsubtheme=subsubtheme
                )
        return render_template('subsubtheme.html',
                               theme=theme,
                               subtheme=subtheme,
                               subsubtheme=subsubtheme,
                               articles=articles)


@app.route('/<theme>/<subtheme>/<subsubtheme>/<article_id>.html')
def article(theme, subtheme, subsubtheme, article_id):
    if theme in blog_data\
     and subtheme in blog_data[theme].keys()\
     and subsubtheme in blog_data[theme][subtheme]:
        article = Article.query.filter_by(id=article_id).first()
        if article:
            return render_template(f'articles/{article.id}-{article.name}.html',
                                   theme=theme,
                                   subtheme=subtheme,
                                   subsubtheme=subsubtheme,
                                   article=article)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.cli.command()
def init():
    db.create_all()
    click.echo("Initialized database.")


@app.cli.command()
@click.option('--theme')
def new_theme(theme):
    this = Theme(
            name=theme
        )
    db.session.add(this)
    db.session.commit()
    click.echo(f'Create theme {theme}.')


@app.cli.command()
@click.option('--theme')
@click.option('--subtheme')
def new_subtheme(theme, subtheme):
    this = Subtheme(
            name=subtheme,
            theme=theme
        )
    db.session.add(this)
    db.session.commit()
    click.echo(f'Create subtheme {subtheme} under {theme}.')


@app.cli.command()
@click.option('--theme')
@click.option('--subtheme')
@click.option('--subsubtheme')
def new_subsubtheme(theme, subtheme, subsubtheme):
    this = Subsubtheme(
            name=subsubtheme,
            theme=theme,
            subtheme=subtheme
        )
    db.session.add(this)
    db.session.commit()
    click.echo(f'Create subsubtheme {subsubtheme} under {theme}/{subtheme}.')


@app.cli.command()
@click.option('--theme')
@click.option('--subtheme')
@click.option('--subsubtheme')
@click.option('--article')
def new_article(theme, subtheme, subsubtheme, article):
    this = Article(
            name=article,
            theme=theme,
            subtheme=subtheme,
            subsubtheme=subsubtheme
        )
    db.session.add(this)
    db.session.commit()

    with open(os.path.join(
        app.root_path, f'templates/articles/{this.id}-{article}.html'
            ), 'w') as f:

        f.write("{% extends 'article.html' %}")
        f.write("\n")
        f.write("{% block content %}")
        f.write("\n\n\n")
        f.write("{% endblock %}")

    click.echo(
            f'Create article {article} under {theme}/{subtheme}/{subsubtheme}.'
            )


@app.cli.command()
@click.option('--theme', is_flag=True)
@click.option('--subtheme', is_flag=True)
@click.option('--subsubtheme', is_flag=True)
@click.option('--article', is_flag=True)
def show(theme, subtheme, subsubtheme, article):
    if theme:
        click.echo('- [All Themes]')
        themes = Theme.query.all()
        for item in themes:
            print(f'-- id={item.id}, name={item.name}')
        click.echo('- [End]')
        click.echo('\n')

    if subtheme:
        click.echo('- [All Subthemes]')
        subthemes = Subtheme.query.all()
        for item in subthemes:
            print(f'-- id={item.id}, name={item.name}, theme={item.theme}')
        click.echo('- [End]')
        click.echo('\n')

    if subsubtheme:
        click.echo('- [All Subsubthemes]')
        subsubthemes = Subsubtheme.query.all()
        for item in subsubthemes:
            print(f'-- id={item.id}, name={item.name}, theme={item.theme},'
                  f' subtheme={item.subtheme}')
        click.echo('- [End]')
        click.echo('\n')

    if article:
        click.echo('- [All Articles]')
        articles = Article.query.all()
        for item in articles:
            print(f'-- id={item.id}, name={item.name}, theme={item.theme},'
                  f' subtheme={item.subtheme}, subsubtheme={item.subsubtheme}')
        click.echo('- [End]')
        click.echo('\n')
