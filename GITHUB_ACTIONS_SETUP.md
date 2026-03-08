# Configuração do GitHub Actions para Deploy Automatizado no Azure

Este guia explica como configurar o GitHub Actions para fazer build e deploy automaticamente do seu contêiner Azure sempre que você fizer push no repositório.

## Pré-requisitos

Você já tem os seguintes recursos provisionados no Azure:
- **Resource Group**: `acs-wpp-mesh-rg`
- **Azure Container Registry**: `acswppmesh1771568067`
- **Subscription ID**: `f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec`

## Passo 1: Criar Service Principal para GitHub Actions

O GitHub Actions precisa de credenciais para acessar sua Azure Subscription. Execute os comandos abaixo no Azure CLI:

```bash
# Criar Service Principal com permissões de Contributor
az ad sp create-for-rbac \
  --name "github-actions-acs-wpp-mesh" \
  --role contributor \
  --scopes /subscriptions/f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec/resourceGroups/acs-wpp-mesh-rg \
  --sdk-auth
```

Este comando retornará um JSON. **Copie todo o JSON** - você precisará dele no próximo passo.

## Passo 2: Obter Credenciais do Azure Container Registry

Execute os comandos abaixo para obter as credenciais do ACR:

```bash
# Obter username do ACR
az acr credential show --name acswppmesh1771568067 --query "username" -o tsv

# Obter password do ACR
az acr credential show --name acswppmesh1771568067 --query "passwords[0].value" -o tsv
```

Anote o **username** e **password** retornados.

## Passo 3: Configurar Secrets no GitHub

Acesse o repositório no GitHub e vá em **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Crie os seguintes secrets:

| Nome do Secret | Valor | Descrição |
|----------------|-------|-----------|
| `AZURE_CREDENTIALS` | JSON completo do Passo 1 | Credenciais do Service Principal |
| `ACR_USERNAME` | Username do Passo 2 | Usuário do Azure Container Registry |
| `ACR_PASSWORD` | Password do Passo 2 | Senha do Azure Container Registry |
| `AZURE_SUBSCRIPTION_ID` | `f7fc86dd-bd9f-43a6-80a4-0bb6cab950ec` | ID da sua subscription Azure |
| `ACS_CONNECTION_STRING` | Sua connection string do ACS | String de conexão do Azure Communication Services |
| `WHATSAPP_BUSINESS_NUMBER` | Seu número WhatsApp Business | Número do WhatsApp configurado |

### Como adicionar cada secret:

1. Clique em **New repository secret**
2. Digite o **Name** (nome exato da tabela acima)
3. Cole o **Value** (valor correspondente)
4. Clique em **Add secret**
5. Repita para todos os secrets

## Passo 4: Ativar o Workflow

O workflow já está configurado em `.github/workflows/azure-container-deploy.yml`. Ele será executado automaticamente quando você:

- Fizer **push** na branch `main`
- Criar um **Pull Request** para a branch `main`
- Executar manualmente via **Actions** → **Build and Deploy to Azure Container Registry** → **Run workflow**

## Passo 5: Verificar Execução

Após fazer push ou executar manualmente:

1. Vá em **Actions** no repositório GitHub
2. Clique no workflow em execução
3. Acompanhe os logs de cada step
4. Ao final, o IP do contêiner será exibido nos logs

## Estrutura do Workflow

O workflow executa as seguintes etapas:

1. **Checkout code**: Clona o repositório
2. **Log in to Azure**: Autentica com as credenciais do Service Principal
3. **Log in to ACR**: Faz login no Azure Container Registry
4. **Build and push**: Faz build da imagem Docker e push para o ACR
5. **Deploy to ACI**: Cria/atualiza o Azure Container Instance
6. **Get container IP**: Exibe o IP público do contêiner

## Troubleshooting

### Erro: "AZURE_CREDENTIALS secret not found"
- Verifique se você criou o secret com o nome **exato**: `AZURE_CREDENTIALS`
- Certifique-se de que colou o JSON completo do Service Principal

### Erro: "ACR login failed"
- Verifique se os secrets `ACR_USERNAME` e `ACR_PASSWORD` estão corretos
- Execute novamente o comando do Passo 2 para obter as credenciais atualizadas

### Erro: "Resource group not found"
- Certifique-se de que o Resource Group `acs-wpp-mesh-rg` existe
- Verifique se o Service Principal tem permissões no Resource Group

### Container não inicia
- Verifique os logs do container no Azure Portal
- Certifique-se de que todas as variáveis de ambiente estão configuradas corretamente nos secrets

## Deploy Manual (Alternativa)

Se preferir fazer deploy manual sem GitHub Actions, siga o guia em `DEPLOYMENT.md`.

## Próximos Passos

Após configurar o GitHub Actions:

1. Faça uma alteração no código
2. Commit e push para a branch `main`
3. Acompanhe o deploy automático em **Actions**
4. Acesse o contêiner pelo IP exibido nos logs

O deploy automatizado garante que toda alteração no código seja automaticamente construída, testada e implantada no Azure! 🚀
