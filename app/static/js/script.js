const botao_carregar = document.querySelector('.botao_carregar')
const input_arquivo = document.querySelector('.input_form_carregar')
const form = document.querySelector('.form_carregar')
let arquivo_selecionado = false

botao_carregar.addEventListener('click', function () {
    if (!arquivo_selecionado) {
        // abre o seletor de arquivos
        input_arquivo.click();
    } else {
        // envia formulario
        iniciarProgressoCarregar()
    }
});

// detecta quando um arquivo foi selecionado
input_arquivo.addEventListener('change', function () {
    if (input_arquivo.isDefaultNamespace.length > 0) {
        arquivo_selecionado = true
        botao_carregar.textContent = 'Enviar Arquivo'
    }
});



// Barra de Progresso
const progressoCarregar = document.querySelector(".progresso_carregar") 
const progressoSalvar = document.querySelector(".progresso_salvar")

function iniciarProgressoCarregar (){
    const carregar = new EventSource('/start_processo_carregar')
    carregar.onmessage = function (evento){
        const progresso = evento.data

        progressoCarregar.style.width = `${progresso}%`

        if (progresso == 100) {
            carregar.close()
            form.submit()
        }
    }
}

function iniciarProgressoSalvar (){
    const salvar = new EventSource('/start_processo_salvar')
    salvar.onmessage = function(evento) {
        const progresso = evento.data

        progressoSalvar.style.width = `${progresso}%`
     
        if (progresso == 100) {
            salvar.close()
            document.querySelector('.form_salvar').submit(); // Envia o formulário quando o progresso atinge 100%

            setTimeout(() => {
                progressoSalvar.style.width = "0%";
            }, 5000) // pequeno atraso para que o usuário veja o progresso 100%
        }
    }
}

function desligarServidor() {
    const botaoDesligar = document.querySelector('.img_desligar');

    botaoDesligar.disabled = true;

    fetch('/desligar_servidor', { method: 'POST' })
        .then(() => {
            alert('Servidor desligando... Você pode fechar esta janela.');
        })
        .catch(() => {
            alert('O servidor está sendo desligado. Por favor, feche esta janela manualmente.');
        })
        .finally(() => {
            botaoDesligar.disabled = false;
            window.close()
        });
        
}