{{ config(materialized='table', engine='MergeTree()', order_by='date_id') }}
with calendar as (
    select toDate('2024-01-01') + number as date_jour
    from numbers(731)
)
select toUInt32(toYYYYMMDD(date_jour)) as date_id,
       date_jour as date, toDayOfMonth(date_jour) as jour,
       toWeek(date_jour) as semaine, toMonth(date_jour) as mois,
       toQuarter(date_jour) as trimestre, toYear(date_jour) as annee
from calendar
