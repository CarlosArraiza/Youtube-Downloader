pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: win
    visible: true
    width: 1040; height: 560
    minimumWidth: 860; minimumHeight: 540
    title: "YouTube Downloader"
    property var state: backend.data
    readonly property var videoInfo: backend.videoInfo
    readonly property var settings: backend.config
    readonly property var entries: backend.entries
    readonly property var allFormats: ["mp4", "mkv", "avi", "webm", "mov", "mp3", "aac", "flac", "ogg", "wav", "m4a"]
    readonly property var audioQualities: ["320kbps", "192kbps", "128kbps"]
    readonly property var videoQualities: ["Mejor disponible", "2160p", "1440p", "1080p", "720p", "480p", "360p", "144p"]
    property int page: 0
    property string theme: win.settings.theme
    readonly property bool dark: theme === "dark" || (theme === "system" && Application.styleHints.colorScheme === Qt.ColorScheme.Dark)
    readonly property color bg: dark ? "#181d24" : "#f5f7fb"
    readonly property color surface: dark ? "#202731" : "#ffffff"
    readonly property color field: dark ? "#252e39" : "#f8fafd"
    readonly property color ink: dark ? "#edf2fa" : "#172337"
    readonly property color muted: dark ? "#a0afc2" : "#5c6c81"
    readonly property color line: dark ? "#374351" : "#dce3ed"
    readonly property color accent: "#1976df"
    readonly property bool locked: win.state.searching || win.state.downloading
    readonly property bool audio: ["mp3", "aac", "flac", "ogg", "wav", "m4a"].indexOf(format.currentText) >= 0
    readonly property var qualities: audio ? win.audioQualities : (win.videoInfo.formats || [])
    color: win.bg
    background: Rectangle { color: win.bg }
    font.family: "Segoe UI"
    font.pixelSize: 14
    palette.window: bg
    palette.windowText: ink
    palette.base: field
    palette.text: ink
    palette.button: surface
    palette.buttonText: ink
    palette.highlight: accent
    palette.highlightedText: "white"
    palette.mid: line
    palette.dark: line
    Behavior on color { ColorAnimation { duration: 160 } }

    component Copy: Label {
        color: win.ink
        elide: Text.ElideRight
        textFormat: Text.PlainText
    }
    component Action: Button {
        id: control
        property bool primary: false
        implicitHeight: 40
        leftPadding: 16; rightPadding: 16
        contentItem: Text {
            text: control.text
            font: control.font
            color: !control.enabled ? win.muted : control.primary ? "white" : win.ink
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            radius: 7
            color: control.primary ? (control.enabled ? (control.down ? "#1059ae" : control.hovered ? "#1469ca" : win.accent) : win.line) : (control.hovered ? win.field : win.surface)
            border.color: control.activeFocus ? win.accent : control.primary ? "transparent" : win.line
            border.width: control.activeFocus ? 2 : 1
            Behavior on color { ColorAnimation { duration: 100 } }
        }
    }
    component Input: TextField {
        id: input
        implicitHeight: 42
        color: win.ink
        placeholderTextColor: win.muted
        selectByMouse: true
        leftPadding: 12; rightPadding: 12
        background: Rectangle {
            radius: 7; color: win.field
            border.color: input.activeFocus ? win.accent : win.line
            border.width: input.activeFocus ? 2 : 1
        }
    }
    component Select: ComboBox {
        id: combo
        implicitHeight: 40
        implicitWidth: 180
        leftPadding: 12; rightPadding: 30
        contentItem: Text {
            text: combo.displayText
            color: combo.enabled ? win.ink : win.muted
            font: combo.font
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        background: Rectangle {
            radius: 7; color: win.field
            border.color: combo.activeFocus ? win.accent : win.line
        }
        indicator: Text { x: parent.width - 23; anchors.verticalCenter: parent.verticalCenter; text: "⌄"; color: win.muted }
        delegate: ItemDelegate {
            required property var modelData
            required property int index
            width: combo.width
            text: modelData
            highlighted: combo.highlightedIndex === index
            contentItem: Text { text: modelData; color: win.ink; font: combo.font; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
            background: Rectangle { color: highlighted ? win.field : win.surface }
        }
        popup: Popup {
            objectName: combo.objectName + "Popup"
            y: combo.height + 4; width: combo.width
            padding: 4
            implicitHeight: Math.min(contentItem.implicitHeight + 8, 300)
            background: Rectangle { color: win.surface; radius: 7; border.color: win.line }
            contentItem: ListView {
                clip: true; implicitHeight: contentHeight
                model: combo.popup.visible ? combo.delegateModel : null
                currentIndex: combo.highlightedIndex
                ScrollIndicator.vertical: ScrollIndicator {}
            }
        }
    }
    component Toggle: Switch {
        id: toggle
        implicitWidth: 64
        implicitHeight: 40
        indicator: Rectangle {
            implicitWidth: 52; implicitHeight: 28
            x: (toggle.width - width) / 2
            y: (toggle.height - height) / 2
            radius: 14
            color: toggle.checked ? (win.dark ? "#28a86b" : "#198754") : (win.dark ? "#46515f" : "#c2cbd6")
            border.color: toggle.activeFocus ? win.accent : "transparent"
            border.width: toggle.activeFocus ? 2 : 0
            Behavior on color { ColorAnimation { duration: 140 } }
            Rectangle {
                width: 22; height: 22; radius: 11
                x: 3 + toggle.visualPosition * (parent.width - width - 6)
                y: 3
                color: "#ffffff"
                Behavior on x { NumberAnimation { duration: 140 } }
            }
        }
    }
    component Rule: Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: win.line }
    component Heading: Copy { font.pixelSize: 16; font.weight: Font.DemiBold }

    function chooseQuality() {
        var preferred = audio ? win.settings.default_quality_audio : win.settings.default_quality_video
        var i = qualities.indexOf(preferred)
        quality.currentIndex = i >= 0 ? i : 0
    }
    onQualitiesChanged: chooseQuality()
    onClosing: function(close) {
        if (backend.busy()) { close.accepted = false; closeConfirm.open() }
    }

    header: Rectangle {
        height: 66; color: surface
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: line }
        RowLayout {
            anchors.fill: parent; anchors.leftMargin: 24; anchors.rightMargin: 24; spacing: 6
            Rectangle {
                width: 30; height: 24; radius: 6; color: "#ef303b"
                Label { anchors.centerIn: parent; text: "▶"; color: "white"; font.pixelSize: 14 }
            }
            Copy { text: "YouTube Downloader"; font.weight: Font.DemiBold; Layout.rightMargin: 24 }
            Repeater {
                model: ["Descargar", "Historial", "Configuración", "Acerca de"]
                delegate: Button {
                    required property int index
                    required property string modelData
                    text: modelData + (index === 3 && win.state.updateState === "available" ? " •" : ""); implicitHeight: 65
                    leftPadding: 14; rightPadding: 14
                    onClicked: win.page = index
                    contentItem: Text { text: parent.text; color: win.page === index ? win.accent : win.muted; font: parent.font; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    background: Rectangle {
                        color: parent.hovered ? win.field : "transparent"
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 3; color: win.accent; visible: win.page === index }
                    }
                }
            }
            Item { Layout.fillWidth: true }
        }
    }

    StackLayout {
        anchors.fill: parent
        anchors.margins: 24
        currentIndex: win.page

        // Essential: one URL row, preview beside options, action and progress below.
        ColumnLayout {
            spacing: 20
            RowLayout {
                spacing: 12
                Input {
                    id: url
                    objectName: "urlInput"
                    Layout.fillWidth: true
                    placeholderText: "Pega aquí el enlace de YouTube…"
                    enabled: !win.locked
                    onAccepted: backend.analyze(text)
                    Accessible.name: "Enlace de YouTube"
                }
                Action { text: win.state.searching ? "Buscando…" : "Buscar"; primary: true; enabled: !win.locked; onClicked: backend.analyze(url.text) }
            }
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                radius: 10; color: surface; border.color: line
                RowLayout {
                    anchors.fill: parent; anchors.margins: 20; spacing: 24
                    Rectangle {
                        Layout.preferredWidth: Math.min(300, win.width * 0.29)
                        Layout.preferredHeight: width * 9 / 16
                        radius: 8; color: field; clip: true
                        Image { anchors.fill: parent; source: win.videoInfo.thumbnail || ""; fillMode: Image.PreserveAspectCrop; asynchronous: true }
                        Column {
                            anchors.centerIn: parent; spacing: 8; visible: !win.videoInfo.thumbnail
                            Copy { anchors.horizontalCenter: parent.horizontalCenter; text: "↓"; font.pixelSize: 34; color: muted }
                            Copy { text: "La vista previa aparecerá aquí"; color: muted; font.pixelSize: 12 }
                        }
                    }
                    ColumnLayout {
                        spacing: 12; Layout.fillWidth: true
                        Copy { Layout.fillWidth: true; text: win.videoInfo.title || "Tu próxima descarga"; font.pixelSize: 21; font.weight: Font.DemiBold; maximumLineCount: 2; wrapMode: Text.Wrap }
                        Copy {
                            Layout.fillWidth: true; color: muted
                            text: win.videoInfo.uploader ? win.videoInfo.uploader + "  ·  " + Math.floor((win.videoInfo.duration || 0) / 60) + ":" + ("0" + Math.floor((win.videoInfo.duration || 0) % 60)).slice(-2) : "Busca un vídeo para ver sus opciones."
                        }
                        RowLayout {
                            spacing: 12; Layout.topMargin: 8
                            ColumnLayout {
                                Layout.fillWidth: true
                                Copy { text: "Formato"; color: muted; font.pixelSize: 12 }
                                Select {
                                    id: format; Layout.fillWidth: true; model: win.allFormats
                                    objectName: "formatSelect"
                                    currentIndex: model.indexOf(win.settings.default_format)
                                    enabled: !win.locked
                                    onActivated: win.chooseQuality()
                                    Accessible.name: "Formato de descarga"
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                Copy { text: "Calidad"; color: muted; font.pixelSize: 12 }
                                Select { id: quality; objectName: "qualitySelect"; Layout.fillWidth: true; model: win.qualities; enabled: !win.locked && count > 0; displayText: count ? currentText : "Buscar un vídeo"; Accessible.name: "Calidad de descarga" }
                            }
                        }
                        Copy { text: "Carpeta de destino"; color: muted; font.pixelSize: 12; Layout.topMargin: 2 }
                        RowLayout {
                            Input { id: folder; Layout.fillWidth: true; text: win.settings.default_output_path; enabled: !win.locked; Accessible.name: "Carpeta de destino" }
                            Action { text: "Elegir…"; enabled: !win.locked; onClicked: folder.text = backend.chooseFolder(folder.text) }
                        }
                    }
                }
            }
            RowLayout {
                spacing: 16
                BusyIndicator { running: win.state.searching; visible: running; implicitWidth: 30; implicitHeight: 30 }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 6
                    Copy { Layout.fillWidth: true; text: win.state.status; color: win.state.error ? (dark ? "#ff9f9f" : "#b42332") : muted; wrapMode: Text.Wrap; maximumLineCount: 3 }
                    ProgressBar {
                        visible: win.state.downloading || win.state.progress > 0
                        Layout.fillWidth: true; value: win.state.progress
                        background: Rectangle { implicitHeight: 5; radius: 3; color: win.line }
                        contentItem: Item { implicitHeight: 5; Rectangle { width: parent.width * win.state.progress; height: 5; radius: 3; color: win.accent; Behavior on width { NumberAnimation { duration: 140 } } } }
                    }
                    Copy { visible: win.state.downloading; text: Math.round(win.state.progress * 100) + "%  " + win.state.speed; color: muted; font.pixelSize: 12 }
                }
                Action {
                    text: win.state.downloading ? "Cancelar" : "Descargar"
                    primary: !win.state.downloading
                    enabled: win.state.downloading || (!!win.videoInfo.title && !win.state.searching && url.text.trim() !== "")
                    implicitWidth: 160; implicitHeight: 44
                    onClicked: backend.download(url.text, format.currentText, quality.currentText, folder.text)
                }
            }
        }

        ColumnLayout {
            spacing: 16
            RowLayout {
                Heading { text: "Historial" }
                Copy { text: win.entries.length + " descargas"; color: muted; Layout.leftMargin: 8 }
                Item { Layout.fillWidth: true }
                Action { text: "Limpiar historial"; enabled: win.entries.length > 0; onClicked: clearConfirm.open() }
            }
            Copy { visible: win.state.error; Layout.fillWidth: true; text: win.state.status; color: win.dark ? "#ff9f9f" : "#b42332"; wrapMode: Text.Wrap }
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true
                color: surface; radius: 10; border.color: line
                Copy { anchors.centerIn: parent; text: "Tus descargas aparecerán aquí."; color: muted; visible: win.entries.length === 0 }
                ListView {
                    anchors.fill: parent; anchors.margins: 12
                    clip: true; model: win.entries; spacing: 2
                    ScrollBar.vertical: ScrollBar {}
                    delegate: Item {
                        required property var modelData
                        width: ListView.view.width - 12; height: 88
                        RowLayout {
                            anchors.fill: parent; anchors.margins: 8; spacing: 16
                            Rectangle {
                                Layout.preferredWidth: 104; Layout.preferredHeight: 58
                                color: field; radius: 5; clip: true
                                Copy { anchors.centerIn: parent; text: "↓"; color: muted; font.pixelSize: 22 }
                                Image { anchors.fill: parent; source: modelData.thumbnail_url || ""; asynchronous: true; fillMode: Image.PreserveAspectCrop }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true; spacing: 5
                                Copy { Layout.fillWidth: true; text: modelData.title || "Sin título"; font.weight: Font.DemiBold }
                                Copy { Layout.fillWidth: true; color: muted; font.pixelSize: 12; text: [modelData.date, modelData.format, modelData.quality, modelData.size_mb != null ? modelData.size_mb + " MB" : ""].filter(Boolean).join("  ·  ") }
                                Copy { Layout.fillWidth: true; color: muted; font.pixelSize: 12; text: modelData.output_path || "" }
                            }
                            Action { text: "Abrir"; onClicked: backend.openPath(modelData.file_path || "", modelData.output_path || "") }
                        }
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: line }
                    }
                }
            }
        }

        ColumnLayout {
            spacing: 12
            Heading { text: "Configuración" }
            ScrollView {
                id: settingsScroll
                Layout.fillWidth: true; Layout.fillHeight: true
                rightPadding: 20
                contentWidth: availableWidth; clip: true
                ColumnLayout {
                    width: settingsScroll.availableWidth; spacing: 12
                    Heading { text: "Apariencia"; Layout.topMargin: 8 }
                    RowLayout {
                        Copy { text: "Tema"; Layout.fillWidth: true }
                        Select {
                            id: themeSelect; model: ["Claro", "Oscuro", "Sistema"]
                            currentIndex: ["light", "dark", "system"].indexOf(win.theme)
                            onActivated: win.theme = ["light", "dark", "system"][currentIndex]
                        }
                    }
                    Rule {}
                    Heading { text: "Descargas" }
                    RowLayout {
                        Layout.fillWidth: true
                        Copy { text: "Carpeta predeterminada"; Layout.preferredWidth: 240 }
                        Item { Layout.fillWidth: true }
                        Input { id: defaultFolder; text: win.settings.default_output_path; Layout.fillWidth: true; Layout.preferredWidth: 440; Layout.maximumWidth: 440 }
                        Action { text: "Elegir…"; onClicked: defaultFolder.text = backend.chooseFolder(defaultFolder.text) }
                    }
                    RowLayout {
                        Copy { text: "Abrir carpeta al terminar"; Layout.fillWidth: true }
                        Toggle { id: openFolder; checked: win.settings.open_folder_after_download; Accessible.name: "Abrir carpeta al terminar" }
                    }
                    RowLayout {
                        Copy { text: "Formato predeterminado"; Layout.fillWidth: true }
                        Select { id: defaultFormat; model: win.allFormats; currentIndex: model.indexOf(win.settings.default_format) }
                    }
                    RowLayout {
                        Copy { text: "Calidad de vídeo"; Layout.fillWidth: true }
                        Select { id: defaultVideo; model: win.videoQualities; currentIndex: model.indexOf(win.settings.default_quality_video) }
                    }
                    RowLayout {
                        Copy { text: "Calidad de audio"; Layout.fillWidth: true }
                        Select { id: defaultAudio; model: win.audioQualities; currentIndex: model.indexOf(win.settings.default_quality_audio) }
                    }
                    Rule {}
                    Heading { text: "Actualizaciones" }
                    RowLayout {
                        Copy { text: "Buscar actualizaciones al iniciar"; Layout.fillWidth: true }
                        Toggle { id: checkStart; checked: win.settings.check_updates_on_start; Accessible.name: "Buscar actualizaciones al iniciar" }
                    }
                }
            }
            RowLayout {
                Copy { Layout.fillWidth: true; text: win.state.status === "Configuración guardada." || win.state.error ? win.state.status : "Los cambios se aplican al guardar."; color: muted }
                Action {
                    text: "Guardar configuración"; primary: true
                    onClicked: backend.saveSettings({theme: win.theme, default_output_path: defaultFolder.text,
                        open_folder_after_download: openFolder.checked, default_format: defaultFormat.currentText,
                        default_quality_video: defaultVideo.currentText, default_quality_audio: defaultAudio.currentText,
                        check_updates_on_start: checkStart.checked})
                }
            }
        }

        Item {
            Rectangle {
                anchors.centerIn: parent; width: Math.min(parent.width, 620); height: Math.min(parent.height, aboutContent.implicitHeight + 40)
                color: surface; border.color: line; radius: 10
                ScrollView {
                    anchors.fill: parent; anchors.margins: 20; contentWidth: availableWidth; clip: true
                    ColumnLayout {
                        id: aboutContent; width: parent.width; spacing: 14
                        Heading { text: "YouTube Downloader"; font.pixelSize: 23 }
                        Copy { text: "Versión " + win.state.version; color: muted }
                        Copy { Layout.fillWidth: true; text: "Vídeo y audio, guardados a tu manera.\nCon yt-dlp y FFmpeg."; wrapMode: Text.Wrap; color: muted }
                        Action { text: "Ver proyecto en GitHub ↗"; onClicked: Qt.openUrlExternally("https://github.com/cali-sb/Youtube-Downloader") }
                        Rule {}
                        Heading { text: "Actualizaciones" }
                        Copy { Layout.fillWidth: true; text: win.state.updateMessage; wrapMode: Text.Wrap; maximumLineCount: 5; color: muted }
                        ScrollView {
                            visible: !!win.state.updateNotes; Layout.fillWidth: true; Layout.preferredHeight: 110; clip: true
                            TextArea { text: win.state.updateNotes; readOnly: true; wrapMode: Text.Wrap; color: ink; textFormat: TextEdit.PlainText; background: Rectangle { color: field; radius: 6 } }
                        }
                        ProgressBar { visible: win.state.updateState === "downloading"; Layout.fillWidth: true; value: win.state.updateProgress }
                        RowLayout {
                            Action { text: win.state.updateState === "checking" ? "Buscando…" : "Buscar actualizaciones"; enabled: win.state.updateState !== "checking" && win.state.updateState !== "downloading"; onClicked: backend.checkUpdates() }
                            Action { text: win.state.updateState === "downloading" ? "Cancelar" : "Descargar e instalar"; primary: true; visible: win.state.updateState === "available" || win.state.updateState === "downloading"; enabled: !win.state.downloading; onClicked: backend.installUpdate() }
                        }
                    }
                }
            }
        }
    }

    Dialog {
        id: clearConfirm; anchors.centerIn: parent
        title: "¿Limpiar el historial?"; modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        Label { text: "Se eliminarán los registros. Tus archivos se conservarán."; color: ink }
        onAccepted: backend.clearHistory()
    }
    Dialog {
        id: closeConfirm; anchors.centerIn: parent
        title: "Hay una descarga en curso"; modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        Label { text: "¿Quieres cancelar la operación y cerrar el programa?"; color: ink }
        onAccepted: { backend.cancelOnClose(); Qt.quit() }
    }
}
