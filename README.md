#Cidade Iluminada

## Instalação do webservice

Dentro de um virtualenv, digite

```
$ pip install -r requirements-dev.txt
$ pip install -r requirements.txt
$ mkdir instance
$ touch instance/settings_local.py
$ mkdir tmp
```

### O `settings_local.py`

Esse arquivo guarda as configurações locais para a aplicação. Veja o arquivo `settings.py` para o exemplo das chaves e valores.

O mais importante para se alterar é a chave `SQLALCHEMY_DATABASE_URI`. Onde você deve alterar os campos `user`, `password` e `port` para os valores que foi configurado na instalação do banco de dados.

### Rodando o webservice

Na pasta do webservice digite

```
$ python manage.py
```

Isso irá te mostrar os comandos disponíveis.

#### Primeira execução

Na primeira vez que você rodar, digite

```
$ python manage.py db upgrade
```
para instalar o banco de dados e

```
$ python manage.py criar_usuario admin admin
```
para criar o usuário padrão.

Para ativar o servidor digite
```
python manage.py runserver
```

Agora acesse [http://localhost:5000](http://localhost:5000) para acessar o webservice.

## Aplicativo Android

O aplicativo foi movido para o [novo repositório](https://github.com/HardDiskD/TCMCidadeIluminada-Android).

## Trabalhando com o git

O workflow básico do git está [aqui](https://github.com/HardDiskD/python-flask-android-setup#trabalhando-com-o-git).

Recomendo seguir um tutorial [básico](http://www.sitepoint.com/git-for-beginners/) de git para não ter maiores problemas.
