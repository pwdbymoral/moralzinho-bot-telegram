# Bot do Telegram

Responde `corno eh tu` quando alguém envia uma mensagem contendo a palavra
“corno”, sem diferenciar maiúsculas de minúsculas.

No grupo, use `/d20` para rolar um dado de 20 lados.

O container inclui um healthcheck Docker reconhecido pelo Coolify. Ele acompanha
as consultas bem-sucedidas ao Telegram e não depende de porta ou endpoint HTTP.

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
4. Faça o deploy. O bot usa long polling, então não precisa de domínio nem porta exposta.
