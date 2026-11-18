# Estado do NURK Assistente Android — 18/11/2026

A branch `main` em `e823876fad1c8d8f582b7183037834e0aaf76ae6` contém a página de distribuição, metadados de versão e um workflow de release. Os 16 commits alcançáveis pelas referências remotas `main`, `v0.60` e `v0.61` não incluem fontes Android ou configuração de compilação. A consulta por referências de PR não retornou resultados. A API de releases retornou 404 para `v0.62` e não foi encontrado `NURK-v62.apk` nos arquivos disponíveis no ambiente. O repositório `leeostark/nurk` descreve um projeto distinto de motorista, passageiro e backend.

## Inspeção estática do APK oficial 0.61

O SHA-256 do APK baixado é `9c01a58fcf814dc3283bfade42dcffee2c87a199894941d5697b05ab51f06aa4`, igual ao registrado no workflow histórico. O certificado público de assinatura tem SHA-256 `9C:39:D7:3A:B8:3D:40:0C:DA:8C:D8:55:22:63:1B:82:73:49:67:54:A8:FC:38:BA:D4:CC:1D:27:2C:BD:33:3F`.

- **Parada da automação.** `RideService.inspect()` chama `stop()` quando um gesto permanece pendente por mais de 2,5 segundos e pede reativação da Acessibilidade. O verificador periódico também chama `stop()` se a leitura lançar exceção. Esses caminhos explicam como a v61 pode parar de forma persistente. A ocorrência específica relatada ainda precisa de reprodução.
- **Som.** A confirmação visual pode exigir dois quadros positivos com pelo menos 300 ms entre eles. Existe também um caminho de confirmação por evidência de corrida ativa. `ConfirmationSound` instancia e prepara um `MediaPlayer` de forma síncrona ao tocar o arquivo dos três toques. A latência de cada etapa ainda precisa ser medida no aparelho.
- **Preço.** A v61 mantém a opção “Valor mínimo”, desligada por padrão, e permite configurar o limiar entre R$ 3 e R$ 25. A interface também contém uma opção separada de negociar pelo maior valor, desligada por padrão. A inspeção não confirmou seleção e envio do maior valor disponível na tela de negociação.
- **Histórico e tablets.** O APK contém armazenamento de corridas em `SharedPreferences` e recursos de reconhecimento para tablet. Persistência após reinício, deduplicação, pagamento no app, relatórios e isolamento entre dois cards ainda precisam de validação funcional.

## Compilação, assinatura e teste

A distribuição oficial está no [GitHub Releases](https://github.com/leeostark/Nurk-assistente-/releases/tag/v0.61). Para compilar uma atualização, é necessário recuperar o projeto Android com manifesto, fontes, recursos, dependências e configuração original. O código decompilado apresenta lacunas em métodos centrais de conexão do serviço, confirmação, execução de ações e captura de tela. O repositório atual não oferece um comando de compilação Android verificável.

A atualização sobre a instalação existente requer o mesmo identificador de pacote e uma assinatura compatível. O certificado público extraído serve para comparar o APK resultante. A chave privada deve permanecer no ambiente seguro de assinatura.

No aplicativo 99, validar recuperação após ausência de callback e troca de janela, tempo do som após confirmação efetiva, seleção do maior valor dentro do card correto, espera sem reenvio, retomada após recusa ou expiração, persistência e deduplicação do histórico e o comportamento com dois cards.
