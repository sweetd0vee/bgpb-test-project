-- Task 5.
-- Latest YL clients who opened more than one contract in September 2023.
-- Show those September contracts with equivalent outstanding on 2023-09-30
-- (zeros kept). Expected: name_client, num_loan, rest_eq_deal, rest_eq_client.

with report as (
    select date '2023-09-30' as dt
),
latest_clients as (
    select
        c.id_client,
        c.name_client
    from clients as c
    where c.dt_end = date '3001-01-01'
      and c.type_client = 'ЮЛ'
),
latest_loans as (
    select
        l.id_loan,
        l.id_client,
        l.num_loan,
        l.dt_open_loan
    from loans as l
    where l.dt_end = date '3001-01-01'
      and l.dt_open_loan >= date '2023-09-01'
      and l.dt_open_loan < date '2023-10-01'
),
eligible_clients as (
    select
        c.id_client,
        c.name_client
    from latest_clients as c
    join latest_loans as l
        on l.id_client = c.id_client
    group by c.id_client, c.name_client
    having count(distinct l.id_loan) > 1
),
fact_as_of as (
    select distinct on (lf.id_loan)
        lf.id_loan,
        coalesce(lf.rest_od_eq, 0) + coalesce(lf.rest_pd_eq, 0) as rest_eq
    from loans_fact as lf
    cross join report as r
    where lf.dt <= r.dt
    order by lf.id_loan, lf.dt desc
)
select
    e.name_client,
    l.num_loan,
    coalesce(f.rest_eq, 0) as rest_eq_deal,
    sum(coalesce(f.rest_eq, 0)) over (partition by e.id_client) as rest_eq_client
from eligible_clients as e
join latest_loans as l
    on l.id_client = e.id_client
left join fact_as_of as f
    on f.id_loan = l.id_loan
order by e.name_client, l.num_loan;
