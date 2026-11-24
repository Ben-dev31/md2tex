# Rapport de Démonstration : Conversion Markdown vers LaTeX

Bienvenue dans ce document d'exemple pour le projet **md2tex**.

## 1. Formatage de texte et caractères spéciaux

On peut mettre du texte en **gras**, en *italique*, en ***gras et italique***, ou encore en ~~texte barré~~.
Les caractères spéciaux comme 100%, les esperluettes & cie, ainsi que les variables avec underscores comme `taux_variation_annuel` sont convenablement échappés pour éviter les erreurs de compilation LaTeX.

## 2. Formules Mathématiques

### Formule en ligne
Le théorème de Pythagore s'énonce $a^2 + b^2 = c^2$.
La célèbre équation d'Einstein est $E = m \cdot c^2$.
Pour une variable aléatoire $X \sim \mathcal{N}(\mu, \sigma^2)$, la densité est donnée par $f(x)$.

### Formule en bloc
Voici l'intégrale de Gauss :

$$
\int_{-\infty}^{+\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Et la formule de décomposition en série de Fourier :

$$
f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty} \left( a_n \cos(nx) + b_n \sin(nx) \right)
$$

---

## 3. Listes

### Liste non ordonnée
- Premier élément important
- Deuxième élément avec une sous-liste :
  - Sous-élément A
  - Sous-élément B avec formule : $x_k \in \mathbb{R}$
- Troisième élément

### Liste ordonnée
1. Étape 1 : Initialisation des variables
2. Étape 2 : Traitement algorithmique
3. Étape 3 : Exportation des résultats

---

## 4. Blocs de Code

Voici un extrait de code Python avec coloration syntaxique :

```python
def fibonacci(n: int) -> list[int]:
    """Génère la suite de Fibonacci jusqu'à n termes."""
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

if __name__ == "__main__":
    print(fibonacci(10))
```

---

## 5. Tableaux

| Nom de l'algorithme | Complexité temporelle | Complexité spatiale | Type |
| :--- | :---: | ---: | :---: |
| Tri Rapide (QuickSort) | $\mathcal{O}(n \log n)$ | $\mathcal{O}(\log n)$ | Diviser pour régner |
| Tri par Fusion (MergeSort) | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | Stable |
| Tri à Bulles (BubbleSort) | $\mathcal{O}(n^2)$ | $\mathcal{O}(1)$ | Naïf |

---

## 6. Citations et Liens

> La science est ce que l'on comprend bien assez pour l'expliquer à un ordinateur. L'art est tout le reste.
> — Donald Knuth

Pour en savoir plus, consultez la documentation officielle de [LaTeX Project](https://www.latex-project.org) ou le dépôt du projet.
