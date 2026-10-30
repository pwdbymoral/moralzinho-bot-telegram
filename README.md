# Bot do Telegram

Responde `corno eh tu` quando alguém envia uma mensagem contendo a palavra
“corno”, sem diferenciar maiúsculas de minúsculas.

No grupo, o bot oferece estes comandos:

- `/d20`, com `/d20 vantagem` e `/d20 desvantagem`
- `/rolar 2d6+3` para rolar dados de RPG
- `/moeda` para cara ou coroa
- `/8ball pergunta` para uma resposta aleatória
- `/escolher pizza | hambúrguer` para sortear uma opção
- `/ajuda` para ver a lista no Telegram

No Coolify, configure `CUSTOM_REPLIES_JSON` como variável de runtime para
personalizar palavras e respostas. Exemplo: `{"corno":"corno eh tu","bom dia":"Bom dia, tropa!"}`.
O gatilho é procurado como palavra ou frase inteira, sem diferenciar maiúsculas.
O bot mantém a resposta padrão de “corno” mesmo se a variável ficar vazia; depois
de alterar a variável, redeploy o app para carregar a configuração.

O container inclui um healthcheck Docker reconhecido pelo Coolify. Ele verifica
se o processo do bot está ativo, sem depender de porta ou endpoint HTTP.

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
5. Faça o deploy. O bot usa long polling, então não precisa de domínio nem porta exposta.
