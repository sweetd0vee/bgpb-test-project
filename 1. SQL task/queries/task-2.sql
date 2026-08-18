-- Task 2.
-- For each day of September 2023, count FL contracts opened that day.
-- Latest SCD versions only (dt_end = 3001-01-01).
-- Expected columns: dt_open_loan, cnt_loan.

select
    d.day_ts::date as dt_open_loan,
    count(distinct case when c.id_client is not null then l.id_loan end) as cnt_loan
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
   and c.type_client = 'ФЛ'
group by d.day_ts::date
order by dt_open_loan;
