LBSociam
========

Instalação
----------------

* Versões:
	* Python 3.4
	* Python 3.4 headers files (python3.4-dev)


* Instala ATLAS + LAPACK

<pre>
cd /usr/local/src/
wget http://sourceforge.net/projects/math-atlas/files/Stable/3.10.1/atlas3.10.1.tar.bz2/download
mv download atlas3.10.1.tar.bz2
tar -xjvf atlas3.10.1.tar.bz2
mkdir /usr/local/atlas3.10.1
rm atlas3.10.1.tar.bz2
wget http://www.netlib.org/lapack/lapack-3.4.1.tgz
mv ATLAS/ ATLAS-3.10.1
cd ATLAS-3.10.1
mkdir Linux_C2D64SSE3
cd Linux_C2D64SSE3
</pre>

Antes de prosseguir é necessário desabilitar o CPU throttle da máquina, ou o LAPACK não vai instalar direito. Como estou no notebook, desabilito para usar e depois habilito no reboot.

<pre>
/usr/bin/cpufreq-selector -g performance
</pre>

Agora posso seguir com a compilação

<pre>
../configure -b 64 -D c -DPentiumCPS=2400 --prefix=/usr/local/atlas3.10.1/ --with-netlib-lapack-tarfile=/usr/local/src/lapack-3.4.1.tgz --shared
make build
make check
make ptcheck
make time
cd lib
make shared 
make cshared 
make ptshared
make cptshared
cd ..
make install
</pre>

**Importante**: A fraquência da CPU deve ser ajustada corretamente na tag DPentiumCPS. Como minha CPU é um Quad Core com 2,67 MHz, coloquei 2400 que deve ser um valor justo.

Agora habilitamos no Sistema operacional

<pre>
ln -s /usr/local/atlas3.10.1/ /usr/local/atlas
</pre>

* Instala numpy

Primeiro passo é colocar o diretório do ATLAS para o numpy e depois executar o easy_install.

<pre>
export ATLAS=/usr/local/atlas/lib/libsatlas.so
/srv/lbsociam/bin/easy_install numpy
</pre>

* Instala Nltk

<pre>
cd /srv/lbsociam/
mkdir terceiros
cd terceiros/
wget http://www.nltk.org/nltk3-alpha/nltk-3.0a4.zip
unzip nltk-3.0a4.zip
rm nltk-3.0a4.zip
cd nltk-3.0a4/
/srv/lbsociam/bin/python setup.py install
</pre>

* Instala nlpnet

<pre>
cd /srv/lbsociam/terceiros/
git clone https://github.com/eduardosan/nlpnet.git
cd nlpnet
/srv/lbsociam/bin/easy_install cython
/srv/lbsociam/bin/python setup.py install
</pre>


Opcional
--------------

* Migrar o código do Python 2 para o Python 3

<pre>
cd /srv/lbsociam/terceiros/nlpnet
/usr/bin/2to3-3.4 -wn .
/srv/lbsociam/bin/python setup.py install
</pre>


Configuração
--------------------

* Baixa os módulos do nltk

<pre>
mkdir /srv/lbsociam/nltk_data
/srv/lbsociam/bin/python
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
  New Directory> /srv/lbsociam/nltk_data
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
mkdir /srv/lbsociam/nlpnet_data
/srv/lbsociam/bin/python
>>> import nlpnet
>>> nlpnet.set_data_dir('/srv/lbsociam/nlpnet_data')
</pre>

Roda o teste pra ver se está funcionando

<pre>

</pre>
