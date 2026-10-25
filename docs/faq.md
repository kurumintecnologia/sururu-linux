# Perguntas frequentes

**O Sururu é a continuação do Kurumin?**
Não. O Kurumin foi a distro histórica do Carlos Morimoto, que ajudou uma
geração inteira a conhecer o Linux no Brasil, e merece todo o respeito. O
Sururu é um projeto novo, com outro nome, outro foco (aprender infraestrutura e
cloud native) e outra base. A inspiração no espírito do Kurumin, de deixar o
Linux fácil para o brasileiro, a gente assume com orgulho.

**É o Debian?**
É baseado no Debian, mas não é um produto oficial do Projeto Debian. Usamos os
pacotes do Debian e somos gratos ao trabalho deles.

**Posso usar no dia a dia, não só para estudar?**
Pode. Por baixo é um Debian estável com desktop XFCE, navegador e tudo que um
computador comum precisa.

**Roda em computador fraco?**
O desktop roda bem com 4 GB de RAM. O cluster Kubernetes é o que pesa: para ele,
6 a 8 GB deixam tudo confortável.

**Funciona sem internet?**
O sistema e os laboratórios de Linux, sim. Criar o cluster pela primeira vez
precisa baixar a imagem do Kubernetes (cerca de 500 MB). Os laboratórios de
containers baixam a imagem do nginx.

**Posso instalar ao lado do Windows?**
Pode. O instalador oferece essa opção. Mesmo assim, faça backup antes.

**Dá para usar para estudar para a CKA?**
Dá, e foi pensado para isso: o cluster é real, o Modo prova tem cronômetro e as
tarefas seguem o estilo da prova. Mas a prova oficial usa clusters criados com
kubeadm; complemente com laboratórios de instalação de cluster.

**Os laboratórios mandam meus dados para algum lugar?**
Não. A Central roda só no seu computador (`127.0.0.1`), sem conta, sem
rastreamento. O progresso fica num arquivo na sua pasta pessoal.
