-- Task 4.
-- Latest YL clients whose name starts with "ООО" (case-insensitive)
-- and who opened more than one contract in 2022.

select
    c.name_client
from clients as c
join loans as l
    on l.id_client = c.id_client
   and l.dt_end = date '3001-01-01'
where c.dt_end = date '3001-01-01'
  and c.type_client = 'ЮЛ'
  and c.name_client ilike 'ООО%'
  and l.dt_open_loan >= date '2022-01-01'
  and l.dt_open_loan < date '2023-01-01'
group by c.id_client, c.name_client
having count(distinct l.id_loan) > 1
order by c.name_client;
