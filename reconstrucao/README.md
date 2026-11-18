# Reconstrução de teste do NURK 0.62

O patch preserva a estrutura do APK 0.61 e modifica seu bytecode Smali através do Apktool. Requer Java, Python 3 e Apktool 2.12.1.

Baixe o [APK 0.61 oficial](https://github.com/leeostark/Nurk-assistente-/releases/download/v0.61/NURK-v61.apk) e execute da raiz do repositório:

```bash
echo '9c01a58fcf814dc3283bfade42dcffee2c87a199894941d5697b05ab51f06aa4  NURK-v61.apk' | sha256sum -c
java -jar apktool_2.12.1.jar d -o nurk-v62 NURK-v61.apk
python3 reconstrucao/patch-v62.py nurk-v62
java -jar apktool_2.12.1.jar b -o NURK-v62-sem-assinatura.apk nurk-v62
```

Para distribuição, alinhe com `zipalign`, assine com o `apksigner` no ambiente de assinatura oficial e confira com `apksigner verify --verbose --print-certs`. Compare com o SHA-256 do certificado da 0.61, `9c39d73ab83d400cda8cd85522631b8273496754a8fc38bad4cc1d272cbd333f`. Use o keystore original fora do repositório. A versão de teste usa um certificado Android Debug e exige ambiente separado da instalação oficial.

## Estado

- A recuperação após falha de leitura ou timeout invalida retornos atrasados de gesto/captura e aguarda um segundo para refazer a leitura. A fase e os dados pendentes são preservados.
- O aviso toca após a confirmação e antes da escrita no histórico, uma vez por corrida. A confirmação visual ainda exige dois quadros.
- O filtro de mínimo fica oculto e suas preferências deixam de bloquear a automação.
- Na negociação reconhecida via Acessibilidade, a procura pelo maior preset acima do valor inicial passou a ser obrigatória. Durante a janela de confirmação, o caminho bloqueia nova proposta no mesmo fluxo. O reaproveitamento da ação existente “Fazer nova oferta” e as transições reais de recusa e expiração dependem de teste no 99.
- A compilação, a leitura do metadado da versão e a assinatura de teste foram verificadas. Celular, tablet, dois cards, aceite, nova oferta e persistência do histórico exigem teste funcional. O APK assinado para teste não é uma atualização instalável sobre a versão oficial.
