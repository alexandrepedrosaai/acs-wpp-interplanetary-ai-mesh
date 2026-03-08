# Implantação no Azure: ACS-WPP Interplanetary AI Mesh

Este documento fornece um guia passo a passo para implantar o projeto `acs-wpp-interplanetary-ai-mesh` no Microsoft Azure usando Docker, Azure Container Registry (ACR) e Azure Container Instances (ACI). A implantação é automatizada através de um template ARM.

## Pré-requisitos

Antes de começar, certifique-se de que você possui as seguintes ferramentas e contas:

- **Azure CLI**: [Instruções de instalação](https://docs.microsoft.com/cli/azure/install-azure-cli)
- **Docker**: [Instruções de instalação](https://docs.docker.com/get-docker/)
- **Git**: [Instruções de instalação](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **Conta no Azure**: Uma assinatura ativa do Azure. A que você forneceu (`f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec`) será usada como padrão.

## 1. Configuração do Ambiente Local

Primeiro, clone o repositório e configure as variáveis de ambiente necessárias.

```bash
# Clone o repositório
git clone https://github.com/alexandrepedrosaai/acs-wpp-interplanetary-ai-mesh.git
cd acs-wpp-interplanetary-ai-mesh

# Crie um arquivo .env a partir do exemplo
cp .env.example .env
```

Agora, edite o arquivo `.env` e preencha os valores apropriados para sua conta do Azure e serviços de comunicação. As variáveis incluem credenciais do Azure, connection strings do ACS e configurações do WhatsApp.

## 2. Provisionamento de Recursos no Azure

Faça login na sua conta do Azure e crie um grupo de recursos onde todos os serviços serão implantados.

```bash
# Faça login no Azure
az login

# Defina a assinatura a ser usada (opcional, se você tiver várias)
az account set --subscription "f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec"

# Crie um grupo de recursos (substitua <location> por uma região do Azure, ex: eastus)
RESOURCE_GROUP="acs-wpp-mesh-rg"
LOCATION="<location>"
az group create --name $RESOURCE_GROUP --location $LOCATION
```

## 3. Build e Push da Imagem Docker

O próximo passo é construir a imagem Docker, criar um Azure Container Registry (ACR) para armazená-la e fazer o push da imagem para o registro.

```bash
# Crie um Azure Container Registry (ACR)
ACR_NAME="acswppmeshregistry$RANDOM"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Faça login no ACR
az acr login --name $ACR_NAME

# Construa a imagem Docker
IMAGE_NAME="acs-wpp-mesh"
IMAGE_TAG="latest"
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Marque a imagem para o ACR
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Faça o push da imagem para o ACR
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG
```

## 4. Implantação com Template ARM

Com a imagem no ACR, use o template ARM (`azure-deploy.json`) para implantar a Azure Container Instance (ACI).

```bash
# Implante o container usando o template ARM
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file azure-deploy.json \
    --parameters acrName=$ACR_NAME \
                 imageName=$IMAGE_NAME \
                 imageTag=$IMAGE_TAG
```

O template irá provisionar a ACI, configurando as portas e as credenciais para acessar a imagem no ACR de forma segura.

## 5. Verificação e Gerenciamento

Após a conclusão da implantação, você pode verificar o status e obter o endereço IP público do seu contêiner.

```bash
# Obtenha o endereço IP público da instância do contêiner
CONTAINER_NAME="acs-wpp-interplanetary-mesh"
az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" --output tsv

# Visualize os logs do contêiner
az container logs --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME
```

Para parar e remover todos os recursos criados, basta excluir o grupo de recursos:

```bash
# ATENÇÃO: Este comando excluirá todos os recursos criados
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

Com isso, sua aplicação estará em execução no Azure, pronta para mediar a comunicação interplanetária!
