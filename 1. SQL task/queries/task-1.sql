-- Task 1.
-- As of 2023-09-30: USD/EUR contracts with non-zero equivalent outstanding.
-- Expected columns: num_loan, risk_group, currency, rest_eq.

with report as (
    select date '2023-09-30' as dt
),
loan_as_of as (
    select
        l.id_loan,
        l.num_loan,
        l.risk_group,
        l.code_curr
    from loans as l
    cross join report as r
    where l.dt_start <= r.dt
      and l.dt_end >= r.dt
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
    l.num_loan,
    l.risk_group,
    case l.code_curr
        when '840' then 'Доллары США'
        when '978' then 'Евро'
    end as currency,
    f.rest_eq
from loan_as_of as l
join fact_as_of as f
    on f.id_loan = l.id_loan
where l.code_curr in ('840', '978')
  and f.rest_eq <> 0
order by l.num_loan;
