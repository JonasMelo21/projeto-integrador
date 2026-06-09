#!/bin/bash

# Mantenha o nome da equipe que você encontrou no passo anterior
TEAM_NAME="Projeto Integrador III 2.0 Team" 

echo "Buscando informações da sprint atual no Azure DevOps..."

CURRENT_SPRINT_JSON=$(az boards iteration team list --team "$TEAM_NAME" --timeframe current --output json)

SPRINT_NAME=$(echo $CURRENT_SPRINT_JSON | jq -r '.[0].name')
SPRINT_PATH=$(echo $CURRENT_SPRINT_JSON | jq -r '.[0].path')

if [ "$SPRINT_NAME" == "null" ] || [ -z "$SPRINT_NAME" ]; then
    echo "Nenhuma sprint ativa encontrada para a data de hoje."
    exit 1
fi

# O WIQL exige que caminhos com contrabarras (\) sejam escapados (\\)
FORMATTED_PATH=$(echo "$SPRINT_PATH" | sed 's/\\/\\\\/g')

# Monta a query WIQL para buscar apenas os PBIs dessa sprint
WIQL_QUERY="SELECT [System.Id], [System.Title] FROM workitems WHERE [System.WorkItemType] = 'Product Backlog Item' AND [System.IterationPath] = '$FORMATTED_PATH'"

# Roda a query e armazena em JSON
PBIS_JSON=$(az boards query --wiql "$WIQL_QUERY" --output json)
QTD_PBIS=$(echo "$PBIS_JSON" | jq 'length')

if [ "$QTD_PBIS" -eq 0 ]; then
    echo "A sprint $SPRINT_NAME não tem nenhum PBI associado a ela."
    exit 1
fi

# Limpa a tela para uma exibição melhor
clear
echo "=============================================================="
echo " 🏃 SPRINT ATUAL: $SPRINT_NAME"
echo "=============================================================="
echo "PBIs identificados nesta sprint:"
echo ""

# Itera sobre os PBIs lendo o JSON linha por linha
echo "$PBIS_JSON" | jq -c '.[]' | while read -r pbi; do
    PBI_ID=$(echo "$pbi" | jq -r '.id')
    PBI_TITLE=$(echo "$pbi" | jq -r '.fields."System.Title"')
    echo "  📦 [$PBI_ID] - $PBI_TITLE"
done

echo "=============================================================="
echo ""
read -p "A sprint atual é esta mesmo? Deseja listar as tarefas? (s/n): " CONFIRMA

