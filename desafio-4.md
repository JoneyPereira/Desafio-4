
# Automação da compra de VR/VA
## Objetivo
Automatizar o processo mensal de compra de VR (Vale Refeição), garantindo que cada colaborador receba o valor correto, considerando ausências, férias e datas de admissão ou desligamento e calendário de feriados.

## Descrição do problema
Hoje, o cálculo da quantidade de dias para compra de benefícios é feito manualmente a partir de planilhas. Esse processo envolve:
 - Conferência de datas de início e fim do contrato no mês.
 - Exclusão de colaboradores em férias (parcial ou integral por regra de sindicato).
 - Ajustes para datas quebradas (ex.: admissões no meio do mês e desligamentos).
 - Cálculo do número exato de dias a serem comprados para cada pessoa.
 - Geração de um layout de compra a ser enviado para o fornecedor.
 - Considerar as regras vigentes decorrentes dos acordos coletivos de cada um dos sindicatos.
O que o(s) agente(s) deve(m) entregar como resultado – cálculo feito com base dia útil de cada sindicato e considerando a nossa folha ponto.
 - Base única consolidada: Reunir e consolidar informações de 5 bases separadas em uma única base final para (Ativos, Férias, desligados, Base cadastral (admitidos do mês), Base sindicato x valor e Dias úteis por colaborador.
 - Tratamento de exclusões: Remover da base final, todos os profissionais com cargo de diretores, estagiários e aprendizes, afastados em geral (ex.: licença maternidade), profissionais que atuam no exterior. Para isto, se guiar pela matrícula nas planilhas.
 - Validar e corrigir: datas inconsistentes ou "quebradas", campos faltantes, férias mal preenchidas, feriados estaduais e municipais corretamente aplicados

## Cálculo automatizado do benefício:

### Com base na planilha calcular automaticamente:
 - Quantidade de dias úteis por colaborador (considerando os dias úteis de cada sindicato, férias, afastamentos e data de desligamento)
 - Regra de desligamento: Para desligamento se estiver como OK o comunicado de desligamento até dia 15, não considerar para pagamento. Se for informado depois do dia 15, a compra deve ser proporcional. Verificar se pela matricula se é elegível ao benefício (vide base de tratamento de exclusões)
 - Valor total de Vale Refeição (VR) a ser concedido para cada colaborador, de acordo com o valor de cada sindicato que o profissional está vinculado, gerando o cálculo, correto e vigente.

## Entrega final:
Geração de uma planilha final para envio à operadora, contendo o valor de VR a ser concedido e valor a ser pago pela empresa e profissional, de acordo com Modelo da planilha aba “VR Mensal 05.2025”. Considerar custo para empresa 80% do valor pago e 20% a ser descontado do profissional.
 - Observar as validações constantes na aba “validações” da planilha “VR MENSAL 05.2025 vfinal.xlsx”.