# Guia de Deploy Manual no Azure

Este guia detalha como fazer o deploy manual do projeto `acs-wpp-interplanetary-ai-mesh` no Azure. Use este método se você não quiser usar o GitHub Actions ou se precisar de mais controle sobre o processo.

## Pré-requisitos

- **Azure CLI**: [Instalação](https://docs.microsoft.com/cli/azure/install-azure-cli)
- **Docker**: [Instalação](https://docs.docker.com/get-docker/)
- **Git**: [Instalação](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **Conta no Azure**: Subscription `f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec`

## Passo 1: Configuração do Ambiente

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/alexandrepedrosaai/acs-wpp-interplanetary-ai-mesh.git
   cd acs-wpp-interplanetary-ai-mesh
   ```

2. **Crie e configure o arquivo `.env`**:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` e preencha com suas credenciais do Azure, ACS e WhatsApp.

3. **Faça login no Azure**:
   ```bash
   az login
   az account set --subscription "f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec"
   ```

## Passo 2: Provisionamento de Recursos

Os seguintes recursos já foram criados e podem ser reutilizados:

- **Resource Group**: `acs-wpp-mesh-rg`
- **Azure Container Registry**: `acswppmesh1771568067`

Se precisar recriá-los, use os comandos:

```bash
# Criar Resource Group
az group create --name acs-wpp-mesh-rg --location eastus

# Criar Azure Container Registry
az acr create --resource-group acs-wpp-mesh-rg --name acswppmesh1771568067 --sku Basic --admin-enabled true
```

## Passo 3: Build e Push da Imagem Docker

1. **Faça login no Azure Container Registry**:
   ```bash
   az acr login --name acswppmesh1771568067
   ```

2. **Construa a imagem Docker**:
   ```bash
   docker build -t acs-wpp-mesh:latest .
   ```

3. **Marque a imagem para o ACR**:
   ```bash
   docker tag acs-wpp-mesh:latest acswppmesh1771568067.azurecr.io/acs-wpp-mesh:latest
   ```

4. **Faça o push da imagem para o ACR**:
   ```bash
   docker push acswppmesh1771568067.azurecr.io/acs-wpp-mesh:latest
   ```

## Passo 4: Deploy no Azure Container Instances (ACI)

1. **Obtenha as credenciais do ACR**:
   ```bash
   ACR_USERNAME=$(az acr credential show --name acswppmesh1771568067 --query "username" -o tsv)
   ACR_PASSWORD=$(az acr credential show --name acswppmesh1771568067 --query "passwords[0].value" -o tsv)
   ```

2. **Crie o container no ACI**:
   ```bash
   az container create \
     --resource-group acs-wpp-mesh-rg \
     --name acs-wpp-mesh-container \
     --image acswppmesh1771568067.azurecr.io/acs-wpp-mesh:latest \
     --registry-login-server acswppmesh1771568067.azurecr.io \
     --registry-username $ACR_USERNAME \
     --registry-password $ACR_PASSWORD \
     --dns-name-label acs-wpp-mesh-$(date +%s) \
     --ports 80 443 8080 3000 \
     --cpu 1 \
     --memory 2 \
     --environment-variables \
       AZURE_SUBSCRIPTION_ID=f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec \
       ACS_CONNECTION_STRING="<sua-acs-connection-string>" \
       WHATSAPP_BUSINESS_NUMBER="<seu-whatsapp-number>" \
     --restart-policy OnFailure
   ```
   **Importante**: Substitua `<sua-acs-connection-string>` e `<seu-whatsapp-number>` pelos valores reais.

## Passo 5: Verificação

1. **Obtenha o IP público do container**:
   ```bash
   az container show \
     --resource-group acs-wpp-mesh-rg \
     --name acs-wpp-mesh-container \
     --query "ipAddress.ip" \
     --output tsv
   ```

2. **Visualize os logs**:
   ```bash
   az container logs --resource-group acs-wpp-mesh-rg --name acs-wpp-mesh-container
   ```

## Passo 6: Limpeza de Recursos

Para excluir todos os recursos criados, delete o Resource Group:

```bash
# ATENÇÃO: Este comando excluirá todos os recursos
az group delete --name acs-wpp-mesh-rg --yes --no-wait
```

Este guia fornece uma alternativa robusta para deploy manual, garantindo que você tenha controle total sobre cada etapa do processo.
