"""Aplica a atualização ao diretório intermediário gerado pelo patch 0.62."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
smali = root / "smali/br/leo/assistente"


def replace(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Trecho inesperado: {before!r}")
    return text.replace(before, after)


def change(path, before, after):
    path.write_text(replace(path.read_text(), before, after))


def method(text, marker, transform):
    start = text.index(marker)
    end = text.index(".end method", start)
    return text[:start] + transform(text[start:end]) + text[end:]


activity = smali / "MainActivity.smali"
text = activity.read_text()
text = replace(text, '    # O filtro antigo não é exibido na versão 0.62.\n\n', '')
text = replace(text, '    const-string v14, "Seu assistente"', '    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->addMinimumFare(Landroid/widget/LinearLayout;)V\n\n    const-string v14, "Seu assistente"')
# Put the minimum card before the start card.
text = replace(text, '''    .line 29
    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v7

    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->addMinimumFare(Landroid/widget/LinearLayout;)V''', '''    .line 29
    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->addMinimumFare(Landroid/widget/LinearLayout;)V

    invoke-virtual {v0, v4}, Lbr/leo/assistente/MainActivity;->card(Landroid/widget/LinearLayout;)Landroid/widget/LinearLayout;

    move-result-object v7''')
start = text.index('    .line 66\n    iget-object v1')
end = text.index('    .line 68', start)
text = text[:start] + text[end:]
activity.write_text(replace(text, 'NURK CORP. \\u00b7 0.62', 'NURK CORP. \\u00b7 0.63'))

service = smali / "RideService.smali"
text = service.read_text()
text = replace(text, 'NURK 0.62', 'NURK 0.63')
text = method(text, '.method dispatchAction(', lambda b: replace(b,
    '''    move/from16 p3, v6
    const/4 v0, 0x0

    if-eqz v0, :cond_16''',
    '''    move/from16 p3, v6
    const-string v0, "filter"
    const/4 v6, 0x0
    invoke-interface {v3, v0, v6}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v0
    if-eqz v0, :cond_16'''))
text = replace(text, '''    move-result-object v2

    const/4 v2, 0x0

    if-nez v2, :cond_7

    .line 476''', '''    move-result-object v2

    const-string v4, "filter"
    invoke-interface {v2, v4, v13}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v2
    if-nez v2, :cond_7

    .line 476''')
text = method(text, '.method inspect()V', lambda b: replace(b, '''    .line 719
    :cond_1
    invoke-virtual/range''', '''    .line 719
    :cond_1
    iget-boolean v0, v7, Lbr/leo/assistente/RideService;->shotBusy:Z
    if-eqz v0, :read_window
    iget-wide v0, v7, Lbr/leo/assistente/RideService;->lastShot:J
    sub-long v0, v4, v0
    const-wide/16 v2, 0x1388
    cmp-long v0, v0, v2
    if-lez v0, :read_window
    invoke-virtual {v7}, Lbr/leo/assistente/RideService;->recoverReading()V
    const-string v0, "Captura sem retorno. Retomando a leitura do 99."
    sput-object v0, Lbr/leo/assistente/RideService;->status:Ljava/lang/String;
    return-void

    :read_window
    invoke-virtual/range'''))
text = method(text, '.method inspect()V', lambda b: replace(b, '''    iget v0, v7, Lbr/leo/assistente/RideService;->phase:I

    if-ne v0, v1, :cond_5

    iput v6, v7, Lbr/leo/assistente/RideService;->phase:I

    :cond_5''', '''    # Uma janela temporária do sistema não muda a fase da proposta.'''))
text = method(text, '.method dispatchAction(', lambda b: replace(b, '''    if-eqz v5, :cond_b

    # Em negociação acessível''', '''    if-nez v5, :negotiation_text
    const-string v5, "enviar proposta"
    invoke-virtual {v2, v5}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v5
    if-eqz v5, :cond_b

    :negotiation_text
    # Em negociação acessível'''))
text = method(text, '.method highestBid(', lambda b: replace(b, '''    invoke-virtual {v1}, Ljava/lang/Long;->longValue()J

    move-result-wide v3''', '''    const-wide/16 v3, 0x0'''))
# A recognized retry control can reopen a proposal even if the old accept label is visible.
text = method(text, '.method inspect()V', lambda b: replace(b, '''    if-nez v13, :cond_1b

    if-eqz v9, :cond_1b''', '''    if-eqz v13, :retry_available
    iget v13, v7, Lbr/leo/assistente/RideService;->phase:I
    if-ne v13, v1, :cond_1b

    :retry_available
    if-eqz v9, :cond_1b'''))
# Match the actual control also when 99 omits the verb "fazer".
rules = smali / "Rules.smali"
rules.write_text(method(rules.read_text(), '.method public static renew(', lambda b: replace(b, '''    move-result p0

    return p0''', '''    move-result v0
    if-nez v0, :recognized
    const-string v0, "nova oferta"
    invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    :recognized
    return v0''')))
# Prevent the known visual negotiation template from using the base-accept coordinates.
text = replace(text, '''    if-eqz p2, :cond_3

    aget p1, p2, v2

    aget p2, p2, v3

    filled-new-array {v1, p1, p2}, [I

    move-result-object p1

    return-object p1''', '''    if-eqz p2, :cond_3

    return-object v0''')
# Ask for the second visual confirmation sooner without removing the two-frame requirement.
text = replace(text, 'const/16 v0, 0x15e', 'const/16 v0, 0xfa')
text = replace(text, 'const/16 p1, 0x15e', 'const/16 p1, 0xfa')
service.write_text(text)

change(root / "apktool.yml", 'versionCode: 62\n  versionName: 0.62', 'versionCode: 63\n  versionName: 0.63')

sound = smali / "ConfirmationSound.smali"
text = sound.read_text()
text = replace(text, '.field private player:Landroid/media/MediaPlayer;', '''.field private player:Landroid/media/MediaPlayer;

.field private pool:Landroid/media/SoundPool;

.field private sample:I

.field private stream:I''')
text += r'''
.method preload(Landroid/content/Context;)V
    .locals 4
    iget-object v0, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;
    if-nez v0, :done
    :try_start
    new-instance v0, Landroid/media/SoundPool;
    const/4 v1, 0x1
    const/4 v2, 0x3
    const/4 v3, 0x0
    invoke-direct {v0, v1, v2, v3}, Landroid/media/SoundPool;-><init>(III)V
    iput-object v0, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;

    invoke-virtual {p1}, Landroid/content/Context;->getAssets()Landroid/content/res/AssetManager;
    move-result-object v2
    const-string v3, "nurk-confirmed.wav"
    invoke-virtual {v2, v3}, Landroid/content/res/AssetManager;->openFd(Ljava/lang/String;)Landroid/content/res/AssetFileDescriptor;
    move-result-object v2
    :load_start
    invoke-virtual {v0, v2, v1}, Landroid/media/SoundPool;->load(Landroid/content/res/AssetFileDescriptor;I)I
    move-result v1
    iput v1, p0, Lbr/leo/assistente/ConfirmationSound;->sample:I
    :load_end
    .catchall {:load_start .. :load_end} :close_asset
    invoke-virtual {v2}, Landroid/content/res/AssetFileDescriptor;->close()V
    goto :done

    :close_asset
    move-exception v3
    invoke-virtual {v2}, Landroid/content/res/AssetFileDescriptor;->close()V
    throw v3
    :try_end
    .catch Ljava/lang/Exception; {:try_start .. :try_end} :unavailable

    :unavailable
    move-exception v0
    invoke-virtual {p0}, Lbr/leo/assistente/ConfirmationSound;->releasePool()V

    :done
    return-void
.end method

.method private playLoaded()Z
    .locals 7
    iget-object v0, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;
    if-eqz v0, :unavailable
    iget v1, p0, Lbr/leo/assistente/ConfirmationSound;->sample:I
    if-eqz v1, :unavailable
    const/high16 v2, 0x3f800000
    move v3, v2
    const/4 v4, 0x1
    const/4 v5, 0x0
    move v6, v2
    invoke-virtual/range {v0 .. v6}, Landroid/media/SoundPool;->play(IFFIIF)I
    move-result v0
    if-eqz v0, :unavailable
    iput v0, p0, Lbr/leo/assistente/ConfirmationSound;->stream:I
    const-string v0, "Reproduzindo os três toques"
    iput-object v0, p0, Lbr/leo/assistente/ConfirmationSound;->state:Ljava/lang/String;
    const/4 v0, 0x1
    return v0

    :unavailable
    const/4 v0, 0x0
    return v0
.end method

.method releasePool()V
    .locals 2
    iget-object v0, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;
    if-eqz v0, :done
    invoke-virtual {v0}, Landroid/media/SoundPool;->release()V
    const/4 v1, 0x0
    iput-object v1, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;
    iput v1, p0, Lbr/leo/assistente/ConfirmationSound;->sample:I
    iput v1, p0, Lbr/leo/assistente/ConfirmationSound;->stream:I

    :done
    return-void
.end method
'''
text = method(text, '.method play(Landroid/content/Context;)Z', lambda b: replace(b,
    '''    :cond_0
    new-instance v0, Landroid/media/AudioAttributes$Builder;''',
    '''    :cond_0
    invoke-direct {p0}, Lbr/leo/assistente/ConfirmationSound;->playLoaded()Z
    move-result v0
    if-eqz v0, :fallback_player
    invoke-virtual {v6}, Landroid/media/MediaPlayer;->release()V
    const/4 v1, 0x0
    iput-object v1, p0, Lbr/leo/assistente/ConfirmationSound;->player:Landroid/media/MediaPlayer;
    const/4 v0, 0x1
    return v0

    :fallback_player
    new-instance v0, Landroid/media/AudioAttributes$Builder;'''))
text = method(text, '.method stop()V', lambda b: b.replace('.locals 2', '.locals 3').replace(
    '    .line 15', '''    iget-object v1, p0, Lbr/leo/assistente/ConfirmationSound;->pool:Landroid/media/SoundPool;
    if-eqz v1, :stop_player
    iget v2, p0, Lbr/leo/assistente/ConfirmationSound;->stream:I
    if-eqz v2, :stop_player
    invoke-virtual {v1, v2}, Landroid/media/SoundPool;->stop(I)V
    const/4 v2, 0x0
    iput v2, p0, Lbr/leo/assistente/ConfirmationSound;->stream:I
    :stop_player
    .line 15'''))
sound.write_text(text)

text = service.read_text()
text = method(text, '.method arm(IZZ)V', lambda b: b.replace(
    '    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->stop()V',
    '''    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->stop()V
    iget-object v0, p0, Lbr/leo/assistente/RideService;->confirmationSound:Lbr/leo/assistente/ConfirmationSound;
    invoke-virtual {v0, p0}, Lbr/leo/assistente/ConfirmationSound;->preload(Landroid/content/Context;)V''', 1))
text = method(text, '.method public onDestroy()V', lambda b: replace(b,
    '    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->stop()V',
    '''    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->stop()V
    iget-object v0, p0, Lbr/leo/assistente/RideService;->confirmationSound:Lbr/leo/assistente/ConfirmationSound;
    invoke-virtual {v0}, Lbr/leo/assistente/ConfirmationSound;->releasePool()V'''))
service.write_text(text)

version = smali / "VersionGate.smali"
text = version.read_text()
text = replace(text, '.field private static volatile installed:I', '''.field private static volatile installed:I

.field private static volatile downloadContext:Landroid/content/Context;''')
text = replace(text, '''    .line 27
    const-string v1, "release_policy"''', '''    sput-object p0, Lbr/leo/assistente/VersionGate;->downloadContext:Landroid/content/Context;

    .line 27
    const-string v1, "release_policy"''')
text = replace(text, '''    const-string v5, "minimumVersionCode"

    invoke-virtual {v1, v5}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I''', '''    invoke-static {v1}, Lbr/leo/assistente/VersionGate;->downloadLatest(Lorg/json/JSONObject;)V

    const-string v5, "minimumVersionCode"

    invoke-virtual {v1, v5}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I''')
text += r'''
.method private static downloadLatest(Lorg/json/JSONObject;)V
    .locals 7
    :try_start
    const-string v0, "latestVersionCode"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I
    move-result v2
    sget v0, Lbr/leo/assistente/VersionGate;->installed:I
    if-lez v0, :done
    if-le v2, v0, :done
    sget-object v0, Lbr/leo/assistente/VersionGate;->downloadContext:Landroid/content/Context;
    if-eqz v0, :done

    const-string v3, "release_policy"
    invoke-virtual {v0, v3, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v3
    const-string v4, "queued_release"
    invoke-interface {v3, v4, v1}, Landroid/content/SharedPreferences;->getInt(Ljava/lang/String;I)I
    move-result v1
    if-ge v1, v2, :done

    new-instance v1, Ljava/lang/StringBuilder;
    const-string v5, "https://leeostark.github.io/Nurk-assistente-/NURK-v"
    invoke-direct {v1, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v5, ".apk"
    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v1}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;
    move-result-object v1
    new-instance v5, Landroid/app/DownloadManager$Request;
    invoke-direct {v5, v1}, Landroid/app/DownloadManager$Request;-><init>(Landroid/net/Uri;)V
    const-string v1, "Atualização do NURK Assistente"
    invoke-virtual {v5, v1}, Landroid/app/DownloadManager$Request;->setTitle(Ljava/lang/CharSequence;)Landroid/app/DownloadManager$Request;
    const-string v1, "application/vnd.android.package-archive"
    invoke-virtual {v5, v1}, Landroid/app/DownloadManager$Request;->setMimeType(Ljava/lang/String;)Landroid/app/DownloadManager$Request;
    const/4 v1, 0x1
    invoke-virtual {v5, v1}, Landroid/app/DownloadManager$Request;->setNotificationVisibility(I)Landroid/app/DownloadManager$Request;
    const-string v1, "download"
    invoke-virtual {v0, v1}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v6
    check-cast v6, Landroid/app/DownloadManager;
    if-eqz v6, :done
    invoke-virtual {v6, v5}, Landroid/app/DownloadManager;->enqueue(Landroid/app/DownloadManager$Request;)J
    invoke-interface {v3}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    invoke-interface {v0, v4, v2}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end
    .catch Ljava/lang/RuntimeException; {:try_start .. :try_end} :unavailable
    :done
    return-void

    :unavailable
    move-exception v0
    return-void
.end method
'''
version.write_text(text)

text = service.read_text()
text = replace(text, '.field recoveryUntil:J', '''.field recoveryUntil:J

.field proposalSendDeadline:J

.field proposalWindow:I''')
text = method(text, '.method dispatchAction(', lambda b: replace(replace(replace(replace(
    b, '.locals 22', '.locals 23'),
    '    move-object/from16 v8, p5\n\n    invoke-static {},',
    '    move-object/from16 v8, p5\n    const/16 v22, 0x0\n\n    invoke-static {},'),
    '''    if-eqz v5, :cond_9

    iget v4, v11''',
    '''    if-eqz v5, :cond_9

    # Only follow a send button that becomes actionable after choosing the preset.
    invoke-virtual {v11, v1}, Lbr/leo/assistente/RideService;->proposalButton(Ljava/util/List;)Landroid/view/accessibility/AccessibilityNodeInfo;
    move-result-object v4
    if-nez v4, :check_bid_phase
    const/16 v22, 0x1
    :check_bid_phase
    iget v4, v11'''),
    '''    invoke-virtual {v11, v12}, Lbr/leo/assistente/RideService;->markActionQueued(I)V

    .line 384''',
    '''    invoke-virtual {v11, v12}, Lbr/leo/assistente/RideService;->markActionQueued(I)V

    move/from16 v0, v22
    if-eqz v0, :gesture_queued
    move-object/from16 v0, p1
    invoke-virtual {v0}, Landroid/view/accessibility/AccessibilityNodeInfo;->getWindowId()I
    move-result v0
    iput v0, v11, Lbr/leo/assistente/RideService;->proposalWindow:I
    iget-wide v0, v11, Lbr/leo/assistente/RideService;->touchAt:J
    const-wide/16 v2, 0x1770
    add-long/2addr v0, v2
    iput-wide v0, v11, Lbr/leo/assistente/RideService;->proposalSendDeadline:J

    :gesture_queued
    .line 384'''))
text = method(text, '.method inspect()V', lambda b: replace(b,
    '''    :cond_14
    iget v13, v7, Lbr/leo/assistente/RideService;->phase:I''',
    '''    :cond_14
    invoke-virtual {v7, v0, v8, v4, v5}, Lbr/leo/assistente/RideService;->sendSelectedProposal(Landroid/view/accessibility/AccessibilityNodeInfo;Ljava/util/List;J)Z
    move-result v13
    if-eqz v13, :inspect_offers
    return-void

    :inspect_offers
    iget v13, v7, Lbr/leo/assistente/RideService;->phase:I'''))
text += r'''
.method private proposalButton(Ljava/util/List;)Landroid/view/accessibility/AccessibilityNodeInfo;
    .locals 4
    const/4 v0, 0x0
    const/4 v1, 0x0
    invoke-interface {p1}, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p1

    :next_node
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :finished
    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Landroid/view/accessibility/AccessibilityNodeInfo;
    invoke-static {v2}, Lbr/leo/assistente/FareReader;->text(Landroid/view/accessibility/AccessibilityNodeInfo;)Ljava/lang/String;
    move-result-object v3
    invoke-virtual {p0, v3}, Lbr/leo/assistente/RideService;->buttonLabel(Ljava/lang/CharSequence;)Ljava/lang/String;
    move-result-object v3
    const-string v0, "enviar proposta"
    invoke-virtual {v0, v3}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :next_node
    invoke-virtual {p0, v2}, Lbr/leo/assistente/RideService;->clickableControl(Landroid/view/accessibility/AccessibilityNodeInfo;)Landroid/view/accessibility/AccessibilityNodeInfo;
    move-result-object v2
    if-eqz v2, :next_node
    if-eqz v1, :found
    invoke-virtual {v1, v2}, Landroid/view/accessibility/AccessibilityNodeInfo;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :next_node
    const/4 v0, 0x0
    return-object v0

    :found
    move-object v1, v2
    goto :next_node

    :finished
    return-object v1
.end method

.method private sendSelectedProposal(Landroid/view/accessibility/AccessibilityNodeInfo;Ljava/util/List;J)Z
    .locals 4
    const/4 v0, 0x0
    iget v1, p0, Lbr/leo/assistente/RideService;->phase:I
    const/4 v2, 0x3
    if-ne v1, v2, :done
    iget-wide v1, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J
    cmp-long v1, p3, v1
    if-lez v1, :done
    iget-object v1, p0, Lbr/leo/assistente/RideService;->confirmation:Lbr/leo/assistente/ConfirmationGate;
    invoke-virtual {v1, p3, p4}, Lbr/leo/assistente/ConfirmationGate;->pending(J)Z
    move-result v1
    if-eqz v1, :done
    invoke-virtual {p1}, Landroid/view/accessibility/AccessibilityNodeInfo;->getWindowId()I
    move-result v1
    iget v2, p0, Lbr/leo/assistente/RideService;->proposalWindow:I
    if-ne v1, v2, :done
    invoke-direct {p0, p2}, Lbr/leo/assistente/RideService;->proposalButton(Ljava/util/List;)Landroid/view/accessibility/AccessibilityNodeInfo;
    move-result-object v1
    if-eqz v1, :done
    const-wide/16 v2, 0x0
    iput-wide v2, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J
    const/16 v2, 0x10
    invoke-virtual {v1, v2}, Landroid/view/accessibility/AccessibilityNodeInfo;->performAction(I)Z
    move-result v0
    if-eqz v0, :done
    const-string v1, "Proposta enviada"
    const-string v2, "Aguardando a resposta do passageiro."
    invoke-virtual {p0, v1, v2}, Lbr/leo/assistente/RideService;->report(Ljava/lang/String;Ljava/lang/String;)V
    :done
    return v0
.end method
'''
# Direct methods must use invoke-direct.
text = text.replace('invoke-virtual {v11, v1}, Lbr/leo/assistente/RideService;->proposalButton', 'invoke-direct {v11, v1}, Lbr/leo/assistente/RideService;->proposalButton')
text = text.replace('invoke-virtual {v7, v0, v8, v4, v5}, Lbr/leo/assistente/RideService;->sendSelectedProposal', 'invoke-direct {v7, v0, v8, v4, v5}, Lbr/leo/assistente/RideService;->sendSelectedProposal')
service.write_text(text)

text = service.read_text()
text = method(text, '.method dispatchAction(', lambda b: replace(b, '''    .line 356
    const-string v9,''', '''    move/from16 v0, v22
    if-eqz v0, :record_direct_click
    move-object/from16 v0, p1
    invoke-direct {v11, v0}, Lbr/leo/assistente/RideService;->allowProposalSend(Landroid/view/accessibility/AccessibilityNodeInfo;)V

    :record_direct_click
    .line 356
    const-string v9,'''))
text = method(text, '.method dispatchAction(', lambda b: replace(b, '''    invoke-virtual {v0}, Landroid/view/accessibility/AccessibilityNodeInfo;->getWindowId()I
    move-result v0
    iput v0, v11, Lbr/leo/assistente/RideService;->proposalWindow:I
    iget-wide v0, v11, Lbr/leo/assistente/RideService;->touchAt:J
    const-wide/16 v2, 0x1770
    add-long/2addr v0, v2
    iput-wide v0, v11, Lbr/leo/assistente/RideService;->proposalSendDeadline:J''', '''    invoke-direct {v11, v0}, Lbr/leo/assistente/RideService;->allowProposalSend(Landroid/view/accessibility/AccessibilityNodeInfo;)V'''))
text += r'''
.method private allowProposalSend(Landroid/view/accessibility/AccessibilityNodeInfo;)V
    .locals 4
    invoke-virtual {p1}, Landroid/view/accessibility/AccessibilityNodeInfo;->getWindowId()I
    move-result v0
    iput v0, p0, Lbr/leo/assistente/RideService;->proposalWindow:I
    iget-wide v0, p0, Lbr/leo/assistente/RideService;->lastAction:J
    const-wide/16 v2, 0x1770
    add-long/2addr v0, v2
    iput-wide v0, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J
    return-void
.end method
'''
text = method(text, '.method private sendSelectedProposal(', lambda b: replace(b, '''    const-wide/16 v2, 0x0
    iput-wide v2, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J''', '''    invoke-virtual {v1}, Landroid/view/accessibility/AccessibilityNodeInfo;->refresh()Z
    move-result v2
    if-eqz v2, :done
    invoke-virtual {p0, v1}, Lbr/leo/assistente/RideService;->clickableControl(Landroid/view/accessibility/AccessibilityNodeInfo;)Landroid/view/accessibility/AccessibilityNodeInfo;
    move-result-object v1
    if-eqz v1, :done
    new-instance v2, Landroid/graphics/Rect;
    invoke-direct {v2}, Landroid/graphics/Rect;-><init>()V
    invoke-virtual {v1, v2}, Landroid/view/accessibility/AccessibilityNodeInfo;->getBoundsInScreen(Landroid/graphics/Rect;)V
    invoke-virtual {v2}, Landroid/graphics/Rect;->isEmpty()Z
    move-result v3
    if-nez v3, :done
    invoke-virtual {v2}, Landroid/graphics/Rect;->centerX()I
    move-result v3
    invoke-virtual {v2}, Landroid/graphics/Rect;->centerY()I
    move-result v2
    invoke-virtual {p0, v3, v2}, Lbr/leo/assistente/RideService;->targetClear(II)Z
    move-result v2
    if-eqz v2, :done
    const-wide/16 v2, 0x0
    iput-wide v2, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J'''))
text = method(text, '.method resetConfirmation()V', lambda b: replace(b,
    '    .locals 1', '''    .locals 2
    const-wide/16 v0, 0x0
    iput-wide v0, p0, Lbr/leo/assistente/RideService;->proposalSendDeadline:J'''))
text = method(text, '.method public onInterrupt()V', lambda b: replace(b,
    '''    .locals 0

    .line 104
    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->stop()V''',
    '''    .locals 1

    .line 104
    iget-object v0, p0, Lbr/leo/assistente/RideService;->confirmationSound:Lbr/leo/assistente/ConfirmationSound;
    invoke-virtual {v0}, Lbr/leo/assistente/ConfirmationSound;->stop()V
    iget-boolean v0, p0, Lbr/leo/assistente/RideService;->armed:Z
    if-eqz v0, :paused
    invoke-virtual {p0}, Lbr/leo/assistente/RideService;->recoverReading()V
    :paused'''))
service.write_text(text)
