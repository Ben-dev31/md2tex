#!/usr/bin/env python3
"""
md2tex - Convertisseur Markdown vers LaTeX
Usage en ligne de commande ou comme module Python.
"""

import sys
import os, pathlib
import shutil
import tempfile
import argparse
from parser import MarkdownToLatex, extract_title
import subprocess
import logging
import traceback

logging.basicConfig(level=logging.INFO)

LATEX_DOCUMENT_TEMPLATE = r"""\documentclass[11pt,a4paper]{article}

% Encodage et polices
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[__LANG__]{babel}

% Mise en page
\usepackage{geometry}
\geometry{a4paper, margin=2.5cm}

% Mathématiques avancées
\usepackage{amsmath,amssymb,amsfonts}

% Graphiques et tableaux
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}

% Liens hypertextes
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    citecolor=blue
}

% Texte barré et souligné
\usepackage[normalem]{ulem}

% Blocs de code
\usepackage{listings}
\usepackage{xcolor}

\definecolor{codebg}{rgb}{0.96,0.96,0.96}
\definecolor{codecomment}{rgb}{0.25,0.5,0.35}
\definecolor{codekeyword}{rgb}{0.13,0.13,1}
\definecolor{codestring}{rgb}{0.8,0.1,0.1}

\lstdefinestyle{moderncode}{
    backgroundcolor=\color{codebg},
    commentstyle=\color{codecomment}\textit,
    keywordstyle=\color{codekeyword}\textbf,
    numberstyle=\tiny\color{gray},
    stringstyle=\color{codestring},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,
    breaklines=true,
    captionpos=b,
    keepspaces=true,
    numbers=left,
    numbersep=8pt,
    showspaces=false,
    showstringspaces=false,
    showtabs=false,
    tabsize=4,
    frame=single,
    rulecolor=\color{black!20},
    literate=
      {á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1
      {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1
      {à}{{\`a}}1 {è}{{\`e}}1 {ì}{{\`i}}1 {ò}{{\`o}}1 {ù}{{\`u}}1
      {À}{{\`A}}1 {È}{{\'E}}1 {Ì}{{\`I}}1 {Ò}{{\`O}}1 {Ù}{{\`U}}1
      {ä}{{\"a}}1 {ë}{{\"e}}1 {ï}{{\"i}}1 {ö}{{\"o}}1 {ü}{{\"u}}1
      {Ä}{{\"A}}1 {Ë}{{\"E}}1 {Ï}{{\"I}}1 {Ö}{{\"O}}1 {Ü}{{\"U}}1
      {â}{{\^a}}1 {ê}{{\^e}}1 {î}{{\^i}}1 {ô}{{\^o}}1 {û}{{\^u}}1
      {Â}{{\^A}}1 {Ê}{{\^E}}1 {Î}{{\^I}}1 {Ô}{{\^O}}1 {Û}{{\^U}}1
      {œ}{{\oe}}1 {Œ}{{\OE}}1 {æ}{{\ae}}1 {Æ}{{\AE}}1 {ç}{{\c c}}1
      {Ç}{{\c C}}1 {«}{{\guillemotleft}}1 {»}{{\guillemotright}}1
}
\lstset{style=moderncode}

__METADATA__

\begin{document}

__MAKETITLE__

__BODY__

\end{document}
"""


def detect_title_and_strip(content: str) -> tuple:
    """
    Détecte si le document commence par un titre de niveau 1 (# Mon Titre).
    Retourne (titre_trouve, contenu_sans_le_premier_titre).
    """
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith('# '):
            title = extract_title(line)
            # Retirer cette ligne de titre pour éviter qu'elle soit dupliquée après \maketitle
            remaining_lines = lines[:idx] + lines[idx + 1:]
            return title, "\n".join(remaining_lines)
    return "", content


