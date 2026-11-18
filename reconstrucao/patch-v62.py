"""Aplica o patch ao diretório produzido pelo Apktool 2.12.1."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
smali = root / "smali/br/leo/assistente"


def replace(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Trecho inesperado: {before!r}")
    return text.replace(before, after)


def method(text, name, change):
    start = text.index(name)
    end = text.index(".end method", start)
    return text[:start] + change(text[start:end]) + text[end:]


service = smali / "RideService.smali"
text = service.read_text()
text = replace(text, '.field touchBusy:Z', '.field recoveryUntil:J\n\n.field touchBusy:Z')
text = replace(text, '.method inspect()V', r'''.method recoverReading()V
    .locals 4

    iget v0, p0, Lbr/leo/assistente/RideService;->generation:I
    add-int/lit8 v0, v0, 0x1
    iput v0, p0, Lbr/leo/assistente/RideService;->generation:I

    const/4 v0, 0x0
    iput-boolean v0, p0, Lbr/leo/assistente/RideService;->touchBusy:Z
    iput-boolean v0, p0, Lbr/leo/assistente/RideService;->shotBusy:Z
    iput-object v0, p0, Lbr/leo/assistente/RideService;->pendingVerification:Lbr/leo/assistente/RideService$ImageResult;

    iget-object v0, p0, Lbr/leo/assistente/RideService;->offerEvidence:Lbr/leo/assistente/OfferEvidenceGate;
    invoke-virtual {v0}, Lbr/leo/assistente/OfferEvidenceGate;->reset()V

    invoke-static {}, Landroid/os/SystemClock;->uptimeMillis()J
    move-result-wide v0
    const-wide/16 v2, 0x3e8
    add-long/2addr v0, v2
    iput-wide v0, p0, Lbr/leo/assistente/RideService;->recoveryUntil:J
    return-void
.end method

.method inspect()V''')
text = method(text, '.method inspect()V', lambda body: replace(
    replace(body, '    move-result-wide v4', '''    move-result-wide v4

    iget-wide v0, v7, Lbr/leo/assistente/RideService;->recoveryUntil:J
    cmp-long v2, v4, v0
    if-gez v2, :ready_to_read
    return-void
    :ready_to_read'''),
    '    invoke-virtual/range {p0 .. p0}, Lbr/leo/assistente/RideService;->stop()V\n\n    const-string v0, "Android n\\u00e3o confirmou o gesto. Reative a acessibilidade."',
    '    invoke-virtual/range {p0 .. p0}, Lbr/leo/assistente/RideService;->recoverReading()V\n\n    const-string v0, "Gesto sem retorno. Aguardando nova leitura do 99."'))
text = method(text, '.method dispatchAction(', lambda body: replace(
    body, '    if-nez v0, :cond_33\n\n    iget-boolean v0, v11, Lbr/leo/assistente/RideService;->interactingOverlay:Z',
    '''    if-nez v0, :cond_33

    iget-wide v0, v11, Lbr/leo/assistente/RideService;->recoveryUntil:J
    cmp-long v2, v9, v0
    if-ltz v2, :cond_33

    iget-boolean v0, v11, Lbr/leo/assistente/RideService;->interactingOverlay:Z'''))
text = method(text, '.method dispatchAction(', lambda body: replace(body, '''    const-string v5, "highestBid"

    invoke-interface {v3, v5, v13}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v5

    if-eqz v5, :cond_b''', '''    # Em negociação acessível, procurar sempre a proposta máxima do card.
    iget v5, v11, Lbr/leo/assistente/RideService;->phase:I
    const/4 v6, 0x3
    if-ne v5, v6, :find_bid

    iget-object v5, v11, Lbr/leo/assistente/RideService;->confirmation:Lbr/leo/assistente/ConfirmationGate;
    invoke-virtual {v5, v9, v10}, Lbr/leo/assistente/ConfirmationGate;->pending(J)Z
    move-result v5
    if-eqz v5, :find_bid
    return v13

    :find_bid'''))
text = method(text, '.method dispatchAction(', lambda body: replace(body, '''    const-string v0, "filter"

    move/from16 p3, v6

    const/4 v6, 0x0

    invoke-interface {v3, v0, v6}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0''', '''    move/from16 p3, v6
    const/4 v0, 0x0'''))
text = replace(text, '''    const-string v4, "filter"

    invoke-interface {v2, v4, v13}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v2''', '''    const/4 v2, 0x0''')
text = replace(text, 'NURK 0.61', 'NURK 0.62')
service.write_text(text)

tick = smali / "RideService$1.smali"
tick.write_text(replace(tick.read_text(),
    '    invoke-virtual {v1}, Lbr/leo/assistente/RideService;->stop()V\n\n    new-instance v1, Ljava/lang/StringBuilder;\n\n    const-string v2, "Pausado por erro de leitura: "',
    '    invoke-virtual {v1}, Lbr/leo/assistente/RideService;->recoverReading()V\n\n    new-instance v1, Ljava/lang/StringBuilder;\n\n    const-string v2, "Nova leitura em instantes: "'))

activity = smali / "MainActivity.smali"
activity.write_text(replace(replace(activity.read_text(),
    '    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->addMinimumFare(Landroid/widget/LinearLayout;)V',
    '    # O filtro antigo não é exibido na versão 0.62.'),
    'NURK CORP. \\u00b7 0.61', 'NURK CORP. \\u00b7 0.62'))

gate = smali / "ConfirmationGate.smali"
gate.write_text(replace(gate.read_text(), 'const-wide/16 p4, 0x12c', 'const-wide/16 p4, 0x96'))

config = root / "apktool.yml"
config.write_text(replace(config.read_text(), 'versionCode: 61\n  versionName: 0.61', 'versionCode: 62\n  versionName: 0.62'))


def move_sound_before_storage(body):
    start = body.index('    const-string v1, "nurk_settings"')
    end = body.index('    goto :goto_0', start)
    sound = body[start:end]
    return replace(
        body[:start] + body[end:],
        '    .line 257\n',
        '''    iget-object v0, p0, Lbr/leo/assistente/RideService;->confirmation:Lbr/leo/assistente/ConfirmationGate;
    iget-boolean v1, v0, Lbr/leo/assistente/ConfirmationGate;->sounded:Z
    if-nez v1, :persist_confirmation
    const/4 v1, 0x1
    iput-boolean v1, v0, Lbr/leo/assistente/ConfirmationGate;->sounded:Z
    move v0, v1
''' + sound.replace(':cond_1', ':silent_confirmation') + '''
    goto :persist_confirmation

    :silent_confirmation
    const-string v0, "Som desativado"
    const-string v1, "Navega\\u00e7\\u00e3o confirmada, mas o aviso sonoro est\\u00e1 desativado nas prefer\\u00eancias."
    invoke-virtual {p0, v0, v1}, Lbr/leo/assistente/RideService;->report(Ljava/lang/String;Ljava/lang/String;)V

    :persist_confirmation
    .line 257
''')


def confirm(body):
    body = move_sound_before_storage(body)
    return body[:body.index('    :cond_1')]


service.write_text(method(service.read_text(), '.method confirmedNavigation()V', confirm))
gate.write_text(replace(replace(gate.read_text(),
    '.field delivered:Z', '.field delivered:Z\n\n.field sounded:Z'),
    '    iput-boolean v0, p0, Lbr/leo/assistente/ConfirmationGate;->delivered:Z',
    '    iput-boolean v0, p0, Lbr/leo/assistente/ConfirmationGate;->delivered:Z\n'
    '    iput-boolean v0, p0, Lbr/leo/assistente/ConfirmationGate;->sounded:Z'))