if [[ "$CONFIRMA" != "s" && "$CONFIRMA" != "S" ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "Buscando tarefas filhas e horas restantes..."
echo "=============================================================="

# Variável para armazenar as tasks temporariamente para a fase de atualização
TASKS_TO_UPDATE=""

# Itera pelos PBIs para buscar e listar as tasks
echo "$PBIS_JSON" | jq -c '.[]' | while read -r pbi; do
    PBI_ID=$(echo "$pbi" | jq -r '.id')
    PBI_TITLE=$(echo "$pbi" | jq -r '.fields."System.Title"')
    
    echo "📦 PBI: [$PBI_ID] $PBI_TITLE"
    
    # Adicionamos [System.ChangedDate] na query
    TASKS_WIQL="SELECT [System.Id], [System.Title], [System.State], [Microsoft.VSTS.Scheduling.RemainingWork], [System.ChangedDate] FROM workitems WHERE [System.WorkItemType] = 'Task' AND [System.Parent] = $PBI_ID"
    
    TASKS_JSON=$(az boards query --wiql "$TASKS_WIQL" --output json 2>/dev/null)
    QTD_TASKS=$(echo "$TASKS_JSON" | jq 'length')
    
    if [ "$QTD_TASKS" -eq 0 ]; then
        echo "   └── Nenhuma tarefa encontrada para este PBI."
    else
        echo "$TASKS_JSON" | jq -c '.[]' | while read -r task; do
            TASK_ID=$(echo "$task" | jq -r '.id')
            TASK_TITLE=$(echo "$task" | jq -r '.fields."System.Title"')
            TASK_STATE=$(echo "$task" | jq -r '.fields."System.State"')
            TASK_HOURS=$(echo "$task" | jq -r '.fields."Microsoft.VSTS.Scheduling.RemainingWork"')
            TASK_CHANGED=$(echo "$task" | jq -r '.fields."System.ChangedDate"')
            
            # Tratamento de nulos e formatação de data
            if [ "$TASK_HOURS" == "null" ]; then TASK_HOURS="0"; fi
            if [ "$TASK_CHANGED" != "null" ]; then
                # Converte a data ISO do Azure para o formato DD/MM/YYYY HH:MM
                TASK_CHANGED_FMT=$(date -d "$TASK_CHANGED" "+%d/%m/%Y %H:%M")
            else
                TASK_CHANGED_FMT="N/A"
            fi
            
            echo "   └── 🛠️  Task [$TASK_ID]: $TASK_TITLE | Status: $TASK_STATE | Remaining: $TASK_HOURS h | Última mod: $TASK_CHANGED_FMT"
        done
    fi
    echo "--------------------------------------------------------------"
done

# ==============================================================
# FASE 2: ATUALIZAÇÃO INTERATIVA DAS HORAS
# ==============================================================

echo ""
# Lemos diretamente do teclado (tty) para não conflitar com loops
read -p "Deseja atualizar as horas das tarefas listadas? (s/n): " ATUALIZAR </dev/tty

if [[ "$ATUALIZAR" == "s" || "$ATUALIZAR" == "S" ]]; then
    echo ""
    echo "=============================================================="
    echo "⚙️  ATUALIZAÇÃO DE HORAS"
    echo "=============================================================="

    # Extraímos os IDs dos PBIs para uma lista (evita o bug de engolir a entrada)
    PBI_IDS=$(echo "$PBIS_JSON" | jq -r '.[].id')

    for PBI_ID in $PBI_IDS; do
        TASKS_WIQL="SELECT [System.Id], [System.Title], [System.State], [Microsoft.VSTS.Scheduling.RemainingWork] FROM workitems WHERE [System.WorkItemType] = 'Task' AND [System.Parent] = $PBI_ID"
        TASKS_JSON=$(az boards query --wiql "$TASKS_WIQL" --output json 2>/dev/null)

        # Extraímos os IDs das Tasks para iterar de forma segura
        TASK_IDS=$(echo "$TASKS_JSON" | jq -r '.[].id')

        # Se não houver tasks, o loop não executa e vai pro próximo PBI
        for TASK_ID in $TASK_IDS; do
            # Extraindo os dados específicos da task atual
            TASK_TITLE=$(echo "$TASKS_JSON" | jq -r ".[] | select(.id==$TASK_ID) | .fields.\"System.Title\"")
            TASK_STATE=$(echo "$TASKS_JSON" | jq -r ".[] | select(.id==$TASK_ID) | .fields.\"System.State\"")
            TASK_HOURS=$(echo "$TASKS_JSON" | jq -r ".[] | select(.id==$TASK_ID) | .fields.\"Microsoft.VSTS.Scheduling.RemainingWork\"")

            if [ "$TASK_HOURS" == "null" ]; then TASK_HOURS="0"; fi

            # Ignora tarefas que já estão prontas (Done)
            if [ "$TASK_STATE" == "Done" ]; then
                continue
            fi

            echo "Tarefa: [$TASK_ID] $TASK_TITLE (Horas atuais: $TASK_HOURS)"
            
            # Pedimos o ajuste (- para diminuir, número positivo para aumentar, Enter pula)
            read -p "  👉 Ajuste (ex: -1 diminui, 1 aumenta, Enter pula): " AJUSTE </dev/tty

            # Se apertar Enter vazio, pula a tarefa sem fazer requisição na nuvem
            if [ -z "$AJUSTE" ]; then
                echo "  ⏭️  Pulando a tarefa $TASK_ID..."
                echo ""
                continue
            fi

            # Verifica se o que foi digitado é um número válido usando Regex
            if ! [[ "$AJUSTE" =~ ^[-+]?[0-9]*\.?[0-9]+$ ]]; then
                echo "  ⚠️  Valor inválido inserido. Pulando a tarefa..."
                echo ""
                continue
            fi

            # Calcula a nova hora somando o ajuste (se for -1, a matemática subtrai automaticamente)
            NOVA_HORA=$(awk "BEGIN {print $TASK_HOURS + ($AJUSTE)}")
            
            # Avalia se a nova hora zerou (ou ficou negativa por engano)
            if awk "BEGIN {exit !($NOVA_HORA <= 0)}"; then
                NOVA_HORA=0
                NOVO_ESTADO="Done"
                echo "  ✅ A tarefa zerou e será movida para 'Done'."
            else
                NOVO_ESTADO="In Progress"
                echo "  ⏳ Atualizando para $NOVA_HORA horas ('In Progress')."
            fi

            # Executa a atualização na nuvem
            az boards work-item update --id "$TASK_ID" \
                --fields "Microsoft.VSTS.Scheduling.RemainingWork=$NOVA_HORA" "System.State=$NOVO_ESTADO" > /dev/null
            
            echo "  ✔️  Tarefa $TASK_ID atualizada com sucesso!"
            echo ""
        done
    done
    echo "=============================================================="
    echo "🎉 Todas as atualizações foram concluídas!"
fi