def convert_markdown_to_latex(
    markdown_content: str,
    standalone: bool = False,
    title: str = "",
    author: str = "",
    date: str = "",
    language: str = "french",
    numbered_sections: bool = True
) -> str:
    r"""
    Convertit une chaîne de caractères Markdown en code LaTeX.

    :param markdown_content: Contenu source au format Markdown.
    :param standalone: Si True, génère un document LaTeX complet (.tex prêt à compiler).
    :param title: Titre du document (optionnel, extrait automatiquement si absent).
    :param author: Auteur du document.
    :param date: Date du document (par défaut aujourd'hui si standalone et titre présent).
    :param language: Langue pour le paquet babel (défaut 'french').
    :param numbered_sections: Si True, numérote les sections (\section vs \section*).
    :return: Code LaTeX généré.
    """
    body_content = markdown_content
    auto_title = ""

    if standalone:
        if not title:
            auto_title, body_content = detect_title_and_strip(markdown_content)
            title = auto_title
        else:
            # Si un titre explicite est donné, on enlève aussi le premier titre # s'il existe
            _, body_content = detect_title_and_strip(markdown_content)

    converter = MarkdownToLatex(
        numbered_sections=numbered_sections,
        default_language=language
    )
    latex_body = converter.parse(body_content)

    if not standalone:
        return latex_body

    # Construction des métadonnées du document autonome
    metadata_lines = []
    maketitle_str = ""

    if title:
        metadata_lines.append(f"\\title{{{converter.escape_latex(title)}}}")
        maketitle_str = "\\maketitle\n\\vspace{1em}\n"
    if author:
        metadata_lines.append(f"\\author{{{converter.escape_latex(author)}}}")
    elif title:
        metadata_lines.append(r"\author{}")
    if date:
        metadata_lines.append(f"\\date{{{converter.escape_latex(date)}}}")
    elif title:
        metadata_lines.append(r"\date{\today}")

    metadata_str = "\n".join(metadata_lines)

    result = LATEX_DOCUMENT_TEMPLATE
    result = result.replace("__LANG__", language)
    result = result.replace("__METADATA__", metadata_str)
    result = result.replace("__MAKETITLE__", maketitle_str)
    result = result.replace("__BODY__", latex_body.strip())

    return result


