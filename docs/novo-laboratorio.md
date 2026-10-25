# Escrever um laboratório

Esta é a forma mais fácil e valiosa de contribuir: um laboratório é **um
arquivo JSON** em `central/labs/`. Não precisa saber programar a Central.

## Exemplo comentado

```json
{
  "id": "k8s-05-secret",
  "trilha": "kubernetes",
  "ordem": 5,
  "titulo": "Guardar senhas com Secret",
  "nivel": "intermediário",
  "tempo": 15,
  "precisa": ["cluster"],
  "prova": true,
  "resumo": "Guardar a senha do banco sem deixar ela na imagem.",
  "historia": "A loja da Dona Cida ganhou um banco de dados. A senha não pode ficar no código.",
  "passos": [
    { "texto": "Crie o Secret.", "comando": "kubectl create secret generic banco --from-literal=senha=sururu123" }
  ],
  "verificacoes": [
    {
      "texto": "O Secret banco existe",
      "comando": "kubectl get secret banco",
      "dica": "kubectl create secret generic banco --from-literal=..."
    }
  ],
  "solucao": ["kubectl create secret generic banco --from-literal=senha=sururu123"],
  "limpeza": ["kubectl delete secret banco --ignore-not-found"]
}
```

| Campo | Para que serve |
|---|---|
| `id` | Nome único, no formato `trilha-NN-assunto` |
| `trilha` | `linux`, `containers` ou `kubernetes` |
| `precisa` | `[]`, `["docker"]` ou `["cluster"]`; a Central avisa o aluno |
| `prova` | `true` para entrar no Modo prova |
| `verificacoes` | Cada `comando` roda no Bash; **código de saída 0 = certo** |
| `limpeza` | Comandos do botão "Recomeçar do zero" |

## Regras da casa

- **Histórias brasileiras e do cotidiano.** Feira, bodega, pousada, oficina,
  escola. Nada de "foo" e "bar".
- **Uma ideia por laboratório.** Dez a quinze minutos, no máximo.
- **Dica que ensina.** Em vez de "está errado", diga o que conferir.
- **Verificação de verdade.** Confira o estado do sistema, não se o aluno
  digitou um comando específico. Existem vários jeitos certos.
- **Teste antes de mandar:** rode `make central`, faça o lab, erre de
  propósito e veja se as dicas ajudam.

Depois é só abrir um pull request. Veja [Como contribuir](contribuir.md).
