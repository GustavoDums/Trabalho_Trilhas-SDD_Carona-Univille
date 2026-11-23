# Dados da espera

| Campo canônico | Regra |
| --- | --- |
| WaitlistEntry.id | Identificador crescente que desempata e determina a ordem de ingresso para a oferta |
| WaitlistEntry.offer | FK protegida, obrigatória; a oferta é a unidade de concorrência |
| WaitlistEntry.passenger | FK protegida, obrigatória; única por oferta |
| WaitlistEntry.boarding_point | FK protegida, obrigatória; pertence à oferta |
| WaitlistEntry.alighting_point | FK protegida, obrigatória e distinta do embarque; ocorre depois no itinerário |

Cada linha representa uma entrada pendente. A confirmação ou a perda de elegibilidade remove a linha. O índice de oferta e ID atende à consulta FIFO.
