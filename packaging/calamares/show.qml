/* Slides do instalador do Sururu Linux */
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation

    function nextSlide() { presentation.goToNextSlide(); }

    Timer {
        id: avancar
        interval: 9000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: nextSlide()
    }

    Rectangle { anchors.fill: parent; color: "#0F3B40"; z: -1 }

    Slide {
        Image { id: concha1; source: "logo.png"; width: 140; height: 140; fillMode: Image.PreserveAspectFit
                anchors.horizontalCenter: parent.horizontalCenter; anchors.top: parent.top; anchors.topMargin: 30 }
        Text { anchors.top: concha1.bottom; anchors.topMargin: 20; width: parent.width; horizontalAlignment: Text.AlignHCenter
               color: "#E7F1EF"; font.pixelSize: 26; font.bold: true; text: "Bem-vindo ao Sururu Linux" }
        Text { anchors.top: concha1.bottom; anchors.topMargin: 66; width: parent.width * 0.8; anchors.horizontalCenter: parent.horizontalCenter
               horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; color: "#A9C9D0"; font.pixelSize: 16
               text: "Linux, containers e Kubernetes sem bicho de sete cabeças. Enquanto instalamos, tome um café." }
    }
    Slide {
        Text { anchors.centerIn: parent; width: parent.width * 0.8; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
               color: "#E7F1EF"; font.pixelSize: 20
               text: "<b>Central Sururu</b><br><br>Crie seu cluster Kubernetes com um clique e faça laboratórios que se corrigem sozinhos. Fica na concha da barra de tarefas." }
    }
    Slide {
        Text { anchors.centerIn: parent; width: parent.width * 0.8; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
               color: "#E7F1EF"; font.pixelSize: 20
               text: "<b>Seguro e estável</b><br><br>Por baixo é Debian 13. As atualizações de segurança chegam direto do Debian, pelo apt." }
    }
    Slide {
        Text { anchors.centerIn: parent; width: parent.width * 0.8; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
               color: "#E7F1EF"; font.pixelSize: 20
               text: "<b>Feito pela comunidade</b><br><br>O Sururu é livre. Achou um erro ou quer escrever um laboratório? Participe no GitHub do projeto." }
    }

    function onActivate() { presentation.currentSlide = 0; }
    function onLeave() { }
}
