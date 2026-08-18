-- Task 6.
-- Weighted average BYN (933) principal rate for latest YL clients as of 2022-12-31.
-- avg_rate is absolute value, rounded to 2 decimals. Skip zero/NULL principal.

with report as (
    select date '2022-12-31' as dt
),
latest_clients as (
    select c.id_client
    from clients as c
    where c.dt_end = date '3001-01-01'
      and c.type_client = 'ЮЛ'
),
loan_as_of as (
    select
        l.id_loan,
        l.id_client,
        l.int_rate
    from loans as l
    cross join report as r
    where l.dt_start <= r.dt
      and l.dt_end >= r.dt
      and l.code_curr = '933'
),
fact_as_of as (
    select
        lf.id_loan,
        lf.rest_od_eq
    from loans_fact as lf
    cross join report as r
    where lf.dt = r.dt
      and coalesce(lf.rest_od_eq, 0) > 0
)
select
    c.id_client,
    round(
        abs(sum(l.int_rate * f.rest_od_eq) / sum(f.rest_od_eq)),
        2
    ) as avg_rate,
    sum(f.rest_od_eq) as rest_od_eq
from latest_clients as c
join loan_as_of as l
    on l.id_client = c.id_client
join fact_as_of as f
    on f.id_loan = l.id_loan
group by c.id_client
order by avg_rate;
