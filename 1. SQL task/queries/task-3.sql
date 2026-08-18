-- Task 3.
-- For each day of September 2023, count YL contracts opened that day
-- split by currency. Latest SCD versions only (dt_end = 3001-01-01).
-- Expected columns: dt_open_loan, cnt_BYN, cnt_USD, cnt_EUR.

select
    d.day_ts::date as dt_open_loan,
    count(distinct case when c.id_client is not null and l.code_curr = '933' then l.id_loan end) as "cnt_BYN",
    count(distinct case when c.id_client is not null and l.code_curr = '840' then l.id_loan end) as "cnt_USD",
    count(distinct case when c.id_client is not null and l.code_curr = '978' then l.id_loan end) as "cnt_EUR"
from generate_series(
        date '2023-09-01',
        date '2023-09-30',
        interval '1 day'
    ) as d(day_ts)
left join loans as l
    on l.dt_open_loan = d.day_ts::date
   and l.dt_end = date '3001-01-01'
left join clients as c
    on c.id_client = l.id_client
   and c.dt_end = date '3001-01-01'
   and c.type_client = 'ЮЛ'
group by d.day_ts::date
order by dt_open_loan;
