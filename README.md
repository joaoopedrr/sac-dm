# sac-dm
Repositório para dados e códigos referentes a análise de sinais através da abordagem sac-dm

#Para instalar as dependências, a partir da raiz do projeto, execute os comandos abaixo:

`pip install -r src/sac-dm/requirements.txt`
`pip install -r src/server/requirements.txt`


## Dispositivo padrão

O projeto utiliza-se de duas controladoras, uma ESP-32 para coletar e calcular os dados e uma Raspberry PI para transformação e requisição dos dados obtidos.


## Primeiro passo

### Baixe o Arduino IDE

Inicialmente, devemos acessar o site arduino.cc, home page da Arduino. Vá até o menu software e clique em downloads.
![image](https://github.com/user-attachments/assets/6e7eaa93-d62e-41f4-b61b-36b7cc1f2390)


Em seguida, encontramos o menu de escolha para download da IDE. Oferecida para diversos sistemas operacionais (Windows, Mac OS X e Linux), versões de 32 bits e 64 bits, além de também ser possível fazer o download em formatos diferentes, como um zip do software ou um instalador executável. Faça o download do ZIP ou da sua versão via SO
![image](https://github.com/user-attachments/assets/b8f18c00-ff2d-4db7-a2ea-25e085164e8a)

Depois será direcionado para página de download que tem uma opção de contribuição, caso queira.
Aperte para download
![image](https://github.com/user-attachments/assets/a348861e-2fd4-44e3-80fc-3430a6eeda08)

Em seguida, o download do arquivo irá começar.



Após ser baixada, acesse a pasta de Downloads do seu navegador e abra o arquivo do arduino. A seguinte tela de instalação irá aparecer:
![image](https://github.com/user-attachments/assets/68ab0c79-9db1-440d-bedf-fad26966a792)

Nela, clique em ‘I Agree’, para aceitar os termos. Na sequência, aparacerão os componentes a serem instalados, conforme figura abaixo. Clique em ‘Next’ para prosseguir.
![image](https://github.com/user-attachments/assets/4d89be5e-6913-4a25-91c1-b9da192c9c96)


O local padrão de instalação é em “C:\Program Files (x86)\Arduino”. Normalmente também é criado uma pasta em “C:\Users\<username>\Documents\Arduino”. Mas caso ela não tenha sido criada, você mesmo pode criar uma e nomeá-la como Arduino. Nela são armazenados as libraries (bibliotecas de funções) e outros arquivos de configuração adicionais. Clique em ‘Install’ para prosseguir.
![image](https://github.com/user-attachments/assets/f97d6d18-3d12-4ecd-bdc5-279fb778bd01)

O processo de instalação irá, então, iniciar. Aguarde o seu término.

Quando for finalizado, aparecerá a opção ‘Close’ para encerrar. Clique nela e o Arduino estará pronto para ser usado! Ele poderá ser acessado pela área de trabalho ou pelo menu iniciar.
![image](https://github.com/user-attachments/assets/33a0e06f-989e-4147-bbb6-f7ca8ca4f462)



Inicialmente aparecerá essa tela:
![image](https://github.com/user-attachments/assets/895380fd-1078-4443-bbd7-2edb43176c50)


### Baixe a placa da ESP-32: 
Para usar e programar ESP32 na IDE do Arduino, precisamos primeiro que ele reconheça os modelos da placa. Para isso, primeiramente devemos ir até as Preferências e colar a URL abaixo no campo de URLs adicionais:

    https://dl.espressif.com/dl/package_esp32_index.json
    
![image](https://github.com/user-attachments/assets/aa4ce7b8-111b-4458-96b1-a00340615cd8)


Com isso, permitimos que a IDE acesse uma pequena “base de dados” no formato .json que contém a configuração de inúmeras placas. Após isso, devemos acessar o menu Ferramentas -> Placa -> Gerenciador de Placas.
![image](https://github.com/user-attachments/assets/fa34752e-b82c-439e-8d4a-db89e236eb24)


Nele, pesquise por ‘esp32′ na caixa de pesquisa. Em seguida, instale a versão mais recente do driver que irá aparecer: “esp32 by Espressif Systems’, conforme ilustrado na figura a seguir:
![image](https://github.com/user-attachments/assets/b1ca1cd5-d284-410e-ae8e-09b5b6c4d383)


Feito isso, você deve selecionar a placa “ESP32 Dev Module”, no menu de placas, para programar na ESP.
![image](https://github.com/user-attachments/assets/8c88b1bd-05ce-4516-a3d2-808d1629d4ee)

Instalação e configuração finalizada.


