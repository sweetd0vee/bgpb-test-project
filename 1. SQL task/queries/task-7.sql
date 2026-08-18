-- Task 7.
-- Count of clients who have no credit contract at all, by department.
-- Client attributes come from the latest SCD version (dt_end = 3001-01-01).

select
    c.department,
    count(*) as cnt_clients_without_loans
from clients as c
where c.dt_end = date '3001-01-01'
  and not exists (
      select 1
      from loans as l
      where l.id_client = c.id_client
  )
group by c.department
order by c.department;
