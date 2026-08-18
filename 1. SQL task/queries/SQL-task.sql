-------------- Для решения задач используется диалект PostgreSQL -------------------
-- Сдаваемый файл: схема, тестовые данные и запросы 1-7.
-- Исходники: schemas/create_tables.sql, schemas/data.sql, queries/task-N.sql
-- Условие упоминает Oracle; запросы написаны на PostgreSQL (generate_series, ilike, distinct on).

-- ======== schema ========
-- PostgreSQL schema for the SQL assignment.
-- clients and loans are SCD Type 2 (one row per version, valid on [dt_start, dt_end]).
-- An open-ended version uses the sentinel date 3001-01-01.
-- loans_fact stores end-of-day balances and can have multiple dates per contract.

drop table if exists loans_fact;
drop table if exists loans;
drop table if exists clients;

create table clients (
    id_client integer not null,
    dt_start date not null,
    dt_end date not null,
    name_client varchar(255) not null,
    type_client varchar(20) null,
    department varchar(20) null,
    primary key (id_client, dt_start),
    check (dt_start <= dt_end)
);

create table loans (
    id_loan integer not null,
    dt_start date not null,
    dt_end date not null,
    id_client integer not null,
    num_loan varchar(20) not null,
    dt_open_loan date null,
    code_curr varchar(3),
    int_rate decimal(6, 2) not null,
    risk_group varchar(20) null,
    primary key (id_loan, dt_start),
    check (dt_start <= dt_end)
);

create table loans_fact (
    id_loan integer not null,
    dt date not null,
    rest_od decimal(10, 2) null,
    rest_od_eq decimal(10, 2) null,
    rest_pd decimal(10, 2) null,
    rest_pd_eq decimal(10, 2) null,
    primary key (id_loan, dt)
);

create index idx_clients_id_client on clients (id_client);
create index idx_clients_valid_period on clients (id_client, dt_start, dt_end);
create index idx_loans_id_client on loans (id_client);
create index idx_loans_valid_period on loans (id_loan, dt_start, dt_end);
create index idx_loans_fact_dt on loans_fact (dt);

-- ======== sample data ========
-- Sample data aligned with the seven assignment queries.
-- Open-ended SCD versions use 3001-01-01. Loan examples follow the brief.

insert into clients (id_client, dt_start, dt_end, name_client, type_client, department)
values
    (101, '1980-01-01', '3001-01-01', 'Иванов Иван', 'ФЛ', '1'),
    (102, '1980-01-01', '2023-06-30', 'ООО Ромашка (старое имя)', 'ЮЛ', '2'),
    (102, '2023-07-01', '3001-01-01', 'ООО Ромашка', 'ЮЛ', '2'),
    (103, '1980-01-01', '3001-01-01', 'ООО Василек', 'ЮЛ', '3'),
    (104, '1980-01-01', '3001-01-01', 'client name 4', 'ЮЛ', '3'),
    (105, '1980-01-01', '3001-01-01', 'client name 5', 'ЮЛ', '3'),
    (106, '1980-01-01', '3001-01-01', 'client name 6', 'ЮЛ', '4'),
    (107, '1980-01-01', '3001-01-01', 'Петров Петр', 'ФЛ', '1'),
    (108, '1980-01-01', '3001-01-01', 'Сидоров Сидор', 'ФЛ', '1');

insert into loans (
    id_loan, dt_start, dt_end, id_client, num_loan, dt_open_loan, code_curr, int_rate, risk_group
)
values
    (1, '1980-01-01', '3001-01-01', 101, 'DEAL_A', '2023-05-01', '933', 10.00, '1'),
    (2, '1980-01-01', '2023-09-30', 102, 'DEAL_B', '2023-04-11', '840', 5.50, '1'),
    (2, '2023-10-01', '3001-01-01', 102, 'DEAL_B', '2023-04-11', '840', 5.50, '2'),
    (3, '1980-01-01', '2022-12-31', 102, 'DEAL_C', '2022-09-15', '978', 4.75, '1'),
    (3, '2023-01-01', '2023-02-15', 102, 'DEAL_C', '2022-09-15', '978', 4.75, '2'),
    (3, '2023-02-16', '3001-01-01', 102, 'DEAL_C', '2022-09-15', '978', 5.00, '3'),
    (4, '2023-09-11', '3001-01-01', 102, 'DEAL_D', '2023-09-11', '978', 5.00, '3'),
    (5, '2023-09-12', '3001-01-01', 102, 'DEAL_E', '2023-09-12', '978', 5.00, '3'),
    (6, '2022-03-01', '3001-01-01', 103, 'DEAL_F', '2022-03-01', '978', 6.00, '1'),
    (7, '2022-08-01', '3001-01-01', 103, 'DEAL_G', '2022-08-01', '840', 7.00, '1'),
    (8, '2022-11-01', '3001-01-01', 102, 'DEAL_H', '2022-11-01', '933', 8.00, '2'),
    (9, '2023-09-05', '3001-01-01', 107, 'DEAL_I', '2023-09-05', '933', 9.00, '1'),
    (10, '2022-06-01', '3001-01-01', 103, 'DEAL_J', '2022-06-01', '933', 11.50, '1');

insert into loans_fact (id_loan, dt, rest_od, rest_od_eq, rest_pd, rest_pd_eq)
values
    (3, '2022-12-31', 200.00, 600.00, 0.00, 0.00),
    (8, '2022-12-31', 40.00, 40.00, null, null),
    (10, '2022-12-31', 80.00, 80.00, null, null),
    (1, '2023-09-30', 10.00, 10.00, 3.00, 3.00),
    (2, '2023-09-30', 100.00, 300.00, 3.00, 9.00),
    (3, '2023-09-30', 90.00, 270.00, 5.00, 15.00),
    (4, '2023-09-30', 10.00, 30.00, 3.00, 9.00),
    (5, '2023-09-30', 9.00, 27.00, 5.00, 15.00),
    (6, '2023-09-30', 40.00, 120.00, null, null),
    (7, '2023-09-30', 70.00, 210.00, null, null),
    (8, '2023-09-30', 30.00, 30.00, null, null),
    (9, '2023-09-30', 15.00, 15.00, null, null),
    (10, '2023-09-30', 50.00, 50.00, null, null);

-- ======== task 1 ========
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


-- ======== task 2 ========
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


-- ======== task 3 ========
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


-- ======== task 4 ========
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


-- ======== task 5 ========
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


-- ======== task 6 ========
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


-- ======== task 7 ========
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

