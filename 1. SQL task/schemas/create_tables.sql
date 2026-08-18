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
