# Examples

## Create a FastAPI App

```bash
gate19 new myapi --template fastapi
cd myapi
gate19 install httpx
gate19 run main.py
# Visit http://localhost:8000
```

## Create a CLI

```bash
gate19 new mycli --template cli
cd mycli
gate19 run main.py -- --help
gate19 run main.py hello --name Gate19
```

## Django

```bash
gate19 new mydjango --template django
cd mydjango
gate19 install psycopg2-binary
django-admin startproject config .
gate19 run manage.py migrate
gate19 run manage.py runserver
```

## Pygame

```bash
gate19 new mygame --template pygame
cd mygame
gate19 run main.py
```

## AI Project

```bash
gate19 new myai --template ai
cd myai
# Add OPENAI_API_KEY to .env
gate19 run main.py
```

## Library

```bash
gate19 new mylib --template library
cd mylib
gate19 build
gate19 publish --dry-run
```

## Custom Python

```bash
gate19 python install 3.13
gate19 new cutting_edge --python 3.13 --template api
gate19 python use 3.13
```

## CI Integration

```yaml
- run: pip install gate19
- run: gate19 new app --template app --no-install
- run: gate19 build
```
