# Como contribuir com o Sururu Linux

Obrigado por querer ajudar! O guia completo, com o passo a passo do primeiro
pull request, está em [docs/contribuir.md](docs/contribuir.md).

Resumo rápido:

| Quero... | Onde mexer | Como testar |
|---|---|---|
| Criar um laboratório | `central/labs/*.json` ([modelo](docs/novo-laboratorio.md)) | `make central` e `python3 scripts/validar-labs.py` |
| Melhorar a Central | `central/` (Python puro + HTML/JS) | `make central` |
| Mudar pacotes da ISO | `config/package-lists/` | `make build && make test` |
| Mudar arte | `artwork/` (veja `PALETA.md`) | `make arte` |
| Corrigir a documentação | `docs/` | `make docs` |

Commits e pull requests em português, por favor. Mensagens curtas, dizendo o
que mudou: `Lab: guardar senhas com Secret`, `Central: corrige botão no celular`.