def convert_file(
    input_path: str,
    output_path: str = None,
    standalone: bool = False,
    title: str = "",
    author: str = "",
    date: str = "",
    language: str = "french",
    numbered: bool = True
) -> str:
    """
    Lit un fichier Markdown, le convertit et enregistre le résultat dans un fichier .tex.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    latex_code = convert_markdown_to_latex(
        content,
        standalone=standalone,
        title=title,
        author=author,
        date=date,
        language=language,
        numbered_sections=numbered
    )

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_code)

    return latex_code


class Converter :
    def __init__(self, **kwargs):
        self.kwargs = kwargs 
        self.template = None 
        self.mdfile_name = kwargs.get("input_file")
        self.file_ext = pathlib.Path(self.mdfile_name).name.split('.')[-1]
        self.base = pathlib.Path(self.mdfile_name).parent
        self.output_file_name = kwargs.get('output_file', pathlib.Path(self.mdfile_name).name.removesuffix(self.file_ext)) 
    
    def convert_to_tex(self, temp_dir = None):
        logging.info(f"Conversion en LaTeX...")
        temp_tex_file = os.path.join(temp_dir, pathlib.Path(self.mdfile_name).name.replace(self.file_ext,'.tex'))
        convert_file(
            input_path=self.mdfile_name,
            output_path=temp_tex_file,
            standalone=True,
            title=self.kwargs.get('title', None),
            author=self.kwargs.get('author', None),
            date=self.kwargs.get('data', None),
            language=self.kwargs.get('lang', None),
            numbered=not argsself.kwargs.get('no_numbering', None)
        )

        return temp_tex_file

    def conver_to_pdf(self, temp_dir, temp_tex_file):
        logging.info(f"Compilation en PDF...")
        subprocess.run(
            [
                pdflatex,
                "-interaction=nonstopmode",
                "-output-directory",
                temp_dir,
                temp_tex_file
            ],
            check=True
        ) 
    
    def run(self, mode='tex'):
        if mode == 'tex':
            self.convert_to_tex()


def main():
    parser = argparse.ArgumentParser(
        description="Convertit un fichier Markdown (.md) en fichier LaTeX (.tex)."
    )
    parser.add_argument(
        "--input",
        help="Chemin vers le fichier Markdown (.md) à convertir."
    )
    parser.add_argument(
        "-o", "--output",
        default='tex',
        help="type de sortie (.tex, .pdf). Par défaut: <nom_du_fichier>.tex"
    )
    parser.add_argument(
        "-s", "--standalone",
        action="store_true",
        default=False,
        help="Génère un document LaTeX complet et autonome avec préambule et paquetages requis."
    )
    parser.add_argument(
        "-t", "--title",
        default="",
        help="Titre du document (si absent et en mode autonome, déduit du premier '# Titre')."
    )
    parser.add_argument(
        "-a", "--author",
        default="",
        help="Nom de l'auteur du document."
    )
    parser.add_argument(
        "-d", "--date",
        default="",
        help="Date du document (ex: '24 novembre 2026' ou '\\today')."
    )
    parser.add_argument(
        "--lang",
        default="french",
        help="Langue pour le paquet babel (défaut: french)."
    )
    parser.add_argument(
        "--no-numbering",
        action="store_true",
        default=False,
        help="Désactive la numérotation des sections (\\section* au lieu de \\section)."
    )

    args = parser.parse_args()

    input_file = args.input
    if not os.path.isfile(input_file):
        logging.error(f"Erreur : Le fichier '{input_file}' n'existe pas.")
        sys.exit(1)

    base, _ = os.path.splitext(input_file)
    output_tex_file = base + ".tex"

    output_type = args.output

    try:
        if output_type == 'pdf':
            pdflatex = shutil.which("pdflatex")
            if pdflatex is None:
                logging.error(
                    "Impossible de générer le PDF : 'pdflatex' est introuvable. "
                    "Installez MiKTeX ou TeX Live et ajoutez pdflatex au PATH."
                )
                sys.exit(1)

            tex_name = os.path.basename(base) + "_temp.tex"
            logging.info(f"Conversion en LaTeX ({tex_name})...")
            with tempfile.TemporaryDirectory(prefix="md2tex_") as temp_dir:
                temp_tex_file = os.path.join(temp_dir, tex_name)
                convert_file(
                    input_path=input_file,
                    output_path=temp_tex_file,
                    standalone=True,
                    title=args.title,
                    author=args.author,
                    date=args.date,
                    language=args.lang,
                    numbered=not args.no_numbering
                )

                logging.info(f"Compilation en PDF ({tex_name})...")
                subprocess.run(
                    [
                        pdflatex,
                        "-interaction=nonstopmode",
                        "-output-directory",
                        temp_dir,
                        temp_tex_file
                    ],
                    check=True
                )

                generated_pdf = os.path.join(temp_dir, os.path.splitext(tex_name)[0] + ".pdf")
                shutil.move(generated_pdf, base + ".pdf")
                shutil.move(temp_tex_file, output_tex_file)
            output_file = base + ".pdf"
        else:
            convert_file(
                input_path=input_file,
                output_path=output_tex_file,
                standalone=args.standalone,
                title=args.title,
                author=args.author,
                date=args.date,
                language=args.lang,
                numbered=not args.no_numbering
            )
            output_file = output_tex_file
        mode_str = "document autonome" if args.standalone or output_type == 'pdf' else "fragment"
        logging.info(f"Succès : '{input_file}' a été converti en '{output_file}' ({mode_str}).")
    except Exception as e:
        logging.error(f"Erreur lors de la conversion : {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
