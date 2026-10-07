{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if target.schema is none -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
