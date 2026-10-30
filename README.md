# Bot do Telegram

Responde `corno eh tu` quando alguém envia uma mensagem contendo a palavra
“corno”, sem diferenciar maiúsculas de minúsculas.

No grupo, o bot oferece estes comandos:

- `/d20`, com `/d20 vantagem` e `/d20 desvantagem`
- `/rolar 2d6+3` para rolar dados de RPG
- `/moeda` para cara ou coroa
- `/8ball pergunta` para uma resposta aleatória
- `/escolher pizza | hambúrguer` para sortear uma opção
- `/campanha fantasia | recuperar o artefato` abre um RPG no grupo por 90 segundos
- `/entrar guerreiro` cria um personagem aleatório para a campanha
- `/acao tentar distrair o guarda` pede uma narração ao mestre IA
- `/status`, `/reviver` e `/fim` acompanham e controlam a campanha
- `/ajuda` para ver a lista no Telegram

As respostas seguem um tom curto e informal, com abreviações parecidas com as
suas mensagens.

No Coolify, configure `CUSTOM_REPLIES_JSON` como variável de runtime para
personalizar palavras e respostas. Exemplo: `{"corno":"corno eh tu","bom dia":"Bom dia, tropa!"}`.
O gatilho é procurado como palavra ou frase inteira, sem diferenciar maiúsculas.
O bot mantém a resposta padrão de “corno” mesmo se a variável ficar vazia; depois
de alterar a variável, redeploy o app para carregar a configuração.

O container inclui um healthcheck Docker reconhecido pelo Coolify. Ele verifica
se o processo do bot está ativo, sem depender de porta ou endpoint HTTP.

## Campanhas de RPG

No grupo, alguém inicia com `/campanha <gênero> | <objetivo>`. Os gêneros são
fantasia, terror, sci-fi, apocalipse e mistério. Se não passar objetivo, o bot
sorteia um. A sala fica aberta por 90 segundos; depois disso, gente nova ainda
pode entrar durante a partida.

Cada pessoa escolhe um arquétipo com `/entrar guerreiro`, `/entrar ladino`,
`/entrar mago`, `/entrar curandeiro`, `/entrar atirador` ou `/entrar tanque`.
O Ollama inventa o nome e o conceito do personagem; vida e bônus são sorteados
pelas regras do bot. A regra autoral combina teste de d20, classes e vida com
um marcador de progresso coletivo: sucesso dá um ponto, e um 20 natural dá dois;
seis pontos completam o objetivo. Falhas causam dano; a campanha acaba se o
grupo cumprir o objetivo ou todo mundo morrer.

Durante a partida, `/acao <ação>` resolve um teste e chama o Ollama para narrar
o resultado. O mestre usa português informal no estilo do bot. A IA não decide
rolagens, dano ou progresso. Cada personagem pode ser ressuscitado uma vez por
campanha: responda a uma mensagem da pessoa morta com `/reviver`. Quem morreu
não pode entrar de novo por `/entrar`.

As campanhas ficam em JSON no caminho definido por `CAMPAIGN_STATE_PATH`. Os
três valores de runtime usados no Coolify são `OLLAMA_BASE_URL` (padrão
`http://ollama-api:11434`), `OLLAMA_MODEL` (padrão `qwen3:1.7b`) e
`CAMPAIGN_STATE_PATH` (padrão `./campaigns.json`). Monte um volume persistente
em `/data` e configure o estado como `/data/campaigns.json`.

## Iniciar

1. Crie o bot pelo [@BotFather](https://t.me/BotFather), usando `/newbot`, e copie o token.
2. No terminal, defina o token e inicie:

   ```sh
   export TELEGRAM_BOT_TOKEN="seu-token"
   python3 bot.py
   ```

O token fica numa variável de ambiente; não o publique nem o coloque no código.

## Usar em grupos

Para o bot receber mensagens comuns do grupo, desative o modo de privacidade dele
no @BotFather com `/setprivacy` e remova e adicione o bot ao grupo novamente
para a mudança valer. Em conversa privada, a pessoa precisa iniciar o bot primeiro.

## Deploy no Coolify

1. Crie uma aplicação a partir deste repositório e da branch `main`.
2. Selecione o build pack **Dockerfile** e use `/Dockerfile`.
3. Cadastre `TELEGRAM_BOT_TOKEN` nas variáveis de ambiente e deixe-a disponível
   apenas em runtime; o bot não precisa do token durante o build.
4. Opcionalmente, cadastre `CUSTOM_REPLIES_JSON` como runtime e atualize o JSON
   para personalizar gatilhos e respostas.
5. Configure `OLLAMA_BASE_URL=http://ollama-api:11434`, `OLLAMA_MODEL=qwen3:1.7b`
   e `CAMPAIGN_STATE_PATH=/data/campaigns.json`, todas apenas em runtime.
6. Monte um volume persistente em `/data` para manter a campanha em reinícios.
7. Conecte o bot e o stack do Ollama à rede Docker compartilhada `coolify` para
   o endereço `ollama-api:11434` funcionar entre os dois.
8. Faça o deploy. O bot usa long polling, então não precisa de domínio nem porta exposta.
