# tap-bling-erp

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

This tap:

- Pulls raw data from [Bling ERP's API](https://ajuda.bling.com.br/hc/pt-br/categories/360002186394-API-para-Desenvolvedores)
- Extracts the following resources:
  - [Orders](https://ajuda.bling.com.br/hc/pt-br/articles/360046424094-GET-pedidos)
  - [Invoices](https://ajuda.bling.com.br/hc/pt-br/articles/360046379394-GET-notasfiscais)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state 
- Do a full replication based on a start_date

## Context
Bling is an ERP system used by small and medium companies in Brazil.

## Configuration

This tap requires a config.json which specifies details about API URL, API Token and Start Date. An example of the config.json is as below:
```
{
  'api_url': 'https://bling.com.br/Api',
  'api_token': '<72 char hexcode>',
  'start_date': '2020-12-01T00:00:00.000000Z'
}
```

## Streams

[**orders**](https://ajuda.bling.com.br/hc/pt-br/articles/360046424094-GET-pedidos)
- Endpoint: https://bling.com.br/Api/v2/pedidos/page=[page number]/json
- Primary Key: id
- Replication strategy:
    - Incremental, filtering by start and end date
    - Do a request for each page until empty page is found
- Transformation:
    - **IMPORTANT NOTE**: As the API returns dates as strings at America/Sao_Paulo timezone without timezone information, and Singer.io has it's own way of handling date strings, the code will append the UTC 0 tz info without changing the date string. So all dates stored in the database will have a UTC 0 sufix, however they're in America/Sao_Paulo timezone. Example:
    - If the date stored in your Data warehouse is '2020-12-01T12:10:03 UTC 00:00', it actually represents:  '2020-12-01T12:10:03 UTC -03:00' (or -02:00 depending on day light saving time).

[**invoices**](https://ajuda.bling.com.br/hc/pt-br/articles/360046379394-GET-notasfiscais)
- Endpoint: https://bling.com.br/Api/v2/notasfiscais/page=[page number]/json
- Primary Key: id
- Replication strategy:
    - Incremental, filtering by start and end date
    - Do a request for each page until empty page is found
    - **IMPORTANT NOTE**: As the API only allows to filter invoices by creation date, the end user must develop its own strategy to ensure that any updates of the resources will be properly replicated according to the applicable business rules (for example, an invoice can only be updated within 24 hours of its creation).
- Transformation:
    - **IMPORTANT NOTE**: As the API returns dates as strings at America/Sao_Paulo timezone without timezone information, and Singer.io has it's own way of handling date strings, the code will append the UTC 0 tz info without changing the date string. So all dates stored in the database will have a UTC 0 sufix, however they're in America/Sao_Paulo timezone. Example:
    - If the date stored in your Data warehouse is '2020-12-01T12:10:03 UTC 00:00', it actually represents:  '2020-12-01T12:10:03 UTC -03:00' (or -02:00 depending on day light saving time).
- Filter:
    - By default, the API returns only Sales ("regular") invoices that were not canceled. Additional filtering to extract other kinds of invoices is supported by this tap by adding the 'invoice_extra_filters' key to the **config.json** file.
    - The extra filter parameters are given in a string separated by semicolon (following the api [documentation](https://ajuda.bling.com.br/hc/pt-br/articles/360046379394-GET-notasfiscais)) as shown in the example below:
    ```
  {
    'api_url': 'https://bling.com.br/Api',
    'api_token': '<72 char hexcode>',
    'start_date': '2020-12-01T00:00:00.000000Z'
    'invoice_extra_filters': 'tipo[E];situacao[3]'
  }
  ```

---

Copyright &copy; 2020 Stitch
