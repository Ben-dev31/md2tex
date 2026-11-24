# md2tex

Convertisseur léger et complet de fichiers **Markdown (`.md`)** en code **LaTeX (`.tex`)** en Python, sans dépendances externes.

Ce programme convertit vos documents Markdown en documents LaTeX prêts à être compilés avec `pdflatex`, en prenant en charge le formatage textuel, les formules mathématiques, les tableaux, les blocs de code avec coloration syntaxique, les listes imbriquées, les citations et les liens.

---

## Fonctionnalités

- **Formules mathématiques** :
  - En ligne : `$E = mc^2$` préservé intégralement.
  - En bloc : `$$ \int_a^b f(x)dx $$` converti en environnement `\begin{equation*} ... \end{equation*}`.
- **Titres** : de `#` à `######` convertis en `\section`, `\subsection`, `\subsubsection`, `\paragraph`, etc. (numérotés ou non).
- **Formatage de texte** :
  - **Gras** (`**texte**` ou `__texte__`) $\rightarrow$ `\textbf{texte}`
  - *Italique* (`*texte*` ou `_texte_`) $\rightarrow$ `\textit{texte}`
  - ***Gras & Italique*** $\rightarrow$ `\textbf{\textit{texte}}`
  - ~~Barré~~ (`~~texte~~`) $\rightarrow$ `\sout{texte}`
  - Code en ligne (`` `code` ``) $\rightarrow$ `\texttt{code}`
- **Blocs de code** (```` ```python ... ``` ````) $\rightarrow$ `\begin{lstlisting}[language=python]` avec gestion UTF-8 / accents.
- **Tableaux Markdown** $\rightarrow$ `\begin{table}` et `\begin{tabular}` avec détection automatique des alignements (`:---:`, `:---`, `---:`).
- **Listes ordonnées et non ordonnées** : prise en charge des puces (`-`, `*`, `+`), des numéros (`1.`, `2.`) et des niveaux d'imbrication.
- **Citations** (`> texte`) $\rightarrow$ `\begin{quote} ... \end{quote}`.
- **Liens et Images** :
  - `[Lien](https://...)` $\rightarrow$ `\href{https://...}{Lien}`
  - `![Image](chemin.png)` $\rightarrow$ environnement `\begin{figure}` avec `\includegraphics`.
- **Échappement automatique** des caractères réservés LaTeX (`%`, `&`, `_`, `#`, `{`, `}`, `^`, etc.) hors mathématiques et blocs de code.
- **Mode Document Autonome (`--standalone`)** : génère un fichier `.tex` complet avec préambule préconfiguré (géométrie, encodage UTF-8, babel, mathématiques, couleurs et style listings).

---

## Structure du projet

- [`parser.py`] : Moteur de parsing et conversion Markdown $\rightarrow$ LaTeX.
- [`md2tex.py`] : Interface en ligne de commande (CLI) et générateur de documents complets.
- [`test_md2tex.py`] : Suite de tests unitaires.
- [`sample.md`] : Fichier Markdown d'exemple illustrant l'ensemble des fonctionnalités.

---

## Utilisation

### 1. En ligne de commande (CLI)

#### Conversion simple (génère un fragment de code LaTeX) :
```bash
python md2tex.py document.md -o document.tex
```

#### Conversion en document LaTeX complet prêt à compiler (`--standalone` ou `-s`) :
```bash
python md2tex.py sample.md -s -o document.tex --author "Votre Nom" --title "Mon Titre"
```

#### Conversion en PDF :
```bash
python md2tex.py --input sample.md -o pdf
```

La conversion PDF nécessite une distribution LaTeX (MiKTeX ou TeX Live) avec `pdflatex` accessible depuis le `PATH`.

Si `--title` n'est pas fourni, le programme extrait automatiquement le premier titre `# Titre` trouvé dans le document Markdown.

#### Options disponibles :
| Option | Raccourci | Description |
| :--- | :---: | :--- |
| `--input` | | Fichier Markdown `.md` d'entrée |
| `--output` | `-o` | Type de sortie `tex, pdf` (défaut : `tex`) |
| `--standalone` | `-s` | Génère un document LaTeX complet avec préambule |
| `--title` | `-t` | Titre du document |
| `--author` | `-a` | Nom de l'auteur |
| `--date` | `-d` | Date (défaut : date du jour) |
| `--lang` | | Langue pour babel (`french`, `english`, etc. défaut : `french`) |
| `--no-numbering`| | Désactive la numérotation des sections (`\section*`) |

---

### 2. Utilisation dans du code Python

```python
from md2tex import convert_markdown_to_latex

markdown_text = """
# Introduction à la Physique
La formule d'Einstein est $E = mc^2$.
On note également la fonction $f(x) = \sin(x) + x^2$.

```python
print("Hello LaTeX")
```
"""

# Générer un fragment LaTeX
latex_fragment = convert_markdown_to_latex(markdown_text)

# Générer un document complet autonome
latex_doc = convert_markdown_to_latex(
    markdown_text,
    standalone=True,
    author="Albert Einstein",
    language="french"
)

with open("output.tex", "w", encoding="utf-8") as f:
    f.write(latex_doc)
```

---

### 3. Compilation du fichier LaTeX en PDF

Pour générer le fichier PDF final, utilisez `pdflatex` :

```bash
pdflatex document.tex
```

---

## Exécution des tests

Pour lancer les tests unitaires :

```bash
python -m unittest test_md2tex.py
```
