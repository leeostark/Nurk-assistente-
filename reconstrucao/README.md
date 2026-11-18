# NURK Assistente 0.63

A 0.63 reaplica o patch da 0.62 ao APK oficial 0.61 e atualiza o diretório Smali resultante. A distribuição mantém o pacote e a chave de assinatura da 0.62.

## Compilar

Use Java, Python 3 e Apktool 2.12.1. Obtenha o [APK oficial 0.61](https://github.com/leeostark/Nurk-assistente-/releases/download/v0.61/NURK-v61.apk) e o [patch 0.62](https://github.com/leeostark/Nurk-assistente-/blob/10317506f79098f28e82e6c5a5660746f0f3e3d5/reconstrucao/patch-v62.py). Execute na raiz do repositório:

```bash
echo '9c01a58fcf814dc3283bfade42dcffee2c87a199894941d5697b05ab51f06aa4  NURK-v61.apk' | sha256sum -c
java -jar apktool_2.12.1.jar d -o nurk-build NURK-v61.apk
python3 patch-v62.py nurk-build
python3 reconstrucao/patch-v63.py nurk-build
java -jar apktool_2.12.1.jar b -o NURK-v63-unsigned.apk nurk-build
```

Alinhe o APK com `zipalign` e assine com `apksigner` e a chave usada na 0.62. O alias é `nurk-release`. O SHA-256 esperado do certificado é `cd514cf16732c73af0ddb9e606a14d4db4634a9650331a17eef1a6e6770dcd56`. Mantenha o keystore e sua senha fora do repositório.

## Publicar

Publique o APK assinado em `docs/NURK-v<versionCode>.apk`, ajuste o download do site e informe o novo número em `latestVersionCode` de `docs/version.json`. A partir da 0.63, o app verifica esse campo durante o uso e solicita download via DownloadManager. A instalação depende da confirmação no Android. O campo `minimumVersionCode` continua separado e define o bloqueio obrigatório.

## Validação e limites

Foram verificados a compilação, a integridade, o pacote, a versão e o certificado de distribuição. A automação continua restrita ao pacote do 99. Avisos de apps bancários podem persistir porque o serviço de Acessibilidade continua ativo.

Teste em um aparelho com a 0.62 instalada. Confirme a atualização preservando o histórico, o filtro abaixo e acima do mínimo, a retomada depois de janela temporária ou captura interrompida, a latência dos três toques, os fluxos de aceite e de proposta com um e dois cards e o download de uma versão futura. Quando a tela de negociação conhecida exibe opções apenas na imagem, a aplicação aguarda opções acessíveis para evitar aceitar o valor base por coordenadas.
