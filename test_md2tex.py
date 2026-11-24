"""
Tests unitaires pour le convertisseur Markdown vers LaTeX (md2tex)
"""

import unittest
from parser import MarkdownToLatex, find_title, extract_title
from md2tex import convert_markdown_to_latex


class TestMarkdownToLatex(unittest.TestCase):

    def setUp(self):
        self.conv = MarkdownToLatex()

    def test_find_title(self):
        self.assertTrue(find_title("# Mon Titre"))
        self.assertTrue(find_title("  # Mon Titre"))
        self.assertFalse(find_title("## Sous-titre"))
        self.assertFalse(find_title("Paragraphe simple"))

    def test_extract_title(self):
        self.assertEqual(extract_title("# Mon Titre"), "Mon Titre")
        self.assertEqual(extract_title("### Titre Niveau 3"), "Titre Niveau 3")

    def test_headings(self):
        self.assertEqual(self.conv.convert_heading("# Section 1"), r"\section{Section 1}")
        self.assertEqual(self.conv.convert_heading("## Sous-section"), r"\subsection{Sous-section}")
        self.assertEqual(self.conv.convert_heading("### Sous-sous-section"), r"\subsubsection{Sous-sous-section}")
        self.assertEqual(self.conv.convert_heading("#### Paragraphe"), r"\paragraph{Paragraphe}")

    def test_inline_formatting(self):
        # Gras
        self.assertIn(r"\textbf{texte gras}", self.conv.convert_inline("**texte gras**"))
        self.assertIn(r"\textbf{texte gras}", self.conv.convert_inline("__texte gras__"))

        # Italique
        self.assertIn(r"\textit{italique}", self.conv.convert_inline("*italique*"))

        # Gras et Italique
        self.assertIn(r"\textbf{\textit{combo}}", self.conv.convert_inline("***combo***"))

        # Barré
        self.assertIn(r"\sout{barre}", self.conv.convert_inline("~~barre~~"))

        # Code inline
        self.assertIn(r"\texttt{mon\_code}", self.conv.convert_inline("`mon_code`"))

    def test_escaping_special_characters(self):
        res = self.conv.convert_inline("Prix: 50% & taxe #1 pour var_name")
        self.assertIn(r"50\%", res)
        self.assertIn(r"\&", res)
        self.assertIn(r"\#1", res)
        self.assertIn(r"var\_name", res)

    def test_math_preservation(self):
        # Formule inline : les caractères _ ou ^ ne doivent pas être altérés dans la formule
        res = self.conv.convert_inline("Formule $E = mc^2$ et $x_1 + x_2 = 10$.")
        self.assertIn("$E = mc^2$", res)
        self.assertIn("$x_1 + x_2 = 10$", res)

        # Formule bloc
        md_block = "$$\n\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}\n$$"
        parsed = self.conv.parse(md_block)
        self.assertIn(r"\begin{equation*}", parsed)
        self.assertIn(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}", parsed)
        self.assertIn(r"\end{equation*}", parsed)

    def test_code_blocks(self):
        md = "```python\ndef test():\n    return 42\n```"
        parsed = self.conv.parse(md)
        self.assertIn(r"\begin{lstlisting}[language=python]", parsed)
        self.assertIn("def test():", parsed)
        self.assertIn(r"\end{lstlisting}", parsed)

    def test_lists(self):
        md = "- Item 1\n- Item 2\n  - Sub 2.1\n- Item 3"
        parsed = self.conv.parse(md)
        self.assertIn(r"\begin{itemize}", parsed)
        self.assertIn(r"\item Item 1", parsed)
        self.assertIn(r"\item Sub 2.1", parsed)
        self.assertIn(r"\end{itemize}", parsed)

    def test_tables(self):
        md = "| Col 1 | Col 2 |\n|:---|---:|\n| Val A | Val B |"
        parsed = self.conv.parse(md)
        self.assertIn(r"\begin{table}[htbp]", parsed)
        self.assertIn(r"\begin{tabular}{|l|r|}", parsed)
        self.assertIn(r"\textbf{Col 1} & \textbf{Col 2} \\ \hline", parsed)
        self.assertIn(r"Val A & Val B \\ \hline", parsed)
        self.assertIn(r"\end{tabular}", parsed)

    def test_blockquote(self):
        md = "> Ceci est une citation.\n> Deuxième ligne."
        parsed = self.conv.parse(md)
        self.assertIn(r"\begin{quote}", parsed)
        self.assertIn("Ceci est une citation.", parsed)
        self.assertIn(r"\end{quote}", parsed)

    def test_standalone_document(self):
        md = "# Mon Super Document\nContenu avec **gras** et $x=1$."
        tex = convert_markdown_to_latex(md, standalone=True, author="Auteur Test")
        self.assertIn(r"\documentclass", tex)
        self.assertIn(r"\usepackage{amsmath,amssymb,amsfonts}", tex)
        self.assertIn(r"\title{Mon Super Document}", tex)
        self.assertIn(r"\author{Auteur Test}", tex)
        self.assertIn(r"\maketitle", tex)
        self.assertIn(r"\begin{document}", tex)
        self.assertIn(r"\end{document}", tex)


if __name__ == '__main__':
    unittest.main()
