Um servidor proxy bastante simplificado. Implementação feita em python 3.7.

Os arquivos Main.py, Whitelist.txt e Blacklist.txt precisam estar na mesma pasta.

Esses 2 últimos arquivos devem ser formatados para conter um URL por linha do arquivo.

A configuração básica do servidor deve ser feita dentro do código, alterando o dicionário config dentro do arquivo Main.py.

O programa roda apenas digitando-se python3 Main.py numa janela do terminal. 

As únicas bibliotecas utilizadas foram time, threading, signal e socket.
