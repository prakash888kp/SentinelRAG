# Azure runbook — SentinelRAG Phase 0

## Status (2026-11-08)

**Computer-use bootstrap partially blocked.** Edge was logged into the Azure portal with credits (~₹19,045.75, expires ~2026-12-07). The Create VM wizard opened (`#create/Microsoft.VirtualMachine`) with:

- Image: **Ubuntu Server 24.04 LTS - x64 Gen2** (good)
- Region default: **East US**
- Size default: **Standard_D2s_v3** → error: *unavailable in eastus for this subscription*
- SPA controls (`Create new` RG, `See all sizes`, `Continue` / `Skip`) did not reliably accept injected clicks after repeated attempts

**No VM was provisioned by the agent.** Finish creation manually in the open Edge tab (or Azure CLI after install), then run `vm-bootstrap.sh`.

## Manual finish (human, ~10 min)

1. In the open **Create a virtual machine** blade:
   - **Resource group** → Create new → `rg-sentinelrag`
   - **VM name** → `vm-sentinelrag`
   - **Region** → prefer **Central India** or **South India** (retry East US only if those lack B-series)
   - **Image** → Ubuntu Server 24.04 LTS (already selected)
   - **Size** → **See all sizes** → filter **B-series** → `Standard_B2s` (2 vCPU / 8 GiB) or `Standard_B2ats_v2` if cheaper/available
   - **Authentication** → SSH public key; username `azureuser`
   - Generate a new key pair in portal **or** use an existing key; save private key to  
     `C:\Users\praka\.ssh\sentinelrag_azure` (outside git)
   - OS disk: **Standard SSD**, small
   - Networking: allow **SSH (22)** inbound
2. **Review + create** → Create. Wait until VM status is **Running**.
3. Note **public IP** and update `docs/CHAT_MEMORY.md`.
4. From PowerShell on Windows:

```powershell
ssh -i $env:USERPROFILE\.ssh\sentinelrag_azure azureuser@<PUBLIC_IP>
```

5. On the VM (or paste via SSH):

```bash
curl -fsSL https://raw.githubusercontent.com/...   # or scp local script
# Prefer: scp from Windows then:
bash docs/azure/vm-bootstrap.sh
```

From the Windows mirror after cloning/syncing the repo:

```powershell
scp -i $env:USERPROFILE\.ssh\sentinelrag_azure `
  "D:\AI Engg\SentinelRAG\docs\azure\vm-bootstrap.sh" `
  azureuser@<PUBLIC_IP>:~/
ssh -i $env:USERPROFILE\.ssh\sentinelrag_azure azureuser@<PUBLIC_IP> "bash ~/vm-bootstrap.sh"
```

6. Sync code and start Compose (from Windows):

```powershell
scp -i $env:USERPROFILE\.ssh\sentinelrag_azure -r "D:\AI Engg\SentinelRAG\*" azureuser@<PUBLIC_IP>:~/sentinelrag/
ssh -i $env:USERPROFILE\.ssh\sentinelrag_azure azureuser@<PUBLIC_IP> "cd ~/sentinelrag && docker compose up -d"
```

## Cost control (critical)

| Action | Effect |
|--------|--------|
| Stop VM | Still bills for disks (and sometimes static IP) |
| **Deallocate** (portal: Stop → deallocate, or `az vm deallocate`) | Stops compute billing; disk still bills |
| Delete RG `rg-sentinelrag` | Tears down all Phase 0 Azure resources |

**Habit:** deallocate whenever you are not actively developing.

## Optional: Azure CLI later

```powershell
winget install -e --id Microsoft.AzureCLI
az login
az group create -n rg-sentinelrag -l centralindia
# then az vm create ... with --size Standard_B2s --image Canonical:ubuntu-24_04-lts:server:latest
```

## Blockers logged

1. No `az` CLI on PATH during Phase 0 agent session.
2. Computer-use could not reliably activate Azure portal primary actions (size picker / continue).
3. Student/credit SKU availability: D2s_v3 unavailable in East US — expect region/SKU hunting for B2s.
