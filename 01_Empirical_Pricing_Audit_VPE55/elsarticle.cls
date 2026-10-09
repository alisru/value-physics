\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{elsarticle}[2022/01/01 Minimal Elsevier Class Shim]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

\makeatletter
\newcommand{\address}[1]{\gdef\els@address{#1}}
\newenvironment{frontmatter}{}{\maketitle\begin{center}\small\els@address\end{center}}
\newenvironment{keyword}{\par\medskip\noindent\textbf{Keywords: }}{\par}
\newcommand{\sep}{, }
\newcommand{\MSC}[2][2020]{\par\noindent\textbf{MSC [#1]: }#2}
\newcommand{\JEL}[1]{\par\noindent\textbf{JEL: }#1}
\newcommand{\journal}[1]{\gdef\els@journal{#1}}
\gdef\els@journal{Journal}
\gdef\els@address{}
\makeatother
