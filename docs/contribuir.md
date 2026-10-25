# Como contribuir

O Sururu é feito por quem estuda. Toda ajuda conta, e você não precisa ser
especialista para começar.

## Jeitos de ajudar, do mais simples ao mais técnico

- **Usar e contar como foi.** Testou num notebook diferente? Abra uma
  [issue](https://github.com/kurumintecnologia/sururu-linux/issues) dizendo o
  modelo e o que funcionou ou não.
- **Corrigir textos.** Achou um erro de português ou uma explicação confusa?
  Todo arquivo da documentação tem um lápis de "editar" no canto.
- **Escrever um laboratório.** É só um arquivo JSON.
  [Veja como](novo-laboratorio.md).
- **Melhorar a Central.** Python puro e HTML/JS sem framework. Rode
  `make central` e mexa à vontade.
- **Arte.** Papéis de parede, ícones, tema. A paleta está em
  `artwork/PALETA.md`.

## Passo a passo do primeiro pull request

```bash
git clone https://github.com/SEU-USUARIO/sururu-linux
cd sururu-linux
git switch -c meu-laboratorio
# faça a mudança
make central        # teste a Central aqui mesmo
git commit -am "Lab: guardar senhas com Secret"
git push -u origin meu-laboratorio
```

Depois abra o pull request no GitHub. Explique o que mudou e como testou.

## Combinados

- Seja gentil. Todo mundo aqui já foi iniciante (e ainda é, em alguma coisa).
- Pergunta "boba" não existe. Se você teve a dúvida, outra pessoa também tem.
- Leia o [código de conduta](https://github.com/kurumintecnologia/sururu-linux/blob/main/CODE_OF_CONDUCT.md).
