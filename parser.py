"""
Markdown to LaTeX Parser and Converter
Transforme un fichier ou texte Markdown en code LaTeX compatible.
"""

import re
from typing import List, Tuple, Optional


def find_title(line: str) -> bool:
    """
    Vérifie si une ligne est un titre Markdown de niveau 1.
    Conservé pour la compatibilité avec le code existant.
    """
    return line.strip().startswith('# ')


def extract_title(line: str) -> str:
    """Extrait le texte du titre d'une ligne Markdown."""
    stripped = line.strip()
    return re.sub(r'^#+\s*', '', stripped).strip()


class MarkdownToLatex:
    """
    Convertisseur Markdown vers LaTeX supportant :
    - Titres (# à ######)
    - Mathématiques en ligne ($...$) et en bloc ($$...$$)
    - Blocs de code avec coloration syntaxique (listings)
    - Code en ligne (`...`)
    - Gras, italique, barré (**, *, ~~, __, _)
    - Listes ordonnées et non ordonnées (avec imbrication)
    - Citations (> ...)
    - Tableaux Markdown
    - Liens [texte](url) et images ![alt](chemin)
    - Lignes horizontales (---)
    - Échappement sécurisé des caractères spéciaux LaTeX
    """

    def __init__(self, numbered_sections: bool = True, default_language: str = "french"):
        self.numbered_sections = numbered_sections
        self.default_language = default_language

    def escape_latex(self, text: str) -> str:
        """
        Échappe les caractères réservés de LaTeX dans le texte ordinaire,
        tout en évitant d'échapper les commandes déjà générées.
        """
        # Ordre important : \ d'abord si présent hors commandes
        text = text.replace('\\', r'\textbackslash{}')
        text = text.replace('&', r'\&')
        text = text.replace('%', r'\%')
        text = text.replace('#', r'\#')
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        text = text.replace('^', r'\textasciicircum{}')
        text = text.replace('~', r'\textasciitilde{}')
        return text

    def escape_for_texttt(self, text: str) -> str:
        """Échappe le texte destiné à être rendu dans \\texttt{...}."""
        replacements = [
            ('\\', r'\textbackslash{}'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('_', r'\_'),
            ('&', r'\&'),
            ('%', r'\%'),
            ('#', r'\#'),
            ('^', r'\textasciicircum{}'),
            ('~', r'\textasciitilde{}'),
            ('$', r'\$'),
        ]
        for src, target in replacements:
            text = text.replace(src, target)
        return text

    def convert_inline(self, text: str) -> str:
        """
        Convertit le formatage inline Markdown en LaTeX :
        - Préserve les formules mathématiques
        - Protège le code inline
        - Traite le gras, l'italique, le barré
        - Convertit les liens et images
        - Échappe les caractères spéciaux
        """
        if not text:
            return ""

        math_tokens: List[str] = []
        code_tokens: List[str] = []
        link_tokens: List[Tuple[str, str]] = []
        image_tokens: List[Tuple[str, str]] = []

        # 1. Protéger les formules mathématiques en ligne : $...$
        def store_math(match):
            token = f"XXMD2TEXMATH{len(math_tokens)}XX"
            math_tokens.append(match.group(1))
            return token

        text = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', store_math, text)

        # 2. Protéger le code inline : `...`
        def store_code(match):
            token = f"XXMD2TEXCODE{len(code_tokens)}XX"
            code_tokens.append(match.group(1))
            return token

        text = re.sub(r'`([^`\n]+)`', store_code, text)

        # 3. Protéger les images : ![alt](url)
        def store_image(match):
            token = f"XXMD2TEXIMG{len(image_tokens)}XX"
            image_tokens.append((match.group(1), match.group(2)))
            return token

        text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', store_image, text)

        # 4. Protéger les liens : [text](url)
        def store_link(match):
            token = f"XXMD2TEXLNK{len(link_tokens)}XX"
            link_tokens.append((match.group(1), match.group(2)))
            return token

        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', store_link, text)

        # 5. Échapper les caractères spéciaux LaTeX dans le texte restant
        # Attention : ne pas échapper les * et _ nécessaires au Markdown
        special_chars = [
            ('&', r'\&'),
            ('%', r'\%'),
            ('#', r'\#'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('^', r'\textasciicircum{}'),
        ]
        for src, target in special_chars:
            text = text.replace(src, target)

        # Échapper les dollars isolés non fermés ou échappés
        text = text.replace(r'\$', r'__ESCAPED_DOLLAR__')
        text = text.replace('$', r'\$')
        text = text.replace('__ESCAPED_DOLLAR__', r'\$')

        # 6. Formatage Markdown inline
        # Barré: ~~texte~~
        text = re.sub(r'~~(.*?)~~', r'\\sout{\1}', text)

        # Gras et Italique: ***texte*** ou ___texte___
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
        text = re.sub(r'___(.*?)___', r'\\textbf{\\textit{\1}}', text)

        # Gras: **texte** ou __texte__
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'__(.*?)__', r'\\textbf{\1}', text)

        # Italique: *texte*
        text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)

        # Italique avec underscore: _texte_ (entouré d'espaces, ponctuation ou début/fin de chaîne)
        text = re.sub(r'(^|[\s\(\[\{,\.:;!?])_([^_]+)_(?=[\s\)\]\},\.:;!?]|$)', r'\1\\textit{\2}', text)

        # 7. Échapper les underscores restants (noms de variables, etc. e.g. foo_bar -> foo\_bar)
        text = text.replace('_', r'\_')

        # 8. Restaurer les images
        for i, (alt, url) in enumerate(image_tokens):
            img_latex = (
                f"\\begin{{figure}}[htbp]\n"
                f"\\centering\n"
                f"\\includegraphics[max width=\\linewidth]{{{url}}}\n"
                f"\\caption{{{self.escape_latex(alt)}}}\n"
                f"\\end{{figure}}"
            )
            text = text.replace(f"XXMD2TEXIMG{i}XX", img_latex)

        # 9. Restaurer les liens
        for i, (label, url) in enumerate(link_tokens):
            clean_label = self.convert_inline(label)
            # Dans href, échapper les % et #
            clean_url = url.replace('%', r'\%').replace('#', r'\#')
            link_latex = f"\\href{{{clean_url}}}{{{clean_label}}}"
            text = text.replace(f"XXMD2TEXLNK{i}XX", link_latex)

        # 10. Restaurer le code inline
        for i, code in enumerate(code_tokens):
            escaped_code = self.escape_for_texttt(code)
            code_latex = f"\\texttt{{{escaped_code}}}"
            text = text.replace(f"XXMD2TEXCODE{i}XX", code_latex)

        # 11. Restaurer les formules mathématiques
        for i, math in enumerate(math_tokens):
            math_latex = f"${math}$"
            text = text.replace(f"XXMD2TEXMATH{i}XX", math_latex)

        return text

    def convert_heading(self, line: str) -> str:
        """Convertit une ligne de titre (# ...) en commande de section LaTeX."""
        match = re.match(r'^(#{1,6})\s+(.*)$', line.strip())
        if not match:
            return self.convert_inline(line)

        level = len(match.group(1))
        title = self.convert_inline(match.group(2).strip())
        star = "" if self.numbered_sections else "*"

        heading_map = {
            1: f"\\section{star}{{{title}}}",
            2: f"\\subsection{star}{{{title}}}",
            3: f"\\subsubsection{star}{{{title}}}",
            4: f"\\paragraph{star}{{{title}}}",
            5: f"\\subparagraph{star}{{{title}}}",
            6: f"\\subparagraph{star}{{{title}}}"
        }
        return heading_map.get(level, f"\\textbf{{{title}}}")

    def convert_table(self, lines: List[str]) -> str:
        """Convertit un bloc de tableau Markdown en environnement tabular LaTeX."""
        if len(lines) < 2:
            return "\n".join(self.convert_inline(line) for line in lines)

        # Extraction des lignes et cellules
        rows = []
        for line in lines:
            line = line.strip()
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]
            cells = [c.strip() for c in line.split('|')]
            rows.append(cells)

        if len(rows) < 2:
            return ""

        headers = rows[0]
        delimiter_row = rows[1]
        data_rows = rows[2:]

        # Analyse des alignements
        col_aligns = []
        for cell in delimiter_row:
            cell = cell.strip()
            if cell.startswith(':') and cell.endswith(':'):
                col_aligns.append('c')
            elif cell.endswith(':'):
                col_aligns.append('r')
            else:
                col_aligns.append('l')

        col_count = len(headers)
        # S'assurer que les alignements correspondent au nombre de colonnes
        while len(col_aligns) < col_count:
            col_aligns.append('l')
        col_spec = "|" + "|".join(col_aligns[:col_count]) + "|"

        latex_rows = []
        # Entêtes
        formatted_headers = [f"\\textbf{{{self.convert_inline(h)}}}" for h in headers]
        latex_rows.append(" & ".join(formatted_headers) + r" \\ \hline")

        # Données
        for row in data_rows:
            # Compléter ou tronquer les cellules pour correspondre aux colonnes
            row_cells = row[:col_count]
            while len(row_cells) < col_count:
                row_cells.append("")
            formatted_cells = [self.convert_inline(c) for c in row_cells]
            latex_rows.append(" & ".join(formatted_cells) + r" \\ \hline")

        table_content = "\n".join(latex_rows)
        return (
            f"\\begin{{table}}[htbp]\n"
            f"\\centering\n"
            f"\\begin{{tabular}}{{{col_spec}}}\n"
            f"\\hline\n"
            f"{table_content}\n"
            f"\\end{{tabular}}\n"
            f"\\end{{table}}"
        )

    def parse(self, markdown_text: str) -> str:
        """
        Parse et convertit l'intégralité du texte Markdown en code LaTeX.
        """
        lines = markdown_text.splitlines()
        output: List[str] = []

        in_code_block = False
        code_lang = ""
        code_lines: List[str] = []

        in_math_block = False
        math_lines: List[str] = []

        in_blockquote = False
        quote_lines: List[str] = []

        table_lines: List[str] = []

        # Pile pour les listes: stocke des tuples (list_type, indent_level)
        list_stack: List[Tuple[str, int]] = []

        def close_lists_up_to(indent: int):
            nonlocal list_stack
            res = []
            while list_stack and list_stack[-1][1] > indent:
                env_type, _ = list_stack.pop()
                res.append(f"\\end{{{env_type}}}")
            return res

        def close_all_lists():
            nonlocal list_stack
            res = []
            while list_stack:
                env_type, _ = list_stack.pop()
                res.append(f"\\end{{{env_type}}}")
            return res

        def flush_blockquote():
            nonlocal in_blockquote, quote_lines
            if in_blockquote and quote_lines:
                quote_text = " ".join(quote_lines)
                converted = self.convert_inline(quote_text)
                output.append(f"\\begin{{quote}}\n{converted}\n\\end{{quote}}")
                quote_lines = []
                in_blockquote = False

        def flush_table():
            nonlocal table_lines
            if table_lines:
                output.append(self.convert_table(table_lines))
                table_lines = []

        i = 0
        n = len(lines)

        while i < n:
            raw_line = lines[i]
            stripped = raw_line.strip()

            # 1. Gestion des blocs de code clôturés (```)
            if stripped.startswith('```'):
                flush_blockquote()
                flush_table()
                output.extend(close_all_lists())

                if not in_code_block:
                    in_code_block = True
                    code_lang = stripped[3:].strip()
                    code_lines = []
                else:
                    in_code_block = False
                    lang_opt = f"[language={code_lang}]" if code_lang else ""
                    code_content = "\n".join(code_lines)
                    output.append(f"\\begin{{lstlisting}}{lang_opt}\n{code_content}\n\\end{{lstlisting}}")
                    code_lines = []
                    code_lang = ""
                i += 1
                continue

            if in_code_block:
                code_lines.append(raw_line)
                i += 1
                continue

            # 2. Gestion des formules mathématiques en bloc ($$)
            if stripped == '$$':
                flush_blockquote()
                flush_table()
                output.extend(close_all_lists())

                if not in_math_block:
                    in_math_block = True
                    math_lines = []
                else:
                    in_math_block = False
                    math_content = "\n".join(math_lines)
                    output.append(f"\\begin{{equation*}}\n{math_content}\n\\end{{equation*}}")
                    math_lines = []
                i += 1
                continue

            # Math bloc sur une seule ligne : $$ formule $$
            if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
                flush_blockquote()
                flush_table()
                output.extend(close_all_lists())
                formula = stripped[2:-2].strip()
                output.append(f"\\begin{{equation*}}\n{formula}\n\\end{{equation*}}")
                i += 1
                continue

            if in_math_block:
                math_lines.append(raw_line)
                i += 1
                continue

            # 3. Tableaux Markdown (lignes contenant |)
            # Détection d'un tableau si la ligne contient |
            if '|' in stripped and not stripped.startswith('>'):
                # Si table_lines est vide, vérifier si la ligne suivante ressemble à une ligne de séparation |--|
                if not table_lines and i + 1 < n and re.match(r'^\s*\|?[\s:-]+[-]+[\s:-]+\|?.*$', lines[i + 1]):
                    flush_blockquote()
                    output.extend(close_all_lists())
                    table_lines.append(stripped)
                    i += 1
                    continue
                elif table_lines:
                    table_lines.append(stripped)
                    i += 1
                    continue

            # Si on n'est plus dans un tableau mais qu'il y en avait un en cours
            if table_lines:
                flush_table()

            # 4. Citations (> ...)
            if stripped.startswith('>'):
                output.extend(close_all_lists())
                in_blockquote = True
                content = re.sub(r'^>\s?', '', stripped)
                quote_lines.append(content)
                i += 1
                continue
            elif in_blockquote:
                flush_blockquote()

            # 5. Ligne vide
            if not stripped:
                output.extend(close_all_lists())
                output.append("")
                i += 1
                continue

            # 6. Ligne horizontale (--- ou *** ou ___)
            if re.match(r'^(\*{3,}|-{3,}|_{3,})\s*$', stripped):
                output.extend(close_all_lists())
                output.append(r"\noindent\rule{\linewidth}{0.4pt}")
                i += 1
                continue

            # 7. Titres (# Titre)
            if re.match(r'^#{1,6}\s+', stripped):
                output.extend(close_all_lists())
                output.append(self.convert_heading(stripped))
                i += 1
                continue

            # 8. Listes (ordonnées et non ordonnées)
            unordered_match = re.match(r'^(\s*)([-*+])\s+(.*)$', raw_line)
            ordered_match = re.match(r'^(\s*)(\d+)\.\s+(.*)$', raw_line)

            if unordered_match or ordered_match:
                if unordered_match:
                    indent_str, marker, item_text = unordered_match.groups()
                    target_env = "itemize"
                else:
                    indent_str, marker, item_text = ordered_match.groups()
                    target_env = "enumerate"

                indent_level = len(indent_str.replace('\t', '    '))

                if not list_stack:
                    list_stack.append((target_env, indent_level))
                    output.append(f"\\begin{{{target_env}}}")
                else:
                    curr_env, curr_indent = list_stack[-1]
                    if indent_level > curr_indent:
                        list_stack.append((target_env, indent_level))
                        output.append(f"\\begin{{{target_env}}}")
                    elif indent_level < curr_indent:
                        output.extend(close_lists_up_to(indent_level))
                        if not list_stack or list_stack[-1][0] != target_env:
                            list_stack.append((target_env, indent_level))
                            output.append(f"\\begin{{{target_env}}}")
                    elif curr_env != target_env:
                        # Même niveau mais changement de type de liste
                        env_type, _ = list_stack.pop()
                        output.append(f"\\end{{{env_type}}}")
                        list_stack.append((target_env, indent_level))
                        output.append(f"\\begin{{{target_env}}}")

                formatted_item = self.convert_inline(item_text.strip())
                output.append(f"  \\item {formatted_item}")
                i += 1
                continue

            # Si ce n'est pas une ligne de liste, fermer les listes ouvertes
            output.extend(close_all_lists())

            # 9. Paragraphe régulier
            output.append(self.convert_inline(stripped))
            i += 1

        # Nettoyage final
        flush_blockquote()
        flush_table()
        output.extend(close_all_lists())

        if in_code_block and code_lines:
            lang_opt = f"[language={code_lang}]" if code_lang else ""
            output.append(f"\\begin{{lstlisting}}{lang_opt}\n" + "\n".join(code_lines) + "\n\\end{lstlisting}")

        if in_math_block and math_lines:
            output.append("\\begin{equation*}\n" + "\n".join(math_lines) + "\n\\end{equation*}")

        return "\n".join(output)
