# Decisões para a T039

- A solicitação de implementação inclui a Feature 011 no escopo da T039.
- A vaga é confirmada imediatamente para o primeiro passageiro elegível. Um prazo de aceite exigiria reservar capacidade temporariamente e criar política de expiração.
- Uma entrada que já não pode resultar em reserva sai da fila durante o repasse. Assim uma conta sem vínculo ativo, suspensa ou já confirmada não bloqueia as seguintes. A indisponibilidade da própria oferta interrompe o processamento e preserva as entradas que ainda aguardam.
- O identificador crescente é alocado após bloquear a oferta, para preservar a ordem mesmo quando os relógios coincidem.
- O serviço pode ser exercitado diretamente após liberar capacidade. A integração com o cancelamento é a T040.
