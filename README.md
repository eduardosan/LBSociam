LBSociam
======================

Implementação da SM no Python 3

Instalação
----------------

* Baixa versão do nlpnet

<pre>
mkdir /srv/lbsociam-py2/terceiros
cd /srv/lbsociam-py2/terceiros
git clone https://github.com/eduardosan/nlpnet.git
</pre>

* Executa o comando do python

<pre>
cd /srv/lbsociam-py2/src/LBSociam
/srv/lbsociam-py2/bin/python setup.py develop
</pre>

Configuração
-------------------

* Configura nltk

<pre>
/srv/lbsociam-py2/bin/python
>>> import nltk
>>> nltk.download()
---------------------------------------------------------------------------
    d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
---------------------------------------------------------------------------
Downloader> c
---------------------------------------------------------------------------
    s) Show Config   u) Set Server URL   d) Set Data Dir   m) Main Menu
---------------------------------------------------------------------------
Config> d
  New Directory> /srv/lbsociam-py2/nltk_data
---------------------------------------------------------------------------
    s) Show Config   u) Set Server URL   d) Set Data Dir   m) Main Menu
---------------------------------------------------------------------------
Config> m

---------------------------------------------------------------------------
    d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
---------------------------------------------------------------------------
Downloader> d

Download which package (l=list; x=cancel)?
  Identifier> punkt
    Downloading package punkt to /srv/lbsociam/nltk_data...
      Unzipping tokenizers/punkt.zip.

---------------------------------------------------------------------------
    d) Download   l) List    u) Update   c) Config   h) Help   q) Quit
---------------------------------------------------------------------------
Downloader> q
True
>>> quit()
</pre>

* Configura o diretório do nlpnet

<pre>
mkdir /srv/lbsociam-py2/nlpnet_data
/srv/lbsociam-py2/bin/python
>>> import nlpnet
>>> nlpnet.set_data_dir('/srv/lbsociam-py2/nlpnet_data')
</pre>

* Baixa os modelos

<pre>
cd /srv/lbsociam-py2/nlpnet_data
wget http://nilc.icmc.usp.br/nlpnet/nlpnet-srl.zipi
unzip nlpnet-srl.zip
rm nlpnet-srl.zip
mv srl/* .
rm -r srl
</pre>

Roda o teste pra ver se está funcionando

<pre>
export NLTK_DATA=/srv/lbsociam-py2/nltk_data
/srv/lbsociam-py2/bin/python
>>> import nlpnet
>>> nlpnet.set_data_dir('/srv/lbsociam-py2/nlpnet_data')
>>> tagger = nlpnet.SRLTagger()
>>> sent = tagger.tag(u'O rato roeu a roupa do rei de Roma.')[0]  
>>> sent.tokens
>>> sent.arg_structures
</pre>

Configurando twitter
----------------------------

* Baixar o script de configuração
<pre>
wget https://github.com/bear/python-twitter/raw/master/get_access_token.py
cd /srv/lbsociam-py2/src/LBSociam
/srv/lbsociam-py2/bin/pip install oauth2
/srv/lbsociam-py2/bin/python get_access_token.py
</pre>